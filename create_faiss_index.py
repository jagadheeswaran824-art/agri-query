"""
Step 3: FAISS Vector Store Creation
Create FAISS index for fast similarity search
"""
import pickle
import faiss
import numpy as np
import os

def create_faiss_index(embeddings_file='data/kcc_embeddings.pkl', 
                       index_file='data/faiss_index.bin',
                       meta_file='data/meta.pkl'):
    """
    Create and save FAISS index
    """
    print("📂 Loading embeddings...")
    with open(embeddings_file, 'rb') as f:
        data = pickle.load(f)
    
    embeddings = data['embeddings']
    qa_pairs = data['qa_pairs']
    
    print(f"📊 Embeddings shape: {embeddings.shape}")
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    print(f"🔧 Creating FAISS index with dimension: {dimension}")
    
    # Using IndexFlatL2 for exact search (can be changed to IndexIVFFlat for larger datasets)
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to index
    index.add(embeddings.astype('float32'))
    
    print(f"✅ FAISS index created with {index.ntotal} vectors")
    
    # Save FAISS index
    faiss.write_index(index, index_file)
    print(f"💾 Saved FAISS index to: {index_file}")
    
    # Save metadata
    with open(meta_file, 'wb') as f:
        pickle.dump(qa_pairs, f)
    print(f"💾 Saved metadata to: {meta_file}")
    
    return index, qa_pairs

if __name__ == "__main__":
    create_faiss_index()
    print("✅ FAISS index creation completed!")
