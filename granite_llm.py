"""
Step 5: Granite LLM Integration
Connect to IBM Watsonx Granite LLM for online mode
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class GraniteLLM:
    def __init__(self):
        """
        Initialize IBM Watsonx Granite LLM client
        """
        self.api_key = os.getenv('WATSONX_API_KEY')
        self.project_id = os.getenv('WATSONX_PROJECT_ID')
        self.url = os.getenv('WATSONX_URL', 'https://eu-de.ml.cloud.ibm.com')
        self.model_id = os.getenv('MODEL_ID', 'ibm/granite-3-8b-instruct')
        
        if not self.api_key or not self.project_id:
            print("⚠️ Warning: IBM Watsonx credentials not configured")
            self.enabled = False
        else:
            self.enabled = True
            print("✅ Granite LLM initialized")
    
    def generate_answer(self, prompt, max_tokens=500, temperature=0.7):
        """
        Generate answer using IBM Watsonx Granite LLM
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'IBM Watsonx credentials not configured. Please set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env file.'
            }
        
        try:
            # IBM Watsonx API endpoint
            endpoint = f"{self.url}/ml/v1/text/generation?version=2023-05-29"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "stop_sequences": ["\n\n\n"]
                },
                "model_id": self.model_id,
                "project_id": self.project_id
            }
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('results', [{}])[0].get('generated_text', '')
                
                return {
                    'success': True,
                    'answer': generated_text.strip(),
                    'model': self.model_id
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text}"
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Exception: {str(e)}"
            }
    
    def get_mock_answer(self, prompt):
        """
        Generate mock answer for testing without API
        """
        return {
            'success': True,
            'answer': """Based on the Kisan Call Centre database, here are the recommendations:

For controlling aphids in mustard crops:
- Spray neem oil solution at 5ml per liter of water
- Alternatively, use imidacloprid 17.8% SL at 0.5ml per liter
- Apply during early morning or evening hours for best results
- Repeat application after 7-10 days if infestation persists

Additional tips:
- Monitor crops regularly for early detection
- Remove heavily infested plant parts
- Maintain proper field sanitation""",
            'model': 'mock-model (API not configured)'
        }

if __name__ == "__main__":
    # Test Granite LLM
    llm = GraniteLLM()
    
    test_prompt = "How to control aphids in mustard crops?"
    print(f"\n🔍 Testing prompt: {test_prompt}")
    
    if llm.enabled:
        result = llm.generate_answer(test_prompt)
    else:
        result = llm.get_mock_answer(test_prompt)
    
    if result['success']:
        print(f"\n✅ Generated Answer:\n{result['answer']}")
    else:
        print(f"\n❌ Error: {result['error']}")
