#!/usr/bin/env python3
"""
KrishiSahay Flask Backend Server
Python-based backend with real-time features, AI search engine, and IBM Watsonx integration
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import AI Search Engine and Watsonx
from ai_search_engine import AISearchEngine, RealTimeChatAI
from watsonx_integration import WatsonxGraniteAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='public', static_url_path='')
app.config['SECRET_KEY'] = 'krishisahay-secret-2024'

# Enable CORS
CORS(app, origins="*")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
active_sessions = {}
chat_history = {}
system_analytics = {
    'total_queries': 0,
    'avg_response_time': 0,
    'active_users': 0,
    'error_rate': 0
}

# Initialize IBM Watsonx AI
watsonx_ai = WatsonxGraniteAI()

# Initialize AI Search Engine and Chat AI
search_engine = AISearchEngine()
chat_ai = None  # Will be initialized after knowledge base is loaded

# Enhanced Agricultural Knowledge Base
AGRICULTURE_KNOWLEDGE = {
    'aphids': {
        'crops': ['mustard', 'wheat', 'cotton'],
        'solution': 'Spray neem oil solution (5ml per liter) or use imidacloprid 17.8% SL @ 0.5ml/liter. Apply during early morning or evening.',
        'severity': 'medium',
        'category': 'pest',
        'symptoms': ['curled leaves', 'sticky honeydew', 'yellowing'],
        'prevention': ['regular monitoring', 'beneficial insects', 'proper spacing']
    },
    'leaf spot': {
        'crops': ['tomato', 'potato'],
        'solution': 'Remove infected leaves. Spray mancozeb 75% WP @ 2g/liter or copper oxychloride @ 3g/liter at 10-day intervals.',
        'severity': 'high',
        'category': 'disease',
        'symptoms': ['brown spots', 'leaf yellowing', 'defoliation'],
        'prevention': ['crop rotation', 'proper drainage', 'resistant varieties']
    },
    'whitefly': {
        'crops': ['cotton', 'tomato'],
        'solution': 'Use thiamethoxam 25% WG @ 0.2g/liter or spray neem-based pesticides. Ensure coverage on leaf undersides.',
        'severity': 'medium',
        'category': 'pest',
        'symptoms': ['white flying insects', 'yellowing leaves', 'sooty mold'],
        'prevention': ['yellow sticky traps', 'reflective mulch', 'companion planting']
    },
    'fruit borer': {
        'crops': ['brinjal', 'tomato'],
        'solution': 'Install pheromone traps. Spray spinosad 45% SC @ 0.3ml/liter or use Bacillus thuringiensis.',
        'severity': 'high',
        'category': 'pest',
        'symptoms': ['holes in fruits', 'larvae inside', 'fruit drop'],
        'prevention': ['pheromone traps', 'clean cultivation', 'timely harvest']
    },
    'fertilizer': {
        'crops': ['maize', 'wheat', 'rice'],
        'solution': 'Apply DAP (Diammonium Phosphate) @ 50kg/acre during flowering. Supplement with potash for better yield.',
        'severity': 'low',
        'category': 'nutrition',
        'symptoms': ['poor growth', 'yellowing', 'low yield'],
        'prevention': ['soil testing', 'balanced nutrition', 'organic matter']
    },
    'pm kisan': {
        'crops': ['all'],
        'solution': 'Visit PM Kisan portal (pmkisan.gov.in), register with Aadhaar, land records, and bank details.',
        'severity': 'low',
        'category': 'scheme',
        'benefits': ['₹6000 per year', '3 installments', 'direct transfer'],
        'eligibility': ['small farmers', 'marginal farmers', 'up to 2 hectares']
    }
}

# Initialize Chat AI with knowledge base and Watsonx
chat_ai = RealTimeChatAI(AGRICULTURE_KNOWLEDGE, watsonx_ai)
logger.info("✅ AI Search Engine and Chat AI initialized")
logger.info(f"✅ IBM Watsonx: {'Enabled' if watsonx_ai.is_available else 'Disabled (using fallback)'}")

def calculate_relevance(query, keyword, data):
    """Calculate relevance score"""
    score = 0
    query_lower = query.lower()
    
    if keyword in query_lower:
        score += 10
    
    if 'crops' in data:
        for crop in data['crops']:
            if crop in query_lower:
                score += 5
    
    if 'category' in data and data['category'] in query_lower:
        score += 3
    
    return score

def generate_offline_answer(query):
    """Generate answer from knowledge base"""
    query_lower = query.lower()
    responses = []
    
    for keyword, data in AGRICULTURE_KNOWLEDGE.items():
        relevance = calculate_relevance(query, keyword, data)
        if relevance > 0:
            responses.append({
                'keyword': keyword,
                'relevance': relevance,
                **data
            })
    
    responses.sort(key=lambda x: x['relevance'], reverse=True)
    
    if not responses:
        return generate_generic_advice(query)
    
    answer = '📚 **Agricultural Knowledge Base Results:**\n\n'
    for i, resp in enumerate(responses[:3], 1):
        answer += f"**{i}. {resp['keyword'].upper()}** ({resp['category']})\n"
        answer += f"**Crops:** {', '.join(resp['crops'])}\n"
        answer += f"**Solution:** {resp['solution']}\n"
        if 'symptoms' in resp:
            answer += f"**Symptoms:** {', '.join(resp['symptoms'])}\n"
        answer += f"**Severity:** {resp['severity']}\n\n"
    
    return answer.strip()

def generate_generic_advice(query):
    """Generate generic agricultural advice"""
    return f"""Based on your query about "{query}", here are general agricultural recommendations:

