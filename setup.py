"""
Complete Setup Script
Runs all preprocessing steps in sequence
"""
import os
import sys

def run_setup():
    """
    Run all setup steps
    """
    print("=" * 60)
    print("🌾 Kisan Call Centre Query Assistant - Setup")
    print("=" * 60)
    
    steps = [
        ("Step 1: Data Preprocessing", "data_preprocessing.py"),
        ("Step 2: Generate Embeddings", "generate_embeddings.py"),
        ("Step 3: Create FAISS Index", "create_faiss_index.py")
    ]
    
    for step_name, script in steps:
        print(f"\n{'=' * 60}")
        print(f"🔄 {step_name}")
        print(f"{'=' * 60}\n")
        
        try:
            exec(open(script).read())
        except Exception as e:
            print(f"❌ Error in {step_name}: {str(e)}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print("\n🚀 Run the application with: streamlit run app.py")

if __name__ == "__main__":
    run_setup()
