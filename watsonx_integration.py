#!/usr/bin/env python3
"""
IBM Watsonx Granite LLM Integration for KrishiSahay
Real-time AI response generation using IBM Watsonx API
"""

import os
import json
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WatsonxGraniteAI:
    """IBM Watsonx Granite LLM Integration"""
    
    def __init__(self):
        self.api_key = os.environ.get('WATSONX_API_KEY', '')
        self.project_id = os.environ.get('WATSONX_PROJECT_ID', '')
        self.region = os.environ.get('WATSONX_REGION', 'us-south')
        self.model_id = 'ibm/granite-3-8b-instruct'
        
        # API Configuration
        self.base_url = f"https://{self.region}.ml.cloud.ibm.com"
        self.api_version = "2023-05-29"
        
        # Authentication
        self.access_token = None
        self.token_expiry = None
        
        # Model Parameters
        self.default_params = {
            'max_new_tokens': 1000,
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 50,
            'repetition_penalty': 1.1,
            'stop_sequences': ['Human:', 'User:', '\n\nHuman:', '\n\nUser:']
        }
        
        # Response cache
        self.response_cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        # Check if API key is available
        self.is_available = bool(self.api_key and self.project_id)
        
        if self.is_available:
            logger.info("✅ IBM Watsonx API configured")
        else:
            logger.warning("⚠️  IBM Watsonx API key not found - using fallback mode")
    
    def authenticate(self) -> Optional[str]:
        """Authenticate with IBM Cloud IAM"""
        if not self.is_available:
            return None
        
        # Check if token is still valid
        if self.access_token and self.token_expiry:
            if datetime.now() < self.token_expiry:
                return self.access_token
        
        try:
            auth_url = "https://iam.cloud.ibm.com/identity/token"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
                'apikey': self.api_key
            }
            
            response = requests.post(auth_url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                auth_data = response.json()
                self.access_token = auth_data['access_token']
                expires_in = auth_data.get('expires_in', 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
                
                logger.info("✅ IBM Watsonx authentication successful")
                return self.access_token
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return None
    
    def generate_response(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Generate AI response using IBM Watsonx Granite LLM"""
        
        # Check cache first
        cache_key = self._get_cache_key(query, context)
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if datetime.now() < cached['expiry']:
                logger.info("📋 Returning cached Watsonx response")
                return cached['response']
        
        # If API not available, return fallback
        if not self.is_available:
            return self._generate_fallback_response(query, context)
        
        # Authenticate
        token = self.authenticate()
        if not token:
            return self._generate_fallback_response(query, context)
        
        try:
            # Build enhanced prompt
            prompt = self._build_prompt(query, context)
            
            # Prepare API request
            url = f"{self.base_url}/ml/v1/text/generation?version={self.api_version}"
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            payload = {
                'model_id': self.model_id,
                'input': prompt,
                'parameters': self.default_params,
                'project_id': self.project_id
            }
            
            logger.info(f"🤖 Generating Watsonx response for: {query[:50]}...")
            
            # Make API request
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'results' in result and len(result['results']) > 0:
                    generated_text = result['results'][0]['generated_text']
                    tokens_used = result['results'][0].get('generated_token_count', 0)
                    
                    ai_response = {
                        'answer': self._post_process_response(generated_text),
                        'confidence': 0.92,
                        'source': 'IBM Watsonx Granite LLM',
                        'model': self.model_id,
                        'tokens_used': tokens_used,
                        'timestamp': datetime.now().isoformat(),
                        'cached': False
                    }
                    
                    # Cache the response
                    self.response_cache[cache_key] = {
                        'response': ai_response,
                        'expiry': datetime.now() + timedelta(seconds=self.cache_ttl)
                    }
                    
                    logger.info(f"✅ Watsonx response generated ({tokens_used} tokens)")
                    return ai_response
                else:
                    logger.error("❌ Invalid Watsonx response format")
                    return self._generate_fallback_response(query, context)
            else:
                logger.error(f"❌ Watsonx API error: {response.status_code}")
                return self._generate_fallback_response(query, context)
                
        except requests.Timeout:
            logger.error("❌ Watsonx API timeout")
            return self._generate_fallback_response(query, context)
        except Exception as e:
            logger.error(f"❌ Watsonx generation error: {e}")
            return self._generate_fallback_response(query, context)
    
    def _build_prompt(self, query: str, context: Dict = None) -> str:
        """Build enhanced prompt for Watsonx"""
        
        # System prompt
        system_prompt = """You are an expert agricultural advisor specializing in Indian farming practices. 
You provide practical, science-based solutions for farmers. Your responses should be:
- Clear and actionable
- Specific to Indian agricultural conditions
- Include both organic and chemical solutions when applicable
- Mention proper dosages and timing
- Consider local resources and farmer constraints"""
        
        # Add context if available
        context_info = ""
        if context:
            if 'search_results' in context:
                context_info += "\n\nRelevant Information from Knowledge Base:\n"
                for result in context['search_results'][:3]:
                    if 'data' in result and isinstance(result['data'], dict):
                        data = result['data']
                        context_info += f"\n**{result['key'].upper()}**:\n"
                        if 'solution' in data:
                            context_info += f"Solution: {data['solution']}\n"
                        if 'symptoms' in data:
                            context_info += f"Symptoms: {', '.join(data['symptoms'])}\n"
            
            if 'location' in context:
                context_info += f"\nUser Location: {context['location']}\n"
            
            if 'previous_queries' in context and context['previous_queries']:
                context_info += f"\nPrevious Query: {context['previous_queries'][-1]}\n"
        
        # Build complete prompt
        prompt = f"""{system_prompt}

{context_info}

Farmer's Question: {query}

Please provide a comprehensive, practical answer with:
1. Immediate action steps
2. Detailed solution with dosages
3. Prevention measures
4. Alternative methods (organic and chemical)
5. Important precautions

Response:"""
        
        return prompt
    
    def _post_process_response(self, text: str) -> str:
        """Clean and format the AI response"""
        # Remove any unwanted prefixes
        text = text.strip()
        
        # Remove common AI response prefixes
        prefixes = ['Response:', 'Answer:', 'AI:', 'Assistant:', 'Here is', 'Here\'s']
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Add formatting
        text = text.replace('\n\n', '\n\n')  # Normalize line breaks
        
        # Add emoji headers if not present
        if not text.startswith('🤖'):
            text = f"🤖 **IBM Watsonx Granite AI Response:**\n\n{text}"
        
        return text
    
    def _generate_fallback_response(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Generate fallback response when Watsonx is unavailable"""
        
        fallback_text = f"""**Agricultural Guidance** (Offline Mode)

I understand you're asking about: "{query}"

"""
        
        # Add context-based information if available
        if context and 'search_results' in context and context['search_results']:
            result = context['search_results'][0]
            if 'data' in result and isinstance(result['data'], dict):
                data = result['data']
                
                fallback_text += f"**Based on our knowledge base:**\n\n"
                
                if 'solution' in data:
                    fallback_text += f"**Solution:**\n{data['solution']}\n\n"
                
                if 'symptoms' in data:
                    fallback_text += f"**Symptoms:**\n"
                    for symptom in data['symptoms'][:5]:
                        fallback_text += f"• {symptom.capitalize()}\n"
                    fallback_text += "\n"
                
                if 'prevention' in data:
                    fallback_text += f"**Prevention:**\n"
                    for prevention in data['prevention'][:5]:
                        fallback_text += f"• {prevention.capitalize()}\n"
                    fallback_text += "\n"
        else:
            fallback_text += """**General Recommendations:**
• Consult with local agricultural extension officers
• Conduct soil and crop health assessments
• Follow integrated pest and disease management
• Maintain proper irrigation and drainage
• Use recommended fertilizers based on soil tests

For AI-enhanced responses, please configure IBM Watsonx API credentials."""
        
        return {
            'answer': fallback_text,
            'confidence': 0.75,
            'source': 'Knowledge Base (Fallback)',
            'model': 'offline',
            'tokens_used': 0,
            'timestamp': datetime.now().isoformat(),
            'cached': False
        }
    
    def _get_cache_key(self, query: str, context: Dict = None) -> str:
        """Generate cache key for response"""
        key_parts = [query.lower().strip()]
        
        if context:
            if 'location' in context:
                key_parts.append(context['location'])
            if 'crop' in context:
                key_parts.append(context['crop'])
        
        return '|'.join(key_parts)
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("🧹 Watsonx response cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Watsonx integration statistics"""
        return {
            'is_available': self.is_available,
            'model': self.model_id,
            'region': self.region,
            'cache_size': len(self.response_cache),
            'authenticated': bool(self.access_token),
            'token_valid': bool(self.token_expiry and datetime.now() < self.token_expiry)
        }