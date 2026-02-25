"""
Step 4: Semantic Query Handling
Handle user queries using FAISS similarity search
"""
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class QueryHandler:
    def __init__(self, 
                 index_file='data/faiss_index.bin',
                 meta_file='data/meta.pkl',
                 model_name='all-MiniLM-L6-v2'):
        """
        Initialize query handler with FAISS index and metadata
        """
        print("🔄 Loading FAISS index...")
        self.index = faiss.read_index(index_file)
        
        print("📂 Loading metadata...")
        with open(meta_file, 'rb') as f:
            self.qa_pairs = pickle.load(f)
        
        print("🔄 Loading Sentence Transformer model...")
        self.model = SentenceTransformer(model_name)
        
        print("✅ Query handler initialized!")
    
    def search(self, query, top_k=5):
        """
        Search for similar Q&A pairs
        """
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Retrieve results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.qa_pairs):
                result = self.qa_pairs[idx].copy()
                result['distance'] = float(dist)
                result['similarity'] = float(1 / (1 + dist))  # Convert distance to similarity
                results.append(result)
        
        return results
    
    def format_offline_answer(self, results):
        """
        Format retrieved results as offline answer
        """
        if not results:
            return "No relevant information found in the database."
        
        # Get unique answers
        unique_answers = []
        seen = set()
        
        for result in results:
            answer = result['answer']
            if answer not in seen:
                unique_answers.append(answer)
                seen.add(answer)
        
        # Format as numbered list
        formatted = "📚 Based on Kisan Call Centre Database:\n\n"
        for i, answer in enumerate(unique_answers[:3], 1):
            formatted += f"{i}. {answer}\n\n"
        
        return formatted.strip()
    
    def create_context_prompt(self, query, results):
        """
        Create context prompt for LLM
        """
        context = "Relevant information from Kisan Call Centre database:\n\n"
        
        for i, result in enumerate(results[:3], 1):
            context += f"Q: {result['question']}\n"
            context += f"A: {result['answer']}\n\n"
        
        prompt = f"""You are an expert agricultural assistant helping Indian farmers. 
Use the following information from the Kisan Call Centre database to answer the farmer's question.

{context}

Farmer's Question: {query}

Provide a clear, practical answer in simple language. Include specific recommendations, dosages, or steps when applicable."""

        return prompt

if __name__ == "__main__":
    # Test query handler
    handler = QueryHandler()
    
    test_query = "How to control aphids in mustard?"
    print(f"\n🔍 Testing query: {test_query}")
    
    results = handler.search(test_query, top_k=3)
    print(f"\n✅ Found {len(results)} results")
    
    offline_answer = handler.format_offline_answer(results)
    print(f"\n📝 Offline Answer:\n{offline_answer}")
