"""
KrishiSahay Database Manager
Advanced database operations and management system
"""

import asyncio
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import redis
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "krishisahay"
    username: str = "postgres"
    password: str = "password"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

class DatabaseManager:
    """Advanced database manager for KrishiSahay"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = None
        self.redis_client = None
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup database connections"""
        try:
            # Redis connection
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=True
            )
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
    
    async def initialize_pool(self):
        """Initialize async connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ PostgreSQL connection pool established")
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        async with self.pool.acquire() as connection:
            yield connection

class UserManager:
    """User management operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO users (id, username, email, phone, password_hash, 
                                 user_type, profile_data, location)
                VALUES ($1, $2, $3, $4, $5, $6, $7, ST_Point($8, $9))
            """, 
                user_id,
                user_data['username'],
                user_data['email'],
                user_data.get('phone'),
                user_data['password_hash'],
                user_data.get('user_type', 'farmer'),
                json.dumps(user_data.get('profile_data', {})),
                user_data.get('longitude', 0),
                user_data.get('latitude', 0)
            )
        
        # Cache user data
        self.db.redis_client.setex(
            f"user:{user_id}", 
            3600, 
            json.dumps(user_data)
        )
        
        logger.info(f"✅ User created: {user_id}")
        return user_id
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID with caching"""
        
        # Try cache first
        cached_user = self.db.redis_client.get(f"user:{user_id}")
        if cached_user:
            return json.loads(cached_user)
        
        # Query database
        async with self.db.get_connection() as conn:
            row = await conn.fetchrow("""
                SELECT u.*, fp.farm_name, fp.farm_size_acres, fp.primary_crops
                FROM users u
                LEFT JOIN farmer_profiles fp ON u.id = fp.user_id
                WHERE u.id = $1 AND u.is_active = true
            """, user_id)
            
            if row:
                user_data = dict(row)
                # Cache for 1 hour
                self.db.redis_client.setex(
                    f"user:{user_id}", 
                    3600, 
                    json.dumps(user_data, default=str)
                )
                return user_data
        
        return None
    
    async def update_user_activity(self, user_id: str):
        """Update user last activity"""
        async with self.db.get_connection() as conn:
            await conn.execute("""
                UPDATE users SET last_active = NOW() WHERE id = $1
            """, user_id)
        
        # Invalidate cache
        self.db.redis_client.delete(f"user:{user_id}")

