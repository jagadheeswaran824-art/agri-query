"""
Test script to verify system functionality
"""
import os

def test_system():
    """
    Test all components
    """
    print("=" * 60)
    print("🧪 Testing Kisan Call Centre Query Assistant")
    print("=" * 60)
    
    # Test 1: Check data files
    print("\n1️⃣ Checking data files...")
    data_files = [
        'data/clean_kcc.csv',
        'data/kcc_qa_pairs.json',
        'data/kcc_embeddings.pkl',
        'data/faiss_index.bin',
        'data/meta.pkl'
    ]
    
    for file in data_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - Missing!")
    
    # Test 2: Query Handler
    print("\n2️⃣ Testing Query Handler...")
    try:
        from query_handler import QueryHandler
        handler = QueryHandler()
        
        test_query = "How to control aphids?"
        results = handler.search(test_query, top_k=3)
        print(f"   ✅ Query search working - Found {len(results)} results")
        
        offline_answer = handler.format_offline_answer(results)
        print(f"   ✅ Offline answer generation working")
    except Exception as e:
        print(f"   ❌ Query Handler error: {str(e)}")
    
    # Test 3: Granite LLM
    print("\n3️⃣ Testing Granite LLM...")
    try:
        from granite_llm import GraniteLLM
        llm = GraniteLLM()
        
        if llm.enabled:
            print("   ✅ Granite LLM configured")
        else:
            print("   ⚠️  Granite LLM not configured (will use mock mode)")
    except Exception as e:
        print(f"   ❌ Granite LLM error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ System test completed!")
    print("=" * 60)
    print("\n🚀 Run the application: streamlit run app.py")

if __name__ == "__main__":
    test_system()
