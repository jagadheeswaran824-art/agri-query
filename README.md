# 🌾 KrishiSahay - AI Agricultural Assistant

An AI-Powered Agricultural Helpdesk using IBM Watsonx Granite LLM and FAISS

## Overview

KrishiSahay is an intelligent agricultural query resolution system built for rural support and information dissemination. It leverages AI capabilities including IBM Watsonx Granite LLM and semantic vector search (FAISS) to answer farmers' queries related to crop diseases, pest control, fertilizer usage, and government schemes.

## 🎨 Unique Features

- **Modern UI/UX**: Beautiful gradient design with animated backgrounds
- **Dual Mode Operation**: Toggle between offline (FAISS) and online (AI-enhanced) modes
- **Voice Input**: Speak your questions using voice recognition
- **Real-time Chat**: Interactive chat interface with typing indicators
- **Smart Suggestions**: Quick access to common agricultural queries
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Offline Support**: Ensures continuous access even in low-connectivity environments

## Technical Architecture

### Components

1. **Data Preprocessing**: Cleans and prepares KCC dataset
2. **Embedding Generation**: Creates vector embeddings using Sentence Transformers
3. **FAISS Index**: Enables fast semantic similarity search
4. **Query Handler**: Processes user queries and retrieves relevant information
5. **Granite LLM Integration**: Generates AI-enhanced responses
6. **Streamlit UI**: Provides interactive user interface

## Prerequisites

- Python 3.9+
- IBM Cloud account with Watsonx enabled (for online mode)
- pip package manager

## 🚀 Quick Start

### Frontend (Web Interface)

1. Install Node.js dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

3. Open browser and navigate to:
```
http://localhost:3000
```

### Backend (Python - Optional for Full AI Features)

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure IBM Watsonx credentials in `.env`:
```
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
```

3. Run setup scripts:
```bash
python setup.py
```

4. Start Streamlit app (alternative interface):
```bash
streamlit run app.py
```

## 💡 Usage

1. **Choose Mode**: Toggle between Offline and Online mode
2. **Ask Questions**: Type or speak your agricultural query
3. **Get Answers**: Receive instant responses from the AI
4. **Quick Suggestions**: Click on suggested questions for common queries
5. **Clear Chat**: Start fresh conversations anytime

## Sample Queries

- How to control aphids in mustard?
- What is the treatment for leaf spot in tomato?
- Suggest pesticide for whitefly in cotton
- How to apply for PM Kisan Samman Nidhi scheme?
- What is the dosage of neem oil for aphids?

## Project Structure

```
kri0shisahay/
├── 🎨 frontend/                          # Modern Web Interface
│   ├── public/
│   │   ├── index.html                    # Dynamic UI with animations
│   │   ├── styles.css                    # Unique gradient design
│   │   └── script.js                     # Interactive functionality
│   ├── server.js                         # Express API server
│   └── package.json                      # Node.js dependencies
│
├── 🧠 ai-backend/                        # Python AI Services
│   ├── app.py                            # Streamlit dashboard
│   ├── query_handler.py                  # FAISS query processing
│   ├── granite_llm.py                    # IBM Watsonx integration
│   ├── data_preprocessing.py             # Data cleaning pipeline
│   ├── generate_embeddings.py            # Vector generation
│   ├── create_faiss_index.py             # Index building
│   ├── setup.py                          # Automated setup
│   └── requirements.txt                  # Python dependencies
│
├── 📊 data/                              # Data Storage Layer
│   ├── raw_kcc.csv                       # Original dataset
│   ├── clean_kcc.csv                     # Cleaned dataset
│   ├── kcc_qa_pairs.json                 # Structured Q&A
│   ├── kcc_embeddings.pkl                # Vector representations
│   ├── faiss_index.bin                   # FAISS binary index
│   └── meta.pkl                          # Index metadata
│
├── 📚 docs/                              # Comprehensive Documentation
│   ├── ARCHITECTURE.md                   # Technical architecture
│   ├── DATA_PIPELINE.md                  # Processing pipeline
│   ├── DEPLOYMENT_GUIDE.md               # Deployment instructions
│   └── AI_COMPONENTS.md                  # AI system details
│
├── .env                                  # Environment configuration
├── README.md                             # Project overview
└── .gitignore                            # Git ignore rules
```

## 📋 Documentation

- **[Technical Architecture](ARCHITECTURE.md)** - Comprehensive system architecture
- **[Data Processing Pipeline](DATA_PIPELINE.md)** - Detailed pipeline documentation  
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[AI Components](AI_COMPONENTS.md)** - Dynamic AI system details

## 🔧 Advanced Features

- **Multi-Agent AI System**: Specialized agents for different agricultural domains
- **Dynamic Query Understanding**: Context-aware query processing
- **Continuous Learning**: System improves from user interactions
- **Multi-Modal Support**: Text, voice, and image input processing
- **Predictive Analytics**: Weather, pest, and yield predictions
- **Real-Time Adaptation**: Dynamic model selection and optimization

## License

MIT License

## Contact

For questions or support, please contact the development team.