class QueryManager:
    """Query and response management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def create_query_session(self, user_id: str, context: Dict[str, Any]) -> str:
        """Create a new query session"""
        session_id = str(uuid.uuid4())
        session_token = str(uuid.uuid4())
        
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO query_sessions (id, user_id, session_token, 
                                          location, device_info, context_data)
                VALUES ($1, $2, $3, ST_Point($4, $5), $6, $7)
            """,
                session_id,
                user_id,
                session_token,
                context.get('longitude', 0),
                context.get('latitude', 0),
                json.dumps(context.get('device_info', {})),
                json.dumps(context.get('context_data', {}))
            )
        
        return session_id
    
    async def save_query(self, query_data: Dict[str, Any]) -> str:
        """Save user query"""
        query_id = str(uuid.uuid4())
        
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO user_queries (id, session_id, user_id, query_text,
                                        query_type, intent, entities, context,
                                        language, input_method, location,
                                        processing_time_ms, confidence_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 
                        ST_Point($11, $12), $13, $14)
            """,
                query_id,
                query_data.get('session_id'),
                query_data.get('user_id'),
                query_data['query_text'],
                query_data.get('query_type'),
                query_data.get('intent'),
                json.dumps(query_data.get('entities', {})),
                json.dumps(query_data.get('context', {})),
                query_data.get('language', 'en'),
                query_data.get('input_method', 'text'),
                query_data.get('longitude', 0),
                query_data.get('latitude', 0),
                query_data.get('processing_time_ms'),
                query_data.get('confidence_score')
            )
        
        return query_id
    
    async def save_response(self, response_data: Dict[str, Any]) -> str:
        """Save AI response"""
        response_id = str(uuid.uuid4())
        
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO ai_responses (id, query_id, response_text, response_type,
                                        sources, confidence_score, processing_method,
                                        model_version, generation_time_ms, faiss_results,
                                        llm_results, quality_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
                response_id,
                response_data['query_id'],
                response_data['response_text'],
                response_data.get('response_type', 'text'),
                json.dumps(response_data.get('sources', [])),
                response_data.get('confidence_score'),
                response_data.get('processing_method'),
                response_data.get('model_version'),
                response_data.get('generation_time_ms'),
                json.dumps(response_data.get('faiss_results', {})),
                json.dumps(response_data.get('llm_results', {})),
                response_data.get('quality_score')
            )
        
        return response_id
    
    async def get_query_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user query history"""
        
        # Try cache first
        cache_key = f"history:{user_id}:{limit}"
        cached_history = self.db.redis_client.get(cache_key)
        if cached_history:
            return json.loads(cached_history)
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT uq.*, ar.response_text, ar.confidence_score as response_confidence
                FROM user_queries uq
                LEFT JOIN ai_responses ar ON uq.id = ar.query_id
                WHERE uq.user_id = $1
                ORDER BY uq.timestamp DESC
                LIMIT $2
            """, user_id, limit)
            
            history = [dict(row) for row in rows]
            
            # Cache for 10 minutes
            self.db.redis_client.setex(
                cache_key, 
                600, 
                json.dumps(history, default=str)
            )
            
            return history

class KnowledgeManager:
    """Agricultural knowledge management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def add_crop(self, crop_data: Dict[str, Any]) -> str:
        """Add new crop to database"""
        crop_id = str(uuid.uuid4())
        
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO crops (id, name, scientific_name, category, subcategory,
                                 growing_season, climate_requirements, soil_requirements,
                                 water_requirements, growth_stages, nutritional_needs,
                                 common_diseases, common_pests, companion_crops, market_info)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """,
                crop_id,
                crop_data['name'],
                crop_data.get('scientific_name'),
                crop_data.get('category'),
                crop_data.get('subcategory'),
                crop_data.get('growing_season'),
                json.dumps(crop_data.get('climate_requirements', {})),
                json.dumps(crop_data.get('soil_requirements', {})),
                json.dumps(crop_data.get('water_requirements', {})),
                json.dumps(crop_data.get('growth_stages', {})),
                json.dumps(crop_data.get('nutritional_needs', {})),
                crop_data.get('common_diseases', []),
                crop_data.get('common_pests', []),
                crop_data.get('companion_crops', []),
                json.dumps(crop_data.get('market_info', {}))
            )
        
        return crop_id
    
    async def search_crops(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search crops by name"""
        async with self.db.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM crops
                WHERE name ILIKE $1 OR scientific_name ILIKE $1
                ORDER BY similarity(name, $2) DESC
                LIMIT $3
            """, f"%{search_term}%", search_term, limit)
            
            return [dict(row) for row in rows]
    
    async def get_crop_diseases(self, crop_id: str) -> List[Dict[str, Any]]:
        """Get diseases affecting a specific crop"""
        async with self.db.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM diseases
                WHERE $1 = ANY(affected_crops)
                ORDER BY name
            """, crop_id)
            
            return [dict(row) for row in rows]
    
    async def add_expert_knowledge(self, knowledge_data: Dict[str, Any]) -> str:
        """Add expert knowledge"""
        knowledge_id = str(uuid.uuid4())
        
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO expert_knowledge (id, expert_id, title, content, category,
                                            tags, crops_applicable, region_applicable,
                                            season_applicable, difficulty_level)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
                knowledge_id,
                knowledge_data['expert_id'],
                knowledge_data['title'],
                knowledge_data['content'],
                knowledge_data.get('category'),
                knowledge_data.get('tags', []),
                knowledge_data.get('crops_applicable', []),
                knowledge_data.get('region_applicable'),
                knowledge_data.get('season_applicable'),
                knowledge_data.get('difficulty_level', 'intermediate')
            )
        
        return knowledge_id