🌱 **General Guidelines:**
• Conduct soil testing before planting
• Ensure proper irrigation scheduling
• Monitor weather conditions regularly
• Use organic fertilizers when possible
• Practice crop rotation for better soil health
• Maintain field hygiene and sanitation

For specific advice, please provide more details about your crop, location, and symptoms."""

def detect_question_type(query):
    """Detect the type of agricultural question"""
    query_lower = query.lower()
    
    # Question type patterns
    if any(word in query_lower for word in ['how', 'method', 'way', 'process']):
        return 'How-To Guide'
    elif any(word in query_lower for word in ['what', 'which', 'define']):
        return 'Information Query'
    elif any(word in query_lower for word in ['when', 'timing', 'time']):
        return 'Timing & Schedule'
    elif any(word in query_lower for word in ['why', 'reason', 'cause']):
        return 'Explanation'
    elif any(word in query_lower for word in ['where', 'location', 'place']):
        return 'Location-based'
    elif any(word in query_lower for word in ['best', 'recommend', 'suggest']):
        return 'Recommendation'
    elif any(word in query_lower for word in ['problem', 'issue', 'trouble', 'help']):
        return 'Problem Solving'
    else:
        return 'General Query'

def generate_comprehensive_response(query, category, knowledge_data):
    """Generate comprehensive response based on question type and category"""
    question_type = detect_question_type(query.lower())
    
    response = f"🎯 **{question_type}** - {category.upper()}\n\n"
    
    # Add context-aware introduction
    if question_type == 'How-To Guide':
        response += "📋 **Step-by-Step Solution:**\n\n"
    elif question_type == 'Information Query':
        response += "📚 **Detailed Information:**\n\n"
    elif question_type == 'Timing & Schedule':
        response += "⏰ **Optimal Timing Guide:**\n\n"
    elif question_type == 'Problem Solving':
        response += "🔧 **Problem Resolution:**\n\n"
    elif question_type == 'Recommendation':
        response += "⭐ **Expert Recommendations:**\n\n"
    
    # Add knowledge data
    if isinstance(knowledge_data, dict):
        if 'solution' in knowledge_data:
            response += f"**Primary Solution:**\n{knowledge_data['solution']}\n\n"
        
        if 'symptoms' in knowledge_data:
            response += f"**Symptoms to Watch:**\n"
            for symptom in knowledge_data['symptoms']:
                response += f"• {symptom.capitalize()}\n"
            response += "\n"
        
        if 'prevention' in knowledge_data:
            response += f"**Prevention Measures:**\n"
            for prevention in knowledge_data['prevention']:
                response += f"• {prevention.capitalize()}\n"
            response += "\n"
        
        if 'organic_solutions' in knowledge_data:
            response += f"**Organic Solutions:**\n"
            for solution in knowledge_data['organic_solutions']:
                response += f"• {solution.capitalize()}\n"
            response += "\n"
        
        if 'chemical_solutions' in knowledge_data:
            response += f"**Chemical Solutions:**\n"
            for solution in knowledge_data['chemical_solutions']:
                response += f"• {solution.capitalize()}\n"
            response += "\n"
        
        if 'application_timing' in knowledge_data:
            response += f"**Best Application Time:**\n"
            for timing in knowledge_data['application_timing']:
                response += f"• {timing.capitalize()}\n"
            response += "\n"
        
        if 'dosage' in knowledge_data:
            response += f"**Recommended Dosage:**\n{knowledge_data['dosage']}\n\n"
        
        if 'benefits' in knowledge_data:
            response += f"**Benefits:**\n"
            for benefit in knowledge_data['benefits']:
                response += f"• {benefit}\n"
            response += "\n"
        
        if 'eligibility' in knowledge_data:
            response += f"**Eligibility:**\n"
            for criteria in knowledge_data['eligibility']:
                response += f"• {criteria.capitalize()}\n"
            response += "\n"
    
    # Add general recommendations
    response += "**💡 Additional Tips:**\n"
    response += "• Always follow integrated management practices\n"
    response += "• Consult local agricultural extension officers\n"
    response += "• Keep detailed records of treatments\n"
    response += "• Monitor results and adjust as needed\n"
    
    return response

def generate_enhanced_answer(query, offline_context):
    """Generate AI-enhanced answer with comprehensive coverage"""
    query_lower = query.lower()
    
    # Detect question type
    question_type = detect_question_type(query_lower)
    
    enhanced_answer = f'🤖 **AI-Enhanced Agricultural Guidance** ({question_type}):\n\n'
    
    # Handle different question types
    if 'aphid' in query_lower:
        enhanced_answer += """**Comprehensive Aphid Management:**

