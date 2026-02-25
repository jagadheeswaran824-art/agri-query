# 🚀 KrishiSahay Quick Start Guide

## Get Started in 3 Steps!

### Step 1: Start the Backend Server

**Option A: Windows (Easiest)**
```bash
# Double-click this file:
start_backend.bat
```

**Option B: Command Line**
```bash
python flask_backend.py
```

### Step 2: Open Your Browser
```
http://localhost:5000
```

### Step 3: Start Chatting!
Type any agricultural question like:
- "How to control aphids in mustard?"
- "Best fertilizer for wheat crop?"
- "PM Kisan scheme application process"

## ✅ System Status

Your backend server is currently **RUNNING** on:
- **URL**: http://localhost:5000
- **WebSocket**: ✅ Enabled
- **AI Search Engine**: ✅ Active
- **Real-time Chat**: ✅ Ready

## 🧪 Test the System

### Quick Test
Open: http://localhost:5000/test_backend.html

Click the test buttons to verify:
- ✅ Health Check
- ✅ Query Processing
- ✅ WebSocket Connection
- ✅ AI Search Engine

## 📱 Features Available

### 1. Real-Time Chat
- Instant AI responses
- Typing indicators
- Follow-up suggestions
- Conversation history

### 2. AI Search Engine
- Intelligent query understanding
- Context-aware responses
- Multi-source knowledge
- Trending queries

### 3. Multi-Modal Input
- 🎤 Voice input (click microphone)
- 📷 Image upload (click camera)
- 📍 Location services (click location)
- ⌨️ Text input (type your question)

### 4. Advanced Features
- Smart suggestions
- Related topics
- Expert recommendations
- Government scheme info

## 💡 Example Queries

### Pest Control
```
"How to control aphids in mustard?"
"Organic pest control methods"
"Best pesticide for whitefly"
```

### Disease Management
```
"Treatment for leaf spot in tomato"
"How to prevent blight disease"
"Fungal infection in crops"
```

### Fertilizer Guidance
```
"Best fertilizer for wheat flowering"
"NPK ratio for rice crop"
"Organic fertilizer recommendations"
```

### Government Schemes
```
"PM Kisan scheme application"
"Agricultural loan process"
"Crop insurance details"
```

## 🔧 API Endpoints

### REST API
```bash
# Health Check
curl http://localhost:5000/api/health

# Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"How to control aphids?","mode":"online"}'

# Search
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"pest control"}'

# Trending
curl http://localhost:5000/api/trending

# Statistics
curl http://localhost:5000/api/search-stats
```

### WebSocket
```javascript
// Connect
const socket = io('http://localhost:5000');

// Join session
socket.emit('join-session', 'my_session_id');

// Send message
socket.emit('chat-message', {
  sessionId: 'my_session_id',
  message: 'How to control aphids?'
});

// Receive response
socket.on('ai-response', (response) => {
  console.log(response);
});
```

## 📊 Monitor Performance

### Live Statistics
```
http://localhost:5000/api/analytics
```

Shows:
- Total queries processed
- Average response time
- Active users
- Error rate

### Search Statistics
```
http://localhost:5000/api/search-stats
```

Shows:
- Total searches
- Trending queries
- Popular topics

## 🛠️ Troubleshooting

### Server Not Starting?
```bash
# Install dependencies
pip install Flask Flask-CORS Flask-SocketIO

# Try again
python flask_backend.py
```

### Can't Connect?
1. Check if server is running
2. Verify port 5000 is not blocked
3. Try http://127.0.0.1:5000 instead

### No Responses?
1. Check browser console for errors
2. Verify WebSocket connection
3. Test with: http://localhost:5000/test_backend.html

## 📚 Documentation

- **Full Guide**: AI_SEARCH_ENGINE_GUIDE.md
- **Backend README**: BACKEND_README.md
- **Architecture**: ARCHITECTURE.md
- **API Docs**: Check /api/health for endpoint list

## 🎯 Next Steps

1. ✅ Server is running
2. ✅ Test the interface
3. ✅ Try different queries
4. ✅ Explore advanced features
5. ✅ Check analytics
6. ✅ Review documentation

## 💬 Need Help?

- **Test Page**: http://localhost:5000/test_backend.html
- **Health Check**: http://localhost:5000/api/health
- **Logs**: Check `logs/backend.log`
- **Status**: http://localhost:5000/api/status

---

**You're all set! Start asking agricultural questions now! 🌾**