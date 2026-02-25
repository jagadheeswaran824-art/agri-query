"""
Step 1: Data Preprocessing
Cleans and prepares the Kisan Call Centre dataset
"""
import pandas as pd
import json
import os

def preprocess_kcc_data(input_file='data/raw_kcc.csv', output_csv='data/clean_kcc.csv', output_json='data/kcc_qa_pairs.json'):
    """
    Load, clean, and save KCC dataset
    """
    print("📂 Loading raw KCC data...")
    
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print("⚠️ Raw data file not found. Creating sample dataset...")
        # Create sample data for demonstration
        sample_data = {
            'question': [
                'How to control aphids in mustard?',
                'What is the treatment for leaf spot in tomato?',
                'Suggest pesticide for whitefly in cotton.',
                'How to prevent fruit borer in brinjal?',
                'What fertilizer is recommended during flowering in maize?',
                'How to protect paddy from blast disease?',
                'What is the solution for jassids in cotton?',
                'How to apply for PM Kisan Samman Nidhi scheme?',
                'What is the dosage of neem oil for aphids?',
                'How to treat blight in potato crops?'
            ],
            'answer': [
                'Spray neem oil solution (5ml per liter) or use imidacloprid 17.8% SL @ 0.5ml/liter. Apply during early morning or evening.',
                'Remove infected leaves. Spray mancozeb 75% WP @ 2g/liter or copper oxychloride @ 3g/liter at 10-day intervals.',
                'Use thiamethoxam 25% WG @ 0.2g/liter or spray neem-based pesticides. Ensure coverage on leaf undersides.',
                'Install pheromone traps. Spray spinosad 45% SC @ 0.3ml/liter or use Bacillus thuringiensis.',
                'Apply DAP (Diammonium Phosphate) @ 50kg/acre during flowering. Supplement with potash for better yield.',
                'Use tricyclazole 75% WP @ 0.6g/liter or carbendazim 50% WP @ 1g/liter. Maintain proper water management.',
                'Spray dimethoate 30% EC @ 2ml/liter or thiamethoxam. Remove and destroy affected plant parts.',
                'Visit PM Kisan portal (pmkisan.gov.in), register with Aadhaar, land records, and bank details. Contact local agriculture office.',
                'Mix 5ml neem oil per liter of water. Add 1ml liquid soap as emulsifier. Spray on affected plants every 7 days.',
                'Remove infected plants. Spray metalaxyl + mancozeb @ 2.5g/liter. Avoid overhead irrigation and ensure proper drainage.'
            ]
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(input_file, index=False)
        print("✅ Sample dataset created")
    
    print(f"📊 Original dataset size: {len(df)} records")
    
    # Clean data
    df = df.dropna(subset=['question', 'answer'])
    df = df.drop_duplicates(subset=['question'])
    df['question'] = df['question'].str.strip()
    df['answer'] = df['answer'].str.strip()
    
    print(f"✨ Cleaned dataset size: {len(df)} records")
    
    # Save cleaned CSV
    df.to_csv(output_csv, index=False)
    print(f"💾 Saved cleaned CSV: {output_csv}")
    
    # Save as JSON
    qa_pairs = df.to_dict('records')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved JSON: {output_json}")
    
    return df

if __name__ == "__main__":
    preprocess_kcc_data()
    print("✅ Data preprocessing completed!")