**🎯 Immediate Action:**
• Spray neem oil solution (5ml/liter) early morning
• Alternative: Imidacloprid 17.8% SL @ 0.5ml/liter
• Target leaf undersides where aphids cluster

**🛡️ Integrated Management:**
• Install yellow sticky traps (10-15 per acre)
• Encourage natural predators (ladybugs, lacewings)
• Maintain proper plant spacing for air circulation

**📅 Follow-up Protocol:**
• Monitor plants every 2-3 days
• Repeat treatment after 7-10 days if needed
• Document treatment effectiveness"""

    elif 'leaf spot' in query_lower or 'tomato' in query_lower:
        enhanced_answer += """**Advanced Leaf Spot Management:**

**🚨 Emergency Treatment:**
• Remove and destroy infected leaves immediately
• Spray Mancozeb 75% WP @ 2g/liter
• Apply copper oxychloride as alternative

**🌿 Cultural Practices:**
• Avoid overhead watering (use drip irrigation)
• Ensure 3-4 feet plant spacing
• Improve soil drainage
• Use disease-resistant varieties

**🔄 Long-term Strategy:**
• Practice 3-year crop rotation
• Apply organic mulch to reduce soil splash
• Regular field sanitation"""

    elif 'fertilizer' in query_lower or 'maize' in query_lower:
        enhanced_answer += """**Precision Fertilizer Management:**

**🌾 Flowering Stage Nutrition:**
• DAP (Diammonium Phosphate): 50kg/acre
• Potash (MOP): 25kg/acre for grain filling
• Zinc Sulphate: 10kg/acre if deficient

**📍 Application Method:**
• Apply as side dressing 6 inches from plant base
• Water immediately after application
• Split application for better efficiency

**🔬 Monitoring & Adjustment:**
• Watch for nutrient deficiency symptoms
• Consider foliar spray of micronutrients
• Adjust based on soil test results"""

    elif 'pm kisan' in query_lower or 'scheme' in query_lower:
        enhanced_answer += """**Complete PM Kisan Guide:**

**✅ Eligibility:**
• Small and marginal farmers only
• Land holding up to 2 hectares
• Cultivable land ownership required

**📋 Required Documents:**
• Aadhaar card (mandatory)
• Land ownership documents
• Bank account details (IFSC code)
• Mobile number linked to Aadhaar