class AnalyticsManager:
    """Analytics and monitoring"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def record_performance_metric(self, metric_name: str, value: float, 
                                      unit: str = None, metadata: Dict = None):
        """Record performance metric"""
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO performance_metrics (metric_name, metric_value, 
                                               metric_unit, metadata)
                VALUES ($1, $2, $3, $4)
            """, metric_name, value, unit, json.dumps(metadata or {}))
    
    async def get_query_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get query analytics for specified days"""
        async with self.db.get_connection() as conn:
            # Total queries
            total_queries = await conn.fetchval("""
                SELECT COUNT(*) FROM user_queries
                WHERE timestamp >= NOW() - INTERVAL '%s days'
            """, days)
            
            # Average response time
            avg_response_time = await conn.fetchval("""
                SELECT AVG(generation_time_ms) FROM ai_responses ar
                JOIN user_queries uq ON ar.query_id = uq.id
                WHERE uq.timestamp >= NOW() - INTERVAL '%s days'
            """, days)
            
            # Top categories
            top_categories = await conn.fetch("""
                SELECT query_type, COUNT(*) as count
                FROM user_queries
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                  AND query_type IS NOT NULL
                GROUP BY query_type
                ORDER BY count DESC
                LIMIT 10
            """, days)
            
            # User satisfaction
            avg_rating = await conn.fetchval("""
                SELECT AVG(rating) FROM user_feedback uf
                JOIN ai_responses ar ON uf.response_id = ar.id
                JOIN user_queries uq ON ar.query_id = uq.id
                WHERE uq.timestamp >= NOW() - INTERVAL '%s days'
            """, days)
            
            return {
                'total_queries': total_queries,
                'avg_response_time_ms': float(avg_response_time or 0),
                'top_categories': [dict(row) for row in top_categories],
                'avg_user_rating': float(avg_rating or 0),
                'period_days': days
            }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        async with self.db.get_connection() as conn:
            # Recent errors
            error_count = await conn.fetchval("""
                SELECT COUNT(*) FROM performance_metrics
                WHERE metric_name = 'error_count'
                  AND timestamp >= NOW() - INTERVAL '1 hour'
            """)
            
            # Average response time (last hour)
            recent_response_time = await conn.fetchval("""
                SELECT AVG(metric_value) FROM performance_metrics
                WHERE metric_name = 'response_time_ms'
                  AND timestamp >= NOW() - INTERVAL '1 hour'
            """)
            
            # Active users (last 24 hours)
            active_users = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id) FROM user_queries
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
            """)
            
            return {
                'error_count_last_hour': error_count or 0,
                'avg_response_time_ms': float(recent_response_time or 0),
                'active_users_24h': active_users or 0,
                'status': 'healthy' if (error_count or 0) < 10 else 'degraded'
            }

class VectorManager:
    """Vector embeddings management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def store_embedding(self, content_id: str, content_type: str,
                            embedding: np.ndarray, model: str) -> str:
        """Store vector embedding"""
        embedding_id = str(uuid.uuid4())
        
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO vector_embeddings (id, content_id, content_type,
                                             embedding_model, embedding_vector, dimension)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                embedding_id,
                content_id,
                content_type,
                model,
                embedding.tolist(),
                len(embedding)
            )
        
        return embedding_id
    
    async def get_embeddings_by_type(self, content_type: str) -> List[Dict[str, Any]]:
        """Get embeddings by content type"""
        async with self.db.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM vector_embeddings
                WHERE content_type = $1
                ORDER BY created_at DESC
            """, content_type)
            
            return [dict(row) for row in rows]

# Usage example and testing
async def main():
    """Example usage of the database manager"""
    
    # Initialize database manager
    config = DatabaseConfig()
    db_manager = DatabaseManager(config)
    await db_manager.initialize_pool()
    
    # Initialize managers
    user_manager = UserManager(db_manager)
    query_manager = QueryManager(db_manager)
    knowledge_manager = KnowledgeManager(db_manager)
    analytics_manager = AnalyticsManager(db_manager)
    
    # Example operations
    try:
        # Create a test user
        user_data = {
            'username': 'test_farmer',
            'email': 'farmer@example.com',
            'password_hash': 'hashed_password',
            'user_type': 'farmer',
            'latitude': 28.6139,
            'longitude': 77.2090
        }
        
        user_id = await user_manager.create_user(user_data)
        print(f"✅ Created user: {user_id}")
        
        # Create query session
        session_context = {
            'device_info': {'platform': 'web', 'browser': 'chrome'},
            'latitude': 28.6139,
            'longitude': 77.2090
        }
        
        session_id = await query_manager.create_query_session(user_id, session_context)
        print(f"✅ Created session: {session_id}")
        
        # Save a query
        query_data = {
            'session_id': session_id,
            'user_id': user_id,
            'query_text': 'How to control aphids in mustard?',
            'query_type': 'pest_control',
            'intent': 'get_treatment',
            'confidence_score': 0.95
        }
        
        query_id = await query_manager.save_query(query_data)
        print(f"✅ Saved query: {query_id}")
        
        # Get analytics
        analytics = await analytics_manager.get_query_analytics(7)
        print(f"✅ Analytics: {analytics}")
        
        # Get system health
        health = await analytics_manager.get_system_health()
        print(f"✅ System health: {health}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
    
    finally:
        if db_manager.pool:
            await db_manager.pool.close()

if __name__ == "__main__":
    asyncio.run(main())