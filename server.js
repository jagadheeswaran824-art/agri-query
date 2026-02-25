const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
const redis = require('redis');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const winston = require('winston');
const cron = require('node-cron');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

// Import AI Models
const AdvancedGraniteAI = require('./ai-models/advanced-granite');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    },
    transports: ['websocket', 'polling']
});

const PORT = process.env.PORT || 3000;

// Configure Winston Logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    defaultMeta: { service: 'krishisahay-api' },
    transports: [
        new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/combined.log' }),
        new winston.transports.Console({
            format: winston.format.simple()
        })
    ]
});

// Redis Client Setup
let redisClient;
try {
    redisClient = redis.createClient({
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379,
        password: process.env.REDIS_PASSWORD || undefined
    });
    
    redisClient.on('error', (err) => {
        logger.error('Redis Client Error:', err);
    });
    
    redisClient.on('connect', () => {
        logger.info('✅ Connected to Redis');
    });
    
    redisClient.connect();
} catch (error) {
    logger.warn('Redis not available, using in-memory storage');
    redisClient = null;
}

// Rate Limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later.'
});

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));
app.use(limiter);
app.use(express.static('public'));

// Initialize AI Model
const graniteAI = new AdvancedGraniteAI({
    apiKey: process.env.WATSONX_API_KEY,
    projectId: process.env.WATSONX_PROJECT_ID,
    region: process.env.WATSONX_REGION || 'us-south'
});

// In-memory storage for sessions (fallback)
const activeSessions = new Map();
const chatHistory = new Map();
const userAnalytics = new Map();

// Enhanced Agricultural Knowledge Base with AI Integration
const agricultureKnowledge = {
    'aphids': {
        crops: ['mustard', 'wheat', 'cotton'],
        solution: 'Spray neem oil solution (5ml per liter) or use imidacloprid 17.8% SL @ 0.5ml/liter. Apply during early morning or evening.',
        severity: 'medium',
        category: 'pest',
        symptoms: ['curled leaves', 'sticky honeydew', 'yellowing'],
        prevention: ['regular monitoring', 'beneficial insects', 'proper spacing']
    },
    'leaf spot': {
        crops: ['tomato', 'potato'],
        solution: 'Remove infected leaves. Spray mancozeb 75% WP @ 2g/liter or copper oxychloride @ 3g/liter at 10-day intervals.',
        severity: 'high',
        category: 'disease',
        symptoms: ['brown spots', 'leaf yellowing', 'defoliation'],
        prevention: ['crop rotation', 'proper drainage', 'resistant varieties']
    },
    'whitefly': {
        crops: ['cotton', 'tomato'],
        solution: 'Use thiamethoxam 25% WG @ 0.2g/liter or spray neem-based pesticides. Ensure coverage on leaf undersides.',
        severity: 'medium',
        category: 'pest',
        symptoms: ['white flying insects', 'yellowing leaves', 'sooty mold'],
        prevention: ['yellow sticky traps', 'reflective mulch', 'companion planting']
    },
    'fruit borer': {
        crops: ['brinjal', 'tomato'],
        solution: 'Install pheromone traps. Spray spinosad 45% SC @ 0.3ml/liter or use Bacillus thuringiensis.',
        severity: 'high',
        category: 'pest',
        symptoms: ['holes in fruits', 'larvae inside', 'fruit drop'],
        prevention: ['pheromone traps', 'clean cultivation', 'timely harvest']
    },
    'fertilizer': {
        crops: ['maize', 'wheat', 'rice'],
        solution: 'Apply DAP (Diammonium Phosphate) @ 50kg/acre during flowering. Supplement with potash for better yield.',
        severity: 'low',
        category: 'nutrition',
        symptoms: ['poor growth', 'yellowing', 'low yield'],
        prevention: ['soil testing', 'balanced nutrition', 'organic matter']
    },
    'blast disease': {
        crops: ['paddy', 'rice'],
        solution: 'Use tricyclazole 75% WP @ 0.6g/liter or carbendazim 50% WP @ 1g/liter. Maintain proper water management.',
        severity: 'high',
        category: 'disease',
        symptoms: ['diamond-shaped lesions', 'neck rot', 'panicle blast'],
        prevention: ['resistant varieties', 'balanced fertilization', 'water management']
    },
    'pm kisan': {
        crops: ['all'],
        solution: 'Visit PM Kisan portal (pmkisan.gov.in), register with Aadhaar, land records, and bank details. Contact local agriculture office for assistance.',
        severity: 'low',
        category: 'scheme',
        benefits: ['₹6000 per year', '3 installments', 'direct transfer'],
        eligibility: ['small farmers', 'marginal farmers', 'up to 2 hectares']
    },
    'neem oil': {
        crops: ['all'],
        solution: 'Mix 5ml neem oil per liter of water. Add 1ml liquid soap as emulsifier. Spray on affected plants every 7 days.',
        severity: 'low',
        category: 'organic',
        benefits: ['eco-friendly', 'systemic action', 'multiple pests'],
        application: ['early morning', 'evening', 'avoid flowering']
    },
    'blight': {
        crops: ['potato', 'tomato'],
        solution: 'Remove infected plants. Spray metalaxyl + mancozeb @ 2.5g/liter. Avoid overhead irrigation and ensure proper drainage.',
        severity: 'high',
        category: 'disease',
        symptoms: ['water-soaked lesions', 'rapid spread', 'plant death'],
        prevention: ['proper spacing', 'avoid overhead watering', 'resistant varieties']
    }
};

