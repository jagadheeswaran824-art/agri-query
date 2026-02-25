# 🗄️ KrishiSahay Database Design

## Database Architecture Overview

KrishiSahay employs a sophisticated multi-database architecture combining relational, vector, and cache databases for optimal performance and scalability.

```
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE ECOSYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL      │  Redis Cache     │  FAISS Vector DB     │
│  • Core Data     │  • Session Data  │  • Embeddings        │
│  • User Profiles │  • Query Cache   │  • Semantic Search   │
│  • Analytics     │  • Real-time     │  • Similarity Match  │
│  • Transactions  │  • Performance   │  • Fast Retrieval    │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ Unique Database Features

### 1. **Multi-Dimensional Data Model**
- **Geospatial Support**: PostGIS for location-based queries
- **JSONB Storage**: Flexible schema for agricultural data
- **Vector Embeddings**: AI-powered semantic search
- **Time-Series Data**: Weather and market price tracking

### 2. **Advanced Indexing Strategy**
- **GIN Indexes**: Full-text search on agricultural content
- **GIST Indexes**: Geospatial and range queries
- **Trigram Indexes**: Fuzzy text matching for crop names
- **Composite Indexes**: Multi-column query optimization

### 3. **Intelligent Caching System**
- **Query Result Cache**: Redis-based response caching
- **User Session Cache**: Fast session management
- **Embedding Cache**: Pre-computed vector storage
- **Analytics Cache**: Real-time dashboard data

## 📊 Core Database Tables

### User Management
```sql
users                    -- Core user information
├── farmer_profiles      -- Extended farmer data
├── query_sessions       -- User interaction sessions
└── user_behavior        -- Analytics and tracking
```

### Agricultural Knowledge
```sql
crops                    -- Master crop database
├── diseases            -- Plant disease information
├── pests              -- Pest identification & control
├── fertilizers        -- Nutrient management
└── expert_knowledge   -- Curated expert content
```

### AI & Query System
```sql
user_queries            -- All user questions
├── ai_responses       -- AI-generated answers
├── user_feedback      -- Quality ratings
└── vector_embeddings  -- Semantic search vectors
```

### Analytics & Monitoring
```sql
query_analytics         -- Usage statistics
├── performance_metrics -- System performance
├── system_health      -- Health monitoring
└── search_indices     -- Index management
```

## 🎯 Unique Database Capabilities

### 1. **Semantic Search Integration**
```sql
-- Vector similarity search with metadata
SELECT 
    c.name,
    c.category,
    ve.embedding_vector <-> $1 as similarity_score
FROM crops c
JOIN vector_embeddings ve ON c.id = ve.content_id
WHERE ve.content_type = 'crop'
ORDER BY similarity_score
LIMIT 10;
```

### 2. **Geospatial Agricultural Queries**
```sql
-- Find nearby farmers growing similar crops
SELECT 
    u.username,
    fp.primary_crops,
    ST_Distance(u.location, ST_Point($1, $2)) as distance_km
FROM users u
JOIN farmer_profiles fp ON u.id = fp.user_id
WHERE ST_DWithin(u.location, ST_Point($1, $2), 50000)  -- 50km radius
  AND fp.primary_crops && $3  -- Array overlap
ORDER BY distance_km;
```

### 3. **Time-Series Analytics**
```sql
-- Query performance trends
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(confidence_score) as avg_confidence,
    COUNT(*) as query_count,
    AVG(processing_time_ms) as avg_response_time
FROM user_queries uq
JOIN ai_responses ar ON uq.id = ar.query_id
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

### 4. **Dynamic Content Recommendations**
```sql
-- Personalized crop recommendations
WITH user_context AS (
    SELECT 
        u.location,
        fp.primary_crops,
        fp.farm_size_acres,
        fp.farming_experience_years
    FROM users u
    JOIN farmer_profiles fp ON u.id = fp.user_id
    WHERE u.id = $1
),
seasonal_crops AS (
    SELECT c.*
    FROM crops c
    WHERE c.growing_season = $2  -- Current season
      AND c.climate_requirements->>'temperature_range' ~ $3  -- Climate match
)
SELECT 
    sc.*,
    CASE 
        WHEN sc.name = ANY(uc.primary_crops) THEN 'currently_growing'
        WHEN sc.companion_crops && uc.primary_crops THEN 'companion_crop'
        ELSE 'new_opportunity'
    END as recommendation_type
FROM seasonal_crops sc, user_context uc
ORDER BY 
    CASE recommendation_type
        WHEN 'companion_crop' THEN 1
        WHEN 'new_opportunity' THEN 2
        WHEN 'currently_growing' THEN 3
    END;
```

## 🔄 Real-Time Data Processing

