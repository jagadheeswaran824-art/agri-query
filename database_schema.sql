-- KrishiSahay Database Schema
-- Advanced Agricultural Intelligence Database System

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =====================================================
-- CORE ENTITIES
-- =====================================================

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) DEFAULT 'farmer' CHECK (user_type IN ('farmer', 'expert', 'admin', 'researcher')),
    profile_data JSONB DEFAULT '{}',
    location GEOGRAPHY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    verification_status VARCHAR(20) DEFAULT 'pending',
    preferences JSONB DEFAULT '{}'
);

-- Farmer Profiles (Extended user information)
CREATE TABLE farmer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    farm_name VARCHAR(255),
    farm_size_acres DECIMAL(10,2),
    primary_crops TEXT[],
    farming_experience_years INTEGER,
    education_level VARCHAR(50),
    annual_income_range VARCHAR(50),
    land_ownership VARCHAR(50) CHECK (land_ownership IN ('owned', 'leased', 'shared', 'cooperative')),
    irrigation_type VARCHAR(50),
    farming_methods TEXT[],
    certifications TEXT[],
    government_schemes TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- AGRICULTURAL KNOWLEDGE BASE
-- =====================================================

-- Crops Master Data
CREATE TABLE crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    growing_season VARCHAR(50),
    climate_requirements JSONB,
    soil_requirements JSONB,
    water_requirements JSONB,
    growth_stages JSONB,
    nutritional_needs JSONB,
    common_diseases TEXT[],
    common_pests TEXT[],
    companion_crops TEXT[],
    market_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Diseases Database
CREATE TABLE diseases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255),
    type VARCHAR(50) CHECK (type IN ('fungal', 'bacterial', 'viral', 'nematode', 'physiological')),
    affected_crops UUID[] REFERENCES crops(id),
    symptoms JSONB,
    causes JSONB,
    prevention_methods JSONB,
    treatment_options JSONB,
    severity_levels JSONB,
    environmental_factors JSONB,
    images TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pests Database
CREATE TABLE pests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255),
    type VARCHAR(50) CHECK (type IN ('insect', 'mite', 'nematode', 'rodent', 'bird', 'weed')),
    affected_crops UUID[] REFERENCES crops(id),
    life_cycle JSONB,
    damage_symptoms JSONB,
    identification_features JSONB,
    control_methods JSONB,
    biological_controls JSONB,
    chemical_controls JSONB,
    ipm_strategies JSONB,
    seasonal_occurrence JSONB,
    images TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fertilizers and Nutrients
CREATE TABLE fertilizers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('organic', 'inorganic', 'bio-fertilizer', 'micronutrient')),
    composition JSONB,
    npk_ratio VARCHAR(20),
    application_methods JSONB,
    dosage_recommendations JSONB,
    suitable_crops UUID[] REFERENCES crops(id),
    soil_compatibility JSONB,
    timing_guidelines JSONB,
    precautions TEXT[],
    cost_information JSONB,
    availability_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- QUERY AND RESPONSE SYSTEM
-- =====================================================

-- Query Sessions
CREATE TABLE query_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    location GEOGRAPHY(POINT, 4326),
    device_info JSONB,
    context_data JSONB,
    is_active BOOLEAN DEFAULT true
);

-- User Queries
CREATE TABLE user_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES query_sessions(id),
    user_id UUID REFERENCES users(id),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50),
    intent VARCHAR(100),
    entities JSONB,
    context JSONB,
    language VARCHAR(10) DEFAULT 'en',
    input_method VARCHAR(20) DEFAULT 'text' CHECK (input_method IN ('text', 'voice', 'image')),
    attachments TEXT[],
    location GEOGRAPHY(POINT, 4326),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_time_ms INTEGER,
    confidence_score DECIMAL(3,2)
);