// Real-time Analytics Storage
const systemAnalytics = {
    totalQueries: 0,
    avgResponseTime: 0,
    activeUsers: 0,
    topQueries: [],
    errorRate: 0,
    lastUpdated: new Date()
};

// WebSocket Connection Management
io.on('connection', (socket) => {
    logger.info(`🔗 New client connected: ${socket.id}`);
    systemAnalytics.activeUsers++;
    
    // Join session
    socket.on('join-session', (sessionId) => {
        socket.sessionId = sessionId;
        socket.join(sessionId);
        
        // Store session info
        activeSessions.set(sessionId, {
            socketId: socket.id,
            joinTime: new Date(),
            lastActivity: new Date(),
            queryCount: 0
        });
        
        logger.info(`👤 Session joined: ${sessionId}`);
        
        // Send welcome message
        socket.emit('system-update', {
            type: 'welcome',
            message: 'Connected to KrishiSahay AI Server',
            capabilities: ['Real-time AI Chat', 'Voice Recognition', 'Image Analysis', 'Weather Integration']
        });
    });
    
    // Handle chat messages
    socket.on('chat-message', async (data) => {
        const startTime = Date.now();
        const { sessionId, message, context } = data;
        
        try {
            logger.info(`💬 Processing message from ${sessionId}: ${message.substring(0, 50)}...`);
            
            // Update session activity
            if (activeSessions.has(sessionId)) {
                const session = activeSessions.get(sessionId);
                session.lastActivity = new Date();
                session.queryCount++;
            }
            
            // Show typing indicator
            socket.emit('ai-typing', true);
            
            // Process with AI
            const response = await processAIQuery(message, context, sessionId);
            
            // Calculate response time
            const responseTime = Date.now() - startTime;
            systemAnalytics.avgResponseTime = Math.round(
                (systemAnalytics.avgResponseTime + responseTime) / 2
            );
            
            // Store in chat history
            const chatEntry = {
                sessionId,
                query: message,
                response: response.answer,
                timestamp: new Date(),
                responseTime,
                context
            };
            
            if (redisClient) {
                await redisClient.lpush(`chat:${sessionId}`, JSON.stringify(chatEntry));
                await redisClient.expire(`chat:${sessionId}`, 86400); // 24 hours
            } else {
                if (!chatHistory.has(sessionId)) {
                    chatHistory.set(sessionId, []);
                }
                chatHistory.get(sessionId).push(chatEntry);
            }
            
            // Stop typing indicator
            socket.emit('ai-typing', false);
            
            // Send response
            socket.emit('ai-response', {
                ...response,
                responseTime,
                timestamp: new Date().toISOString()
            });
            
            // Update analytics
            systemAnalytics.totalQueries++;
            updateTopQueries(message);
            
            logger.info(`✅ Response sent in ${responseTime}ms`);
            
        } catch (error) {
            logger.error('Error processing chat message:', error);
            socket.emit('ai-error', {
                message: 'Sorry, I encountered an error processing your request.',
                error: error.message
            });
            systemAnalytics.errorRate++;
        }
    });
    
    // Handle typing indicators
    socket.on('user-typing', (data) => {
        socket.to(data.sessionId).emit('user-typing', true);
    });
    
    // Handle feedback
    socket.on('feedback', async (data) => {
        logger.info(`📝 Feedback received: ${data.rating}/5`);
        
        if (redisClient) {
            await redisClient.lpush('feedback', JSON.stringify({
                ...data,
                timestamp: new Date()
            }));
        }
    });
    
    // Handle analytics requests
    socket.on('request-analytics', () => {
        socket.emit('analytics-update', {
            ...systemAnalytics,
            sessionStats: activeSessions.get(socket.sessionId)
        });
    });
    
    // Handle disconnection
    socket.on('disconnect', (reason) => {
        logger.info(`❌ Client disconnected: ${socket.id} (${reason})`);
        systemAnalytics.activeUsers = Math.max(0, systemAnalytics.activeUsers - 1);
        
        if (socket.sessionId && activeSessions.has(socket.sessionId)) {
            activeSessions.delete(socket.sessionId);
        }
    });
});