### 1. **Live Weather Integration**
```sql
-- Weather-based crop alerts
INSERT INTO alerts (user_id, alert_type, title, message, severity, location)
SELECT 
    u.id,
    'weather',
    'Heavy Rainfall Alert',
    'Protect your ' || array_to_string(fp.primary_crops, ', ') || ' crops from waterlogging',
    'high',
    u.location
FROM users u
JOIN farmer_profiles fp ON u.id = fp.user_id
JOIN weather_data wd ON ST_DWithin(u.location, wd.location, 10000)
WHERE wd.rainfall > 50  -- Heavy rain threshold
  AND wd.date = CURRENT_DATE
  AND NOT EXISTS (
      SELECT 1 FROM alerts a 
      WHERE a.user_id = u.id 
        AND a.alert_type = 'weather' 
        AND a.created_at > NOW() - INTERVAL '6 hours'
  );
```

### 2. **Market Price Tracking**
```sql
-- Price trend analysis
WITH price_trends AS (
    SELECT 
        crop_id,
        date,
        price_per_unit,
        LAG(price_per_unit) OVER (PARTITION BY crop_id ORDER BY date) as prev_price,
        AVG(price_per_unit) OVER (
            PARTITION BY crop_id 
            ORDER BY date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as moving_avg
    FROM market_prices
    WHERE date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT 
    c.name,
    pt.price_per_unit as current_price,
    pt.moving_avg,
    CASE 
        WHEN pt.price_per_unit > pt.prev_price * 1.05 THEN 'rising'
        WHEN pt.price_per_unit < pt.prev_price * 0.95 THEN 'falling'
        ELSE 'stable'
    END as trend
FROM price_trends pt
JOIN crops c ON pt.crop_id = c.id
WHERE pt.date = CURRENT_DATE;
```

## 🚀 Performance Optimizations

### 1. **Partitioning Strategy**
```sql
-- Partition large tables by date
CREATE TABLE user_queries_y2024m01 PARTITION OF user_queries
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE user_queries_y2024m02 PARTITION OF user_queries
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 2. **Materialized Views**
```sql
-- Pre-computed analytics
CREATE MATERIALIZED VIEW daily_query_stats AS
SELECT 
    DATE(timestamp) as query_date,
    COUNT(*) as total_queries,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(confidence_score) as avg_confidence,
    array_agg(DISTINCT intent) as popular_intents
FROM user_queries uq
JOIN ai_responses ar ON uq.id = ar.query_id
GROUP BY DATE(timestamp);

-- Refresh every hour
CREATE OR REPLACE FUNCTION refresh_daily_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_query_stats;
END;
$$ LANGUAGE plpgsql;

SELECT cron.schedule('refresh-stats', '0 * * * *', 'SELECT refresh_daily_stats();');
```

### 3. **Connection Pooling**
```python
# Advanced connection pool configuration
POOL_CONFIG = {
    'min_size': 5,
    'max_size': 20,
    'max_queries': 50000,
    'max_inactive_connection_lifetime': 300,
    'command_timeout': 60,
    'server_settings': {
        'application_name': 'krishisahay',
        'jit': 'off'  # Disable JIT for faster simple queries
    }
}
```

## 🔒 Security & Privacy

### 1. **Row-Level Security**
```sql
-- Users can only see their own data
ALTER TABLE user_queries ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_queries_policy ON user_queries
FOR ALL TO authenticated_users
USING (user_id = current_setting('app.current_user_id')::uuid);
```

### 2. **Data Encryption**
```sql
-- Encrypt sensitive fields
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt phone numbers
ALTER TABLE users ADD COLUMN phone_encrypted bytea;
UPDATE users SET phone_encrypted = pgp_sym_encrypt(phone, 'encryption_key');
```

### 3. **Audit Logging**
```sql
-- Track all data changes
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100),
    operation VARCHAR(10),
    old_values JSONB,
    new_values JSONB,
    user_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, old_values, new_values, user_id)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
        current_setting('app.current_user_id', true)::uuid
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

## 📈 Scalability Features

### 1. **Read Replicas**
```sql
-- Configure streaming replication
-- On primary server
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET wal_keep_segments = 64;

-- On replica server
standby_mode = 'on'
primary_conninfo = 'host=primary_server port=5432 user=replicator'
```

### 2. **Horizontal Sharding**
```python
# Shard user data by geographic region
SHARD_CONFIG = {
    'north_india': {
        'host': 'db-north.krishisahay.com',
        'regions': ['punjab', 'haryana', 'uttar_pradesh']
    },
    'south_india': {
        'host': 'db-south.krishisahay.com', 
        'regions': ['tamil_nadu', 'karnataka', 'andhra_pradesh']
    }
}

def get_shard_for_user(user_location):
    # Route user to appropriate shard based on location
    return determine_shard(user_location)
```

This comprehensive database design ensures KrishiSahay can handle millions of farmers with fast, intelligent, and scalable agricultural assistance.