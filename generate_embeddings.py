"""
Step 2: Embedding Generation
Generate vector embeddings using Sentence Transformers
"""
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import os

def generate_embeddings(json_file='data/kcc_qa_pairs.json', output_file='data/kcc_embeddings.pkl', model_name='all-MiniLM-L6-v2'):
    """
    Generate embeddings for all Q&A pairs
    """
    print("🔄 Loading Sentence Transformer model...")
    model = SentenceTransformer(model_name)
    
    print("📂 Loading Q&A pairs...")
    with open(json_file, 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)
    
    print(f"🧮 Generating embeddings for {len(qa_pairs)} entries...")
    
    # Combine question and answer for better semantic representation
    texts = [f"{qa['question']} {qa['answer']}" for qa in qa_pairs]
    
    # Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    print(f"✅ Generated embeddings shape: {embeddings.shape}")
    
    # Save embeddings
    with open(output_file, 'wb') as f:
        pickle.dump({
            'embeddings': embeddings,
            'qa_pairs': qa_pairs
        }, f)
    
    print(f"💾 Saved embeddings to: {output_file}")
    return embeddings, qa_pairs

if __name__ == "__main__":
    generate_embeddings()
    print("✅ Embedding generation completed!")