// Advanced AI Query Processing
async function processAIQuery(query, context, sessionId) {
    const lowerQuery = query.toLowerCase();
    
    // Generate offline answer (FAISS simulation)
    const offlineAnswer = generateOfflineAnswer(query);
    
    // Generate AI-enhanced answer
    let onlineAnswer = null;
    let confidence = 0.85;
    
    try {
        // Use Granite AI for enhanced processing
        const aiResponse = await graniteAI.generateResponse(query, {
            context: offlineAnswer,
            sessionId,
            userContext: context
        });
        
        onlineAnswer = aiResponse.answer;
        confidence = aiResponse.confidence || 0.85;
        
    } catch (error) {
        logger.error('AI processing error:', error);
        onlineAnswer = generateEnhancedOfflineAnswer(query, offlineAnswer);
    }
    
    return {
        query,
        offlineAnswer,
        onlineAnswer,
        confidence,
        sources: extractSources(query),
        followUpSuggestions: generateFollowUpSuggestions(query),
        relatedTopics: getRelatedTopics(query)
    };
}

// Enhanced offline answer generation
function generateOfflineAnswer(query) {
    const lowerQuery = query.toLowerCase();
    let responses = [];
    
    // Search for matching keywords with enhanced scoring
    for (const [keyword, data] of Object.entries(agricultureKnowledge)) {
        if (lowerQuery.includes(keyword)) {
            responses.push({
                keyword,
                ...data,
                relevanceScore: calculateRelevance(lowerQuery, keyword, data)
            });
        }
    }
    
    // Sort by relevance
    responses.sort((a, b) => b.relevanceScore - a.relevanceScore);
    
    if (responses.length === 0) {
        return generateGenericAdvice(query);
    }
    
    let answer = '📚 **Agricultural Knowledge Base Results:**\n\n';
    responses.slice(0, 3).forEach((resp, idx) => {
        answer += `**${idx + 1}. ${resp.keyword.toUpperCase()}** (${resp.category})\n`;
        answer += `**Affected Crops:** ${resp.crops.join(', ')}\n`;
        answer += `**Solution:** ${resp.solution}\n`;
        if (resp.symptoms) {
            answer += `**Symptoms:** ${resp.symptoms.join(', ')}\n`;
        }
        if (resp.prevention) {
            answer += `**Prevention:** ${resp.prevention.join(', ')}\n`;
        }
        answer += `**Severity:** ${resp.severity}\n\n`;
    });
    
    return answer.trim();
}

// Generate AI-like response
function generateOfflineAnswer(query) {
    const lowerQuery = query.toLowerCase();
    let responses = [];
    
    // Search for matching keywords
    for (const [keyword, data] of Object.entries(agricultureKnowledge)) {
        if (lowerQuery.includes(keyword)) {
            responses.push({
                problem: keyword,
                crops: data.crops.join(', '),
                solution: data.solution
            });
        }
    }
    
    if (responses.length === 0) {
        return `Based on your query about "${query}", here are general agricultural recommendations:\n\n` +
               `1. Conduct soil testing before planting\n` +
               `2. Ensure proper irrigation scheduling\n` +
               `3. Monitor weather conditions regularly\n` +
               `4. Use organic fertilizers when possible\n` +
               `5. Practice crop rotation for better soil health\n\n` +
               `For specific advice, please provide more details about your crop and location.`;
    }
    
    let answer = '📚 Based on Kisan Call Centre Database:\n\n';
    responses.forEach((resp, idx) => {
        answer += `${idx + 1}. **${resp.problem.toUpperCase()}** (Affects: ${resp.crops})\n`;
        answer += `   ${resp.solution}\n\n`;
    });
    
    return answer.trim();
}

function generateOnlineAnswer(query, offlineContext) {
    // Simulate AI-enhanced response
    const lowerQuery = query.toLowerCase();
    
    let enhancedAnswer = `🤖 AI-Enhanced Agricultural Guidance:\n\n`;
    
    if (lowerQuery.includes('aphid')) {
        enhancedAnswer += `For effective aphid control in mustard crops:\n\n`;
        enhancedAnswer += `**Immediate Action:**\n`;
        enhancedAnswer += `• Spray neem oil solution (5ml/liter) early morning\n`;
        enhancedAnswer += `• Alternative: Imidacloprid 17.8% SL @ 0.5ml/liter\n\n`;
        enhancedAnswer += `**Preventive Measures:**\n`;
        enhancedAnswer += `• Install yellow sticky traps in the field\n`;
        enhancedAnswer += `• Encourage natural predators like ladybugs\n`;
        enhancedAnswer += `• Maintain proper plant spacing for air circulation\n\n`;
        enhancedAnswer += `**Follow-up:**\n`;
        enhancedAnswer += `• Repeat application after 7-10 days if needed\n`;
        enhancedAnswer += `• Monitor plants regularly for re-infestation`;
    } else if (lowerQuery.includes('leaf spot') || lowerQuery.includes('tomato')) {
        enhancedAnswer += `For leaf spot disease in tomato:\n\n`;
        enhancedAnswer += `**Treatment Protocol:**\n`;
        enhancedAnswer += `• Remove and destroy infected leaves immediately\n`;
        enhancedAnswer += `• Spray Mancozeb 75% WP @ 2g/liter\n`;
        enhancedAnswer += `• Apply at 10-day intervals for 3-4 rounds\n\n`;
        enhancedAnswer += `**Cultural Practices:**\n`;
        enhancedAnswer += `• Avoid overhead watering\n`;
        enhancedAnswer += `• Ensure proper plant spacing\n`;
        enhancedAnswer += `• Use disease-resistant varieties\n`;
        enhancedAnswer += `• Practice crop rotation`;
    } else if (lowerQuery.includes('fertilizer') || lowerQuery.includes('maize')) {
        enhancedAnswer += `Fertilizer recommendations for maize during flowering:\n\n`;
        enhancedAnswer += `**Primary Nutrients:**\n`;
        enhancedAnswer += `• DAP (Diammonium Phosphate): 50kg/acre\n`;
        enhancedAnswer += `• Potash (MOP): 25kg/acre for better grain filling\n\n`;
        enhancedAnswer += `**Application Method:**\n`;
        enhancedAnswer += `• Apply as side dressing near plant base\n`;
        enhancedAnswer += `• Water immediately after application\n`;
        enhancedAnswer += `• Split application for better efficiency\n\n`;
        enhancedAnswer += `**Additional Tips:**\n`;
        enhancedAnswer += `• Monitor for nutrient deficiency symptoms\n`;
        enhancedAnswer += `• Consider foliar spray of micronutrients`;
    } else if (lowerQuery.includes('pm kisan') || lowerQuery.includes('scheme')) {
        enhancedAnswer += `PM Kisan Samman Nidhi Scheme Application Process:\n\n`;
        enhancedAnswer += `**Eligibility:**\n`;
        enhancedAnswer += `• Small and marginal farmers\n`;
        enhancedAnswer += `• Land holding up to 2 hectares\n\n`;
        enhancedAnswer += `**Required Documents:**\n`;
        enhancedAnswer += `• Aadhaar card\n`;
        enhancedAnswer += `• Land ownership documents\n`;
        enhancedAnswer += `• Bank account details\n`;
        enhancedAnswer += `• Mobile number\n\n`;
        enhancedAnswer += `**Application Steps:**\n`;
        enhancedAnswer += `1. Visit pmkisan.gov.in\n`;
        enhancedAnswer += `2. Click on 'Farmers Corner'\n`;
        enhancedAnswer += `3. Select 'New Farmer Registration'\n`;
        enhancedAnswer += `4. Fill required details and submit\n`;
        enhancedAnswer += `5. Note registration number for tracking\n\n`;
        enhancedAnswer += `**Benefits:** ₹6000 per year in 3 installments`;
    } else {
        enhancedAnswer += offlineContext + '\n\n';
        enhancedAnswer += `**General Recommendations:**\n`;
        enhancedAnswer += `• Always follow integrated pest management (IPM)\n`;
        enhancedAnswer += `• Use recommended dosages to avoid resistance\n`;
        enhancedAnswer += `• Maintain field hygiene and sanitation\n`;
        enhancedAnswer += `• Consult local agricultural extension officers\n`;
        enhancedAnswer += `• Keep records of treatments and results`;
    }
    
    return enhancedAnswer;
}

