"""
Step 6: Streamlit UI
Main application interface for Kisan Call Centre Query Assistant
"""
import streamlit as st
import os
import time
from query_handler import QueryHandler
from granite_llm import GraniteLLM

# Page configuration
st.set_page_config(
    page_title="KrishiSahay - AI Agricultural Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with unique modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        animation: fadeInDown 0.8s ease-out;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 300;
    }
    
    .stats-container {
        display: flex;
        ju

# Initialize session state
if 'query_handler' not in st.session_state:
    with st.spinner("🔄 Initializing system..."):
        try:
            st.session_state.query_handler = QueryHandler()
            st.session_state.granite_llm = GraniteLLM()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"❌ Initialization failed: {str(e)}")
            st.info("💡 Please run setup scripts first: python data_preprocessing.py && python generate_embeddings.py && python create_faiss_index.py")
            st.session_state.initialized = False

# Header
st.markdown("""
<div class="main-header">
    <h1>🌾 Kisan Call Centre Query Assistant</h1>
    <p>AI-Powered Agricultural Helpdesk using IBM Watsonx Granite LLM and FAISS</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    online_mode = st.checkbox("Enable Online Mode (Granite LLM)", value=True)
    top_k = st.slider("Number of similar results", 1, 10, 5)
    
    st.markdown("---")
    st.header("📊 System Info")
    
    if st.session_state.get('initialized'):
        st.success("✅ FAISS Index: Loaded")
        st.success("✅ Query Handler: Ready")
        
        if st.session_state.granite_llm.enabled:
            st.success("✅ Granite LLM: Connected")
        else:
            st.warning("⚠️ Granite LLM: Not configured")
    else:
        st.error("❌ System not initialized")
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.info("""
    This system uses:
    - **FAISS** for semantic search
    - **Sentence Transformers** for embeddings
    - **IBM Watsonx Granite LLM** for intelligent responses
    
    Built for rural agricultural support.
    """)

# Main content
if not st.session_state.get('initialized'):
    st.stop()

# Sample queries
st.subheader("💡 Sample Queries")
sample_queries = [
    "How to control aphids in mustard?",
    "What is the treatment for leaf spot in tomato?",
    "Suggest pesticide for whitefly in cotton.",
    "How to prevent fruit borer in brinjal?",
    "What fertilizer is recommended during flowering in maize?",
    "How to protect paddy from blast disease?",
    "How to apply for PM Kisan Samman Nidhi scheme?",
    "What is the dosage of neem oil for aphids?",
    "How to treat blight in potato crops?"
]

cols = st.columns(3)
for idx, query in enumerate(sample_queries[:6]):
    with cols[idx % 3]:
        if st.button(query, key=f"sample_{idx}", use_container_width=True):
            st.session_state.selected_query = query

# Query input
st.subheader("🔍 Ask Your Question")
user_query = st.text_area(
    "Enter your agricultural query:",
    value=st.session_state.get('selected_query', ''),
    height=100,
    placeholder="Example: How to control pests in my wheat crop?"
)

if st.button("🚀 Get Answer", type="primary", use_container_width=True):
    if not user_query.strip():
        st.warning("⚠️ Please enter a question")
    else:
        with st.spinner("🔄 Processing your query..."):
            # Step 1: FAISS Search
            results = st.session_state.query_handler.search(user_query, top_k=top_k)
            
            # Step 2: Format offline answer
            offline_answer = st.session_state.query_handler.format_offline_answer(results)
            
            # Display offline answer
            st.markdown("### 📚 Offline Answer (FAISS Database)")
            st.markdown(f'<div class="answer-box offline-answer">{offline_answer}</div>', unsafe_allow_html=True)
            
            # Step 3: Generate online answer if enabled
            if online_mode:
                with st.spinner("🤖 Generating AI-enhanced answer..."):
                    prompt = st.session_state.query_handler.create_context_prompt(user_query, results)
                    
                    if st.session_state.granite_llm.enabled:
                        llm_result = st.session_state.granite_llm.generate_answer(prompt)
                    else:
                        llm_result = st.session_state.granite_llm.get_mock_answer(prompt)
                    
                    st.markdown("### 🤖 Online Answer (Granite LLM)")
                    
                    if llm_result['success']:
                        st.markdown(f'<div class="answer-box online-answer">{llm_result["answer"]}</div>', unsafe_allow_html=True)
                        st.caption(f"Model: {llm_result['model']}")
                    else:
                        st.error(f"❌ {llm_result['error']}")
            
            # Show retrieved context
            with st.expander("📖 View Retrieved Context"):
                for i, result in enumerate(results, 1):
                    st.markdown(f"**{i}. Q:** {result['question']}")
                    st.markdown(f"**A:** {result['answer']}")
                    st.caption(f"Similarity: {result['similarity']:.3f}")
                    st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🌾 Kisan Call Centre Query Assistant | Powered by IBM Watsonx Granite LLM & FAISS</p>
    <p>Empowering Indian Farmers with AI-driven Agricultural Knowledge</p>
</div>
""", unsafe_allow_html=True)