-- AI Responses
CREATE TABLE ai_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID REFERENCES user_queries(id) ON DELETE CASCADE,
    response_text TEXT NOT NULL,
    response_type VARCHAR(50) DEFAULT 'text',
    sources JSONB,
    confidence_score DECIMAL(3,2),
    processing_method VARCHAR(50) CHECK (processing_method IN ('faiss_only', 'llm_only', 'hybrid')),
    model_version VARCHAR(50),
    generation_time_ms INTEGER,
    faiss_results JSONB,
    llm_results JSONB,
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Feedback
CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID REFERENCES user_queries(id),
    response_id UUID REFERENCES ai_responses(id),
    user_id UUID REFERENCES users(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_type VARCHAR(50) CHECK (feedback_type IN ('helpful', 'not_helpful', 'incorrect', 'incomplete', 'excellent')),
    comments TEXT,
    improvement_suggestions TEXT,
    follow_up_needed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- KNOWLEDGE MANAGEMENT
-- =====================================================

-- Expert Knowledge Base
CREATE TABLE expert_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    expert_id UUID REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    crops_applicable UUID[] REFERENCES crops(id),
    region_applicable VARCHAR(100),
    season_applicable VARCHAR(50),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    verification_status VARCHAR(20) DEFAULT 'pending',
    verified_by UUID REFERENCES users(id),
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Government Schemes
CREATE TABLE government_schemes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scheme_name VARCHAR(255) NOT NULL,
    scheme_code VARCHAR(50) UNIQUE,
    description TEXT,
    eligibility_criteria JSONB,
    benefits JSONB,
    application_process JSONB,
    required_documents TEXT[],
    application_deadlines JSONB,
    contact_information JSONB,
    states_applicable TEXT[],
    crops_applicable UUID[] REFERENCES crops(id),
    target_beneficiaries TEXT[],
    budget_allocation DECIMAL(15,2),
    launch_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    website_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ANALYTICS AND MONITORING
-- =====================================================

-- Query Analytics
CREATE TABLE query_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    hour INTEGER CHECK (hour BETWEEN 0 AND 23),
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    failed_queries INTEGER DEFAULT 0,
    avg_response_time_ms DECIMAL(10,2),
    avg_confidence_score DECIMAL(3,2),
    top_categories JSONB,
    top_crops JSONB,
    user_satisfaction DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System Performance Metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- User Behavior Analytics
CREATE TABLE user_behavior (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    session_id UUID REFERENCES query_sessions(id),
    action_type VARCHAR(50),
    action_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    page_url VARCHAR(500),
    user_agent TEXT,
    ip_address INET
);

-- =====================================================
-- VECTOR EMBEDDINGS AND SEARCH
-- =====================================================

-- Vector Embeddings Storage
CREATE TABLE vector_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    embedding_model VARCHAR(100),
    embedding_vector DECIMAL(8,6)[],
    dimension INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Search Index Metadata
CREATE TABLE search_indices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    index_name VARCHAR(100) UNIQUE NOT NULL,
    index_type VARCHAR(50) CHECK (index_type IN ('faiss', 'elasticsearch', 'postgresql')),
    content_types TEXT[],
    total_documents INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    index_config JSONB,
    performance_stats JSONB
);

-- =====================================================
-- REAL-TIME FEATURES
-- =====================================================

-- Weather Data
CREATE TABLE weather_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    date DATE NOT NULL,
    temperature_min DECIMAL(5,2),
    temperature_max DECIMAL(5,2),
    humidity DECIMAL(5,2),
    rainfall DECIMAL(8,2),
    wind_speed DECIMAL(5,2),
    wind_direction INTEGER,
    pressure DECIMAL(8,2),
    uv_index DECIMAL(3,1),
    weather_condition VARCHAR(100),
    forecast_data JSONB,
    data_source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market Prices
CREATE TABLE market_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_id UUID REFERENCES crops(id),
    market_name VARCHAR(255),
    location GEOGRAPHY(POINT, 4326),
    price_per_unit DECIMAL(10,2),
    unit VARCHAR(20),
    quality_grade VARCHAR(50),
    date DATE NOT NULL,
    price_trend VARCHAR(20) CHECK (price_trend IN ('rising', 'falling', 'stable')),
    demand_level VARCHAR(20) CHECK (demand_level IN ('high', 'medium', 'low')),
    supply_level VARCHAR(20) CHECK (supply_level IN ('high', 'medium', 'low')),
    data_source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts and Notifications
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    alert_type VARCHAR(50) CHECK (alert_type IN ('weather', 'pest', 'disease', 'market', 'scheme', 'general')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    location GEOGRAPHY(POINT, 4326),
    crops_affected UUID[] REFERENCES crops(id),
    expiry_date TIMESTAMP WITH TIME ZONE,
    is_read BOOLEAN DEFAULT false,
    action_required BOOLEAN DEFAULT false,
    action_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_location ON users USING GIST(location);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;

-- Query indexes
CREATE INDEX idx_queries_user_id ON user_queries(user_id);
CREATE INDEX idx_queries_timestamp ON user_queries(timestamp DESC);
CREATE INDEX idx_queries_intent ON user_queries(intent);
CREATE INDEX idx_queries_location ON user_queries USING GIST(location);
CREATE INDEX idx_queries_text_search ON user_queries USING GIN(to_tsvector('english', query_text));

-- Response indexes
CREATE INDEX idx_responses_query_id ON ai_responses(query_id);
CREATE INDEX idx_responses_confidence ON ai_responses(confidence_score DESC);
CREATE INDEX idx_responses_method ON ai_responses(processing_method);

-- Knowledge base indexes
CREATE INDEX idx_crops_name ON crops USING GIN(name gin_trgm_ops);
CREATE INDEX idx_crops_category ON crops(category);
CREATE INDEX idx_diseases_name ON diseases USING GIN(name gin_trgm_ops);
CREATE INDEX idx_pests_name ON pests USING GIN(name gin_trgm_ops);

-- Analytics indexes
CREATE INDEX idx_analytics_date ON query_analytics(date DESC);
CREATE INDEX idx_performance_timestamp ON performance_metrics(timestamp DESC);
CREATE INDEX idx_behavior_user_session ON user_behavior(user_id, session_id);

-- Vector embeddings indexes
CREATE INDEX idx_embeddings_content ON vector_embeddings(content_id, content_type);
CREATE INDEX idx_embeddings_model ON vector_embeddings(embedding_model);

-- Weather and market indexes
CREATE INDEX idx_weather_location_date ON weather_data USING GIST(location, date);
CREATE INDEX idx_market_crop_date ON market_prices(crop_id, date DESC);
CREATE INDEX idx_alerts_user_unread ON alerts(user_id) WHERE is_read = false;

-- =====================================================
-- TRIGGERS AND FUNCTIONS
-- =====================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_farmer_profiles_updated_at BEFORE UPDATE ON farmer_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_crops_updated_at BEFORE UPDATE ON crops FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_diseases_updated_at BEFORE UPDATE ON diseases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pests_updated_at BEFORE UPDATE ON pests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fertilizers_updated_at BEFORE UPDATE ON fertilizers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Query analytics trigger
CREATE OR REPLACE FUNCTION update_query_analytics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO query_analytics (date, hour, total_queries)
    VALUES (CURRENT_DATE, EXTRACT(HOUR FROM NOW()), 1)
    ON CONFLICT (date, hour) 
    DO UPDATE SET total_queries = query_analytics.total_queries + 1;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_query_analytics AFTER INSERT ON user_queries FOR EACH ROW EXECUTE FUNCTION update_query_analytics();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- User dashboard view
CREATE VIEW user_dashboard AS
SELECT 
    u.id,
    u.username,
    u.email,
    fp.farm_name,
    fp.farm_size_acres,
    fp.primary_crops,
    COUNT(uq.id) as total_queries,
    AVG(ar.confidence_score) as avg_confidence,
    MAX(uq.timestamp) as last_query_time
FROM users u
LEFT JOIN farmer_profiles fp ON u.id = fp.user_id
LEFT JOIN user_queries uq ON u.id = uq.user_id
LEFT JOIN ai_responses ar ON uq.id = ar.query_id
WHERE u.is_active = true
GROUP BY u.id, u.username, u.email, fp.farm_name, fp.farm_size_acres, fp.primary_crops;

-- Popular queries view
CREATE VIEW popular_queries AS
SELECT 
    query_text,
    COUNT(*) as frequency,
    AVG(ar.confidence_score) as avg_confidence,
    AVG(uf.rating) as avg_rating
FROM user_queries uq
LEFT JOIN ai_responses ar ON uq.id = ar.query_id
LEFT JOIN user_feedback uf ON ar.id = uf.response_id
WHERE uq.timestamp >= NOW() - INTERVAL '30 days'
GROUP BY query_text
ORDER BY frequency DESC
LIMIT 100;

-- System health view
CREATE VIEW system_health AS
SELECT 
    DATE(timestamp) as date,
    AVG(CASE WHEN metric_name = 'response_time_ms' THEN metric_value END) as avg_response_time,
    AVG(CASE WHEN metric_name = 'cpu_usage' THEN metric_value END) as avg_cpu_usage,
    AVG(CASE WHEN metric_name = 'memory_usage' THEN metric_value END) as avg_memory_usage,
    COUNT(CASE WHEN metric_name = 'error_count' THEN 1 END) as total_errors
FROM performance_metrics
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;