// API Routes
app.post('/api/query', (req, res) => {
    try {
        const { query, mode = 'online' } = req.body;
        
        if (!query) {
            return res.status(400).json({ 
                success: false, 
                error: 'Query is required' 
            });
        }
        
        // Generate offline answer (FAISS simulation)
        const offlineAnswer = generateOfflineAnswer(query);
        
        // Generate online answer if mode is online
        let onlineAnswer = null;
        if (mode === 'online') {
            onlineAnswer = generateOnlineAnswer(query, offlineAnswer);
        }
        
        res.json({
            success: true,
            query: query,
            offlineAnswer: offlineAnswer,
            onlineAnswer: onlineAnswer,
            mode: mode,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to process query' 
        });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'KrishiSahay API',
        version: '2.0.0'
    });
});

// Serve frontend
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🌾 KrishiSahay Server Running                      ║
║                                                       ║
║   Port: ${PORT}                                      ║
║   URL: http://localhost:${PORT}                      ║
║                                                       ║
║   Status: ✅ Ready to serve farmers!                 ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    `);
});
// Enhanced utility functions
function calculateRelevance(query, keyword, data) {
    let score = 0;
    
    // Exact keyword match
    if (query.includes(keyword)) score += 10;
    
    // Crop mentions
    if (data.crops) {
        data.crops.forEach(crop => {
            if (query.includes(crop)) score += 5;
        });
    }
    
    // Category relevance
    if (data.category && query.includes(data.category)) score += 3;
    
    // Symptom matches
    if (data.symptoms) {
        data.symptoms.forEach(symptom => {
            if (query.includes(symptom)) score += 2;
        });
    }
    
    return score;
}

function generateGenericAdvice(query) {
    return `Based on your query about "${query}", here are general agricultural recommendations:\n\n` +
           `🌱 **General Guidelines:**\n` +
           `• Conduct soil testing before planting\n` +
           `• Ensure proper irrigation scheduling\n` +
           `• Monitor weather conditions regularly\n` +
           `• Use organic fertilizers when possible\n` +
           `• Practice crop rotation for better soil health\n` +
           `• Maintain field hygiene and sanitation\n\n` +
           `For specific advice, please provide more details about your crop, location, and specific symptoms.`;
}

function generateEnhancedOfflineAnswer(query, offlineContext) {
    const lowerQuery = query.toLowerCase();
    
    let enhancedAnswer = `🤖 **AI-Enhanced Agricultural Guidance:**\n\n`;
    
    if (lowerQuery.includes('aphid')) {
        enhancedAnswer += `**Comprehensive Aphid Management Strategy:**\n\n`;
        enhancedAnswer += `**🎯 Immediate Action:**\n`;
        enhancedAnswer += `• Spray neem oil solution (5ml/liter) during early morning\n`;
        enhancedAnswer += `• Alternative: Imidacloprid 17.8% SL @ 0.5ml/liter\n`;
        enhancedAnswer += `• Target leaf undersides where aphids cluster\n\n`;
        enhancedAnswer += `**🛡️ Integrated Management:**\n`;
        enhancedAnswer += `• Install yellow sticky traps (10-15 per acre)\n`;
        enhancedAnswer += `• Encourage natural predators (ladybugs, lacewings)\n`;
        enhancedAnswer += `• Maintain proper plant spacing for air circulation\n`;
        enhancedAnswer += `• Remove weeds that harbor aphids\n\n`;
        enhancedAnswer += `**📅 Follow-up Protocol:**\n`;
        enhancedAnswer += `• Monitor plants every 2-3 days\n`;
        enhancedAnswer += `• Repeat treatment after 7-10 days if needed\n`;
        enhancedAnswer += `• Document treatment effectiveness\n`;
    } else if (lowerQuery.includes('leaf spot') || lowerQuery.includes('tomato')) {
        enhancedAnswer += `**Advanced Leaf Spot Disease Management:**\n\n`;
        enhancedAnswer += `**🚨 Emergency Treatment:**\n`;
        enhancedAnswer += `• Remove and destroy infected leaves immediately\n`;
        enhancedAnswer += `• Spray Mancozeb 75% WP @ 2g/liter\n`;
        enhancedAnswer += `• Apply copper oxychloride as alternative\n\n`;
        enhancedAnswer += `**🌿 Cultural Practices:**\n`;
        enhancedAnswer += `• Avoid overhead watering (use drip irrigation)\n`;
        enhancedAnswer += `• Ensure 3-4 feet plant spacing\n`;
        enhancedAnswer += `• Improve soil drainage\n`;
        enhancedAnswer += `• Use disease-resistant varieties\n\n`;
        enhancedAnswer += `**🔄 Long-term Strategy:**\n`;
        enhancedAnswer += `• Practice 3-year crop rotation\n`;
        enhancedAnswer += `• Apply organic mulch to reduce soil splash\n`;
        enhancedAnswer += `• Regular field sanitation\n`;
    } else if (lowerQuery.includes('fertilizer') || lowerQuery.includes('maize')) {
        enhancedAnswer += `**Precision Fertilizer Management for Maize:**\n\n`;
        enhancedAnswer += `**🌾 Flowering Stage Nutrition:**\n`;
        enhancedAnswer += `• DAP (Diammonium Phosphate): 50kg/acre\n`;
        enhancedAnswer += `• Potash (MOP): 25kg/acre for grain filling\n`;
        enhancedAnswer += `• Zinc Sulphate: 10kg/acre if deficient\n\n`;
        enhancedAnswer += `**📍 Application Method:**\n`;
        enhancedAnswer += `• Apply as side dressing 6 inches from plant base\n`;
        enhancedAnswer += `• Water immediately after application\n`;
        enhancedAnswer += `• Split application for better efficiency\n\n`;
        enhancedAnswer += `**🔬 Monitoring & Adjustment:**\n`;
        enhancedAnswer += `• Watch for nutrient deficiency symptoms\n`;
        enhancedAnswer += `• Consider foliar spray of micronutrients\n`;
        enhancedAnswer += `• Adjust based on soil test results\n`;
    } else if (lowerQuery.includes('pm kisan') || lowerQuery.includes('scheme')) {
        enhancedAnswer += `**Complete PM Kisan Samman Nidhi Guide:**\n\n`;
        enhancedAnswer += `**✅ Eligibility Criteria:**\n`;
        enhancedAnswer += `• Small and marginal farmers only\n`;
        enhancedAnswer += `• Land holding up to 2 hectares\n`;
        enhancedAnswer += `• Cultivable land ownership required\n\n`;
        enhancedAnswer += `**📋 Required Documents:**\n`;
        enhancedAnswer += `• Aadhaar card (mandatory)\n`;
        enhancedAnswer += `• Land ownership documents (Khatauni/Registry)\n`;
        enhancedAnswer += `• Bank account details (IFSC code)\n`;
        enhancedAnswer += `• Mobile number linked to Aadhaar\n\n`;
        enhancedAnswer += `**🌐 Step-by-Step Application:**\n`;
        enhancedAnswer += `1. Visit pmkisan.gov.in\n`;
        enhancedAnswer += `2. Click 'Farmers Corner' → 'New Farmer Registration'\n`;
        enhancedAnswer += `3. Enter Aadhaar number and captcha\n`;
        enhancedAnswer += `4. Fill personal and land details\n`;
        enhancedAnswer += `5. Upload required documents\n`;
        enhancedAnswer += `6. Submit and note registration number\n\n`;
        enhancedAnswer += `**💰 Benefits & Timeline:**\n`;
        enhancedAnswer += `• ₹6000 per year in 3 equal installments\n`;
        enhancedAnswer += `• Direct bank transfer every 4 months\n`;
        enhancedAnswer += `• First installment: April-July\n`;
        enhancedAnswer += `• Second installment: August-November\n`;
        enhancedAnswer += `• Third installment: December-March\n`;
    } else {
        enhancedAnswer += offlineContext + '\n\n';
        enhancedAnswer += `**🎯 Smart Recommendations:**\n`;
        enhancedAnswer += `• Follow integrated pest management (IPM) approach\n`;
        enhancedAnswer += `• Use recommended dosages to prevent resistance\n`;
        enhancedAnswer += `• Maintain detailed field records\n`;
        enhancedAnswer += `• Consult local agricultural extension officers\n`;
        enhancedAnswer += `• Join farmer producer organizations (FPOs)\n`;
        enhancedAnswer += `• Stay updated with weather forecasts\n`;
    }
    
    return enhancedAnswer;
}

function extractSources(query) {
    // Simulate source extraction
    return [
        { name: 'Kisan Call Centre Database', confidence: 0.95 },
        { name: 'ICAR Guidelines', confidence: 0.88 },
        { name: 'State Agriculture Department', confidence: 0.82 }
    ];
}

function generateFollowUpSuggestions(query) {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('pest') || lowerQuery.includes('aphid') || lowerQuery.includes('whitefly')) {
        return [
            'How to identify beneficial insects?',
            'Organic pest control methods',
            'Integrated pest management strategies',
            'When to apply pesticides for maximum effectiveness?'
        ];
    } else if (lowerQuery.includes('disease') || lowerQuery.includes('spot') || lowerQuery.includes('blight')) {
        return [
            'Disease-resistant crop varieties',
            'Preventive fungicide spray schedule',
            'Crop rotation for disease management',
            'How to improve plant immunity naturally?'
        ];
    } else if (lowerQuery.includes('fertilizer') || lowerQuery.includes('nutrient')) {
        return [
            'Soil testing procedures and interpretation',
            'Organic vs chemical fertilizers comparison',
            'Micronutrient deficiency symptoms',
            'Fertilizer application timing guide'
        ];
    } else if (lowerQuery.includes('scheme') || lowerQuery.includes('kisan')) {
        return [
            'Other government schemes for farmers',
            'Crop insurance application process',
            'Subsidy programs for agricultural equipment',
            'How to get agricultural loans?'
        ];
    }
    
    return [
        'Weather impact on crop growth',
        'Best practices for your region',
        'Market price trends for your crops',
        'Seasonal farming calendar'
    ];
}

function getRelatedTopics(query) {
    const lowerQuery = query.toLowerCase();
    
    const topics = [];
    
    if (lowerQuery.includes('pest')) {
        topics.push('Integrated Pest Management', 'Beneficial Insects', 'Organic Pesticides');
    }
    if (lowerQuery.includes('disease')) {
        topics.push('Plant Pathology', 'Disease Prevention', 'Resistant Varieties');
    }
    if (lowerQuery.includes('fertilizer')) {
        topics.push('Soil Health', 'Nutrient Management', 'Organic Farming');
    }
    if (lowerQuery.includes('crop')) {
        topics.push('Crop Selection', 'Seasonal Planning', 'Market Analysis');
    }
    
    return topics.length > 0 ? topics : ['Sustainable Agriculture', 'Climate-Smart Farming', 'Precision Agriculture'];
}

function updateTopQueries(query) {
    const existing = systemAnalytics.topQueries.find(q => q.query === query);
    if (existing) {
        existing.count++;
    } else {
        systemAnalytics.topQueries.push({ query, count: 1 });
    }
    
    // Keep only top 10
    systemAnalytics.topQueries.sort((a, b) => b.count - a.count);
    systemAnalytics.topQueries = systemAnalytics.topQueries.slice(0, 10);
}

// Legacy API Routes (for backward compatibility)
app.post('/api/query', async (req, res) => {
    try {
        const { query, mode = 'online' } = req.body;
        
        if (!query) {
            return res.status(400).json({ 
                success: false, 
                error: 'Query is required' 
            });
        }
        
        const startTime = Date.now();
        
        // Process query
        const result = await processAIQuery(query, {}, 'api-request');
        
        const responseTime = Date.now() - startTime;
        
        res.json({
            success: true,
            query: query,
            offlineAnswer: result.offlineAnswer,
            onlineAnswer: mode === 'online' ? result.onlineAnswer : null,
            confidence: result.confidence,
            sources: result.sources,
            followUpSuggestions: result.followUpSuggestions,
            mode: mode,
            responseTime,
            timestamp: new Date().toISOString()
        });
        
        // Update analytics
        systemAnalytics.totalQueries++;
        systemAnalytics.avgResponseTime = Math.round(
            (systemAnalytics.avgResponseTime + responseTime) / 2
        );
        
    } catch (error) {
        logger.error('API Error:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to process query' 
        });
    }
});

// Analytics API
app.get('/api/analytics', (req, res) => {
    res.json({
        ...systemAnalytics,
        activeSessions: activeSessions.size,
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        timestamp: new Date().toISOString()
    });
});

// Health check with detailed status
app.get('/api/health', (req, res) => {
    const health = {
        status: 'healthy',
        service: 'KrishiSahay Live AI API',
        version: '2.0.0',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        components: {
            redis: redisClient ? 'connected' : 'unavailable',
            ai: graniteAI ? 'ready' : 'unavailable',
            websocket: 'active',
            database: 'simulated'
        },
        stats: systemAnalytics
    };
    
    res.json(health);
});

// System status endpoint
app.get('/api/status', (req, res) => {
    res.json({
        activeConnections: io.engine.clientsCount,
        activeSessions: activeSessions.size,
        totalQueries: systemAnalytics.totalQueries,
        avgResponseTime: systemAnalytics.avgResponseTime,
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        timestamp: new Date().toISOString()
    });
});

// Serve frontend
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Scheduled tasks
cron.schedule('*/5 * * * *', () => {
    // Clean up inactive sessions every 5 minutes
    const now = new Date();
    for (const [sessionId, session] of activeSessions.entries()) {
        if (now - session.lastActivity > 30 * 60 * 1000) { // 30 minutes
            activeSessions.delete(sessionId);
            logger.info(`🧹 Cleaned up inactive session: ${sessionId}`);
        }
    }
    
    // Update system analytics
    systemAnalytics.lastUpdated = now;
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    logger.info('🛑 Received SIGTERM, shutting down gracefully...');
    
    if (redisClient) {
        await redisClient.quit();
    }
    
    server.close(() => {
        logger.info('✅ Server closed');
        process.exit(0);
    });
});

// Error handling
process.on('unhandledRejection', (reason, promise) => {
    logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
    logger.error('Uncaught Exception:', error);
    process.exit(1);
});

// Start server
server.listen(PORT, () => {
    logger.info(`
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🌾 KrishiSahay Live AI Server v2.0.0                                       ║
║                                                                               ║
║   🚀 Server Status: RUNNING                                                   ║
║   🌐 Port: ${PORT}                                                           ║
║   🔗 URL: http://localhost:${PORT}                                           ║
║   📡 WebSocket: ENABLED                                                       ║
║   🧠 AI Engine: IBM Watsonx Granite                                          ║
║   💾 Cache: ${redisClient ? 'Redis Connected' : 'In-Memory Fallback'}        ║
║   📊 Analytics: ACTIVE                                                        ║
║                                                                               ║
║   ✅ Ready to serve farmers with advanced AI assistance!                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    `);
    
    console.log('\n🔧 Available Endpoints:');
    console.log('   • GET  /api/health     - Health check');
    console.log('   • GET  /api/status     - System status');
    console.log('   • GET  /api/analytics  - Usage analytics');
    console.log('   • POST /api/query      - Legacy query API');
    console.log('   • WS   /              - WebSocket connection');
    console.log('\n📡 WebSocket Events:');
    console.log('   • join-session        - Join chat session');
    console.log('   • chat-message        - Send chat message');
    console.log('   • user-typing         - Typing indicator');
    console.log('   • feedback            - Submit feedback');
    console.log('   • request-analytics   - Get live analytics');
    console.log('\n🌟 Features:');
    console.log('   • Real-time AI chat with WebSocket');
    console.log('   • Advanced agricultural knowledge base');
    console.log('   • IBM Watsonx Granite LLM integration');
    console.log('   • Redis caching and session management');
    console.log('   • Live analytics and monitoring');
    console.log('   • Rate limiting and security');
    console.log('   • Comprehensive logging');
    console.log('   • Graceful shutdown handling');
});