**🌐 Application Process:**
1. Visit pmkisan.gov.in
2. Click 'Farmers Corner' → 'New Farmer Registration'
3. Enter Aadhaar and fill details
4. Upload documents and submit
5. Note registration number for tracking

**💰 Benefits:**
• ₹6000 per year in 3 installments
• Direct bank transfer every 4 months"""

    else:
        enhanced_answer += offline_context + '\n\n'
        enhanced_answer += """**🎯 Smart Recommendations:**
• Follow integrated pest management (IPM)
• Use recommended dosages to prevent resistance
• Maintain detailed field records
• Consult local agricultural extension officers
• Stay updated with weather forecasts"""
    
    return enhanced_answer

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    logger.info(f'Client connected: {request.sid}')
    system_analytics['active_users'] += 1
    emit('connection-status', {'connected': True})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')
    system_analytics['active_users'] = max(0, system_analytics['active_users'] - 1)
    
    # Clean up session
    session_to_remove = None
    for session_id, session_data in active_sessions.items():
        if session_data.get('socket_id') == request.sid:
            session_to_remove = session_id
            break
    
    if session_to_remove:
        del active_sessions[session_to_remove]

@socketio.on('join-session')
def handle_join_session(session_id):
    logger.info(f'Session joined: {session_id}')
    
    active_sessions[session_id] = {
        'socket_id': request.sid,
        'join_time': datetime.now(),
        'last_activity': datetime.now(),
        'query_count': 0
    }
    
    emit('system-update', {
        'type': 'welcome',
        'message': 'Connected to KrishiSahay AI Server',
        'capabilities': ['Real-time AI Chat', 'Agricultural Knowledge Base', 'Expert Guidance']
    })

@socketio.on('chat-message')
def handle_chat_message(data):
    start_time = time.time()
    session_id = data.get('sessionId')
    message = data.get('message')
    context = data.get('context', {})
    
    logger.info(f'Processing message from {session_id}: {message[:50]}...')
    
    try:
        # Update session activity
        if session_id in active_sessions:
            active_sessions[session_id]['last_activity'] = datetime.now()
            active_sessions[session_id]['query_count'] += 1
        
        # Show typing indicator
        emit('ai-typing', True)
        
        # Process with AI Search Engine
        ai_result = chat_ai.process_message(message, session_id)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000
        system_analytics['avg_response_time'] = (
            system_analytics['avg_response_time'] + response_time
        ) / 2
        
        # Store in chat history
        if session_id not in chat_history:
            chat_history[session_id] = []
        
        chat_history[session_id].append({
            'query': message,
            'response': ai_result['response'],
            'timestamp': datetime.now().isoformat(),
            'response_time': response_time,
            'search_results': ai_result['search_results']['total_results']
        })
        
        # Stop typing indicator
        emit('ai-typing', False)
        
        # Send comprehensive response
        emit('ai-response', {
            'query': message,
            'offlineAnswer': generate_offline_answer(message),
            'onlineAnswer': ai_result['response'],
            'confidence': ai_result.get('confidence', 0.90),
            'sources': [
                {'name': ai_result.get('source', 'AI Search Engine'), 'confidence': ai_result.get('confidence', 0.90)},
                {'name': 'Knowledge Base', 'confidence': 0.88},
                {'name': f"{ai_result['search_results']['total_results']} sources found", 'confidence': 0.85}
            ],
            'followUpSuggestions': ai_result['suggestions'],
            'searchResults': ai_result['search_results'],
            'intent': ai_result['intent'],
            'watsonxEnabled': watsonx_ai.is_available,
            'responseTime': response_time,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update analytics
        system_analytics['total_queries'] += 1
        
        logger.info(f'✅ AI response sent in {response_time:.2f}ms with {ai_result["search_results"]["total_results"]} search results')
        
    except Exception as e:
        logger.error(f'Error processing message: {e}')
        emit('ai-error', {
            'message': 'Sorry, I encountered an error processing your request.',
            'error': str(e)
        })

def generate_followup_suggestions(query):
    """Generate follow-up suggestions based on query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['pest', 'aphid', 'whitefly']):
        return [
            'How to identify beneficial insects?',
            'Organic pest control methods',
            'Integrated pest management strategies',
            'When to apply pesticides for maximum effectiveness?'
        ]
    elif any(word in query_lower for word in ['disease', 'spot', 'blight']):
        return [
            'Disease-resistant crop varieties',
            'Preventive fungicide spray schedule',
            'Crop rotation for disease management',
            'How to improve plant immunity naturally?'
        ]
    elif any(word in query_lower for word in ['fertilizer', 'nutrient']):
        return [
            'Soil testing procedures and interpretation',
            'Organic vs chemical fertilizers comparison',
            'Micronutrient deficiency symptoms',
            'Fertilizer application timing guide'
        ]
    elif any(word in query_lower for word in ['scheme', 'kisan']):
        return [
            'Other government schemes for farmers',
            'Crop insurance application process',
            'Subsidy programs for agricultural equipment',
            'How to get agricultural loans?'
        ]
    
    return [
        'Weather impact on crop growth',
        'Best practices for your region',
        'Market price trends for your crops',
        'Seasonal farming calendar'
    ]

# REST API Routes
@app.route('/api/query', methods=['POST'])
def api_query():
    try:
        data = request.get_json()
        query = data.get('query')
        mode = data.get('mode', 'online')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        start_time = time.time()
        
        # Generate responses
        offline_answer = generate_offline_answer(query)
        online_answer = generate_enhanced_answer(query, offline_answer) if mode == 'online' else None
        
        response_time = (time.time() - start_time) * 1000
        
        # Update analytics
        system_analytics['total_queries'] += 1
        system_analytics['avg_response_time'] = (
            system_analytics['avg_response_time'] + response_time
        ) / 2
        
        return jsonify({
            'success': True,
            'query': query,
            'offlineAnswer': offline_answer,
            'onlineAnswer': online_answer,
            'confidence': 0.85,
            'sources': [
                {'name': 'Kisan Call Centre Database', 'confidence': 0.95},
                {'name': 'Agricultural Guidelines', 'confidence': 0.88}
            ],
            'followUpSuggestions': generate_followup_suggestions(query),
            'mode': mode,
            'responseTime': response_time,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f'API Error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to process query'
        }), 500

@app.route('/api/health')
def health_check():
    watsonx_stats = watsonx_ai.get_stats()
    return jsonify({
        'status': 'healthy',
        'service': 'KrishiSahay Flask API',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'websocket': 'active',
            'database': 'simulated',
            'ai_search': 'ready',
            'watsonx': 'enabled' if watsonx_stats['is_available'] else 'disabled'
        },
        'watsonx': watsonx_stats,
        'stats': system_analytics
    })

@app.route('/api/analytics')
def get_analytics():
    return jsonify({
        **system_analytics,
        'activeSessions': len(active_sessions),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def get_status():
    return jsonify({
        'activeConnections': len(active_sessions),
        'activeSessions': len(active_sessions),
        'totalQueries': system_analytics['total_queries'],
        'avgResponseTime': system_analytics['avg_response_time'],
        'timestamp': datetime.now().isoformat()
    })

# New AI Search Engine Endpoints
@app.route('/api/search', methods=['POST'])
def api_search():
    """Advanced search endpoint"""
    try:
        data = request.get_json()
        query = data.get('query')
        context = data.get('context', {})
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Perform AI search
        search_results = search_engine.search(query, AGRICULTURE_KNOWLEDGE, context)
        
        return jsonify({
            'success': True,
            'search_results': search_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Search API Error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to perform search'
        }), 500

@app.route('/api/trending')
def get_trending():
    """Get trending search queries"""
    try:
        trending = search_engine.get_trending_queries()
        return jsonify({
            'success': True,
            'trending_queries': trending,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f'Trending API Error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get trending queries'
        }), 500

@app.route('/api/search-stats')
def get_search_stats():
    """Get search engine statistics"""
    try:
        stats = search_engine.get_search_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f'Search Stats API Error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get search statistics'
        }), 500

@app.route('/api/conversation/<session_id>')
def get_conversation(session_id):
    """Get conversation history for a session"""
    try:
        conversation = chat_ai.get_conversation_context(session_id)
        return jsonify({
            'success': True,
            'session_id': session_id,
            'conversation': conversation,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f'Conversation API Error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get conversation history'
        }), 500

@app.route('/api/watsonx/status')
def get_watsonx_status():
    """Get IBM Watsonx integration status"""
    try:
        stats = watsonx_ai.get_stats()
        return jsonify({
            'success': True,
            'watsonx': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f'Watsonx Status API Error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get Watsonx status'
        }), 500

@app.route('/api/watsonx/generate', methods=['POST'])
def watsonx_generate():
    """Direct Watsonx generation endpoint"""
    try:
        data = request.get_json()
        query = data.get('query')
        context = data.get('context', {})
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        if not watsonx_ai.is_available:
            return jsonify({
                'success': False,
                'error': 'IBM Watsonx API not configured'
            }), 503
        
        # Generate response
        response = watsonx_ai.generate_response(query, context)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Watsonx Generate API Error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to generate Watsonx response'
        }), 500

@app.route('/api/watsonx/clear-cache', methods=['POST'])
def clear_watsonx_cache():
    """Clear Watsonx response cache"""
    try:
        watsonx_ai.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Watsonx cache cleared',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f'Clear Cache API Error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to clear cache'
        }), 500

# Serve static files
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🌾 KrishiSahay Flask Backend Server v2.0.0                                 ║
║   🔍 With AI-Powered Real-Time Search Engine                                 ║
║   🤖 IBM Watsonx Granite LLM Integration                                     ║
║                                                                               ║
║   🚀 Server Status: RUNNING                                                   ║
║   🌐 Port: {port}                                                            ║
║   🔗 URL: http://localhost:{port}                                            ║
║   📡 WebSocket: ENABLED                                                       ║
║   🧠 AI Engine: Advanced Search + Chat AI                                    ║
║   🔍 Search: Real-time Intelligent Search                                    ║
║   🤖 Watsonx: {'ENABLED ✅' if watsonx_ai.is_available else 'DISABLED ⚠️ (using fallback)'}                                    ║
║   📊 Analytics: ACTIVE                                                        ║
║                                                                               ║
║   ✅ Ready to serve farmers with AI-powered assistance!                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print('\n🔧 Available Endpoints:')
    print('   • GET  /api/health         - Health check')
    print('   • GET  /api/status         - System status')
    print('   • GET  /api/analytics      - Usage analytics')
    print('   • POST /api/query          - Query API')
    print('   • POST /api/search         - AI Search Engine')
    print('   • GET  /api/trending       - Trending queries')
    print('   • GET  /api/search-stats   - Search statistics')
    print('   • GET  /api/conversation/<id> - Conversation history')
    print('   • GET  /api/watsonx/status - Watsonx status')
    print('   • POST /api/watsonx/generate - Direct Watsonx generation')
    print('   • POST /api/watsonx/clear-cache - Clear Watsonx cache')
    print('   • WS   /                   - WebSocket connection')
    
    print('\n📡 WebSocket Events:')
    print('   • join-session        - Join chat session')
    print('   • chat-message        - Send chat message')
    print('   • ai-response         - Receive AI response')
    print('   • ai-typing           - Typing indicator')
    
    print('\n🌟 Features:')
    print('   • Real-time chat with WebSocket')
    print('   • IBM Watsonx Granite LLM integration')
    print('   • AI-powered intelligent search engine')
    print('   • Context-aware query understanding')
    print('   • Multi-source knowledge integration')
    print('   • Smart query expansion with synonyms')
    print('   • Intent detection and classification')
    print('   • Trending queries and analytics')
    print('   • Conversation history tracking')
    print('   • Follow-up suggestions')
    print('   • Response caching for performance')
    print('   • Automatic fallback when Watsonx unavailable')
    print('   • Live analytics and monitoring')
    print('   • Cross-platform compatibility')
    
    if not watsonx_ai.is_available:
        print('\n⚠️  IBM Watsonx Configuration:')
        print('   To enable IBM Watsonx Granite LLM, set these environment variables:')
        print('   • WATSONX_API_KEY=your_api_key')
        print('   • WATSONX_PROJECT_ID=your_project_id')
        print('   • WATSONX_REGION=us-south (optional)')
        print('   System will use enhanced fallback mode until configured.')
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )