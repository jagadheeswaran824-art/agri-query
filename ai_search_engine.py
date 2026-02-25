#!/usr/bin/env python3
"""
KrishiSahay AI Search Engine
Real-time intelligent search with context awareness and multi-source integration
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict
import difflib

class AISearchEngine:
    """Advanced AI-powered search engine for agricultural queries"""
    
    def __init__(self):
        self.search_history = []
        self.context_memory = defaultdict(list)
        self.search_index = {}
        self.query_patterns = self._load_query_patterns()
        self.synonyms = self._load_synonyms()
        self.search_stats = {
            'total_searches': 0,
            'avg_results': 0,
            'popular_queries': []
        }
        
    def _load_query_patterns(self):
        """Load common query patterns for better understanding"""
        return {
            'pest_control': [
                r'\b(control|kill|remove|eliminate|manage)\b.*\b(pest|insect|bug|aphid|whitefly)\b',
                r'\b(aphid|whitefly|thrips|mite|borer|caterpillar)\b.*\b(control|treatment|solution)\b'
            ],
            'disease_management': [
                r'\b(disease|infection|fungus|virus|bacterial)\b.*\b(treatment|cure|control)\b',
                r'\b(blight|spot|rot|wilt|mildew)\b.*\b(manage|treat|prevent)\b'
            ],
            'fertilizer': [
                r'\b(fertilizer|nutrient|npk|urea|dap)\b.*\b(apply|use|recommend)\b',
                r'\b(nitrogen|phosphorus|potassium)\b.*\b(deficiency|requirement)\b'
            ],
            'crop_management': [
                r'\b(grow|cultivate|plant)\b.*\b(crop|vegetable|grain)\b',
                r'\b(irrigation|watering|drainage)\b.*\b(method|system|schedule)\b'
            ],
            'government_schemes': [
                r'\b(scheme|subsidy|loan|insurance|policy)\b.*\b(farmer|agriculture)\b',
                r'\b(pm kisan|pradhan mantri|government)\b.*\b(benefit|apply|register)\b'
            ]
        }
    
    def _load_synonyms(self):
        """Load agricultural term synonyms for better search"""
        return {
            'pest': ['insect', 'bug', 'parasite', 'infestation'],
            'disease': ['infection', 'sickness', 'ailment', 'disorder'],
            'fertilizer': ['nutrient', 'manure', 'compost', 'feed'],
            'crop': ['plant', 'vegetation', 'produce', 'harvest'],
            'control': ['manage', 'eliminate', 'remove', 'treat'],
            'organic': ['natural', 'bio', 'eco-friendly', 'chemical-free'],
            'yield': ['production', 'output', 'harvest', 'productivity']
        }
    
    def search(self, query: str, knowledge_base: Dict, context: Dict = None) -> Dict[str, Any]:
        """
        Perform intelligent search with context awareness
        """
        self.search_stats['total_searches'] += 1
        
        # Preprocess query
        processed_query = self._preprocess_query(query)
        
        # Extract search intent
        intent = self._extract_intent(processed_query)
        
        # Expand query with synonyms
        expanded_query = self._expand_query(processed_query)
        
        # Search knowledge base
        results = self._search_knowledge_base(expanded_query, knowledge_base)
        
        # Rank results
        ranked_results = self._rank_results(results, processed_query, intent)
        
        # Add context if available
        if context:
            ranked_results = self._apply_context(ranked_results, context)
        
        # Store search history
        self._update_search_history(query, ranked_results)
        
        return {
            'query': query,
            'processed_query': processed_query,
            'intent': intent,
            'results': ranked_results[:10],  # Top 10 results
            'total_results': len(ranked_results),
            'search_time': datetime.now().isoformat(),
            'suggestions': self._generate_suggestions(query, ranked_results)
        }
    
    def _preprocess_query(self, query: str) -> str:
        """Clean and normalize query"""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        
        # Remove special characters but keep important ones
        query = re.sub(r'[^\w\s\-\?]', '', query)
        
        return query
    
    def _extract_intent(self, query: str) -> Dict[str, Any]:
        """Extract user intent from query"""
        intent = {
            'type': 'general',
            'action': None,
            'subject': None,
            'confidence': 0.0
        }
        
        # Check against patterns
        for intent_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    intent['type'] = intent_type
                    intent['confidence'] = 0.9
                    break
            if intent['confidence'] > 0:
                break
        
        # Extract action verbs
        action_verbs = ['control', 'treat', 'prevent', 'apply', 'use', 'grow', 'plant', 'harvest']
        for verb in action_verbs:
            if verb in query:
                intent['action'] = verb
                break
        
        return intent
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms"""
        expanded = [query]
        words = query.split()
        
        for word in words:
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    expanded.append(query.replace(word, synonym))
        
        return expanded

    
    def _search_knowledge_base(self, queries: List[str], knowledge_base: Dict) -> List[Dict]:
        """Search through knowledge base with multiple query variations"""
        results = []
        seen_keys = set()
        
        for query in queries:
            for key, data in knowledge_base.items():
                if key in seen_keys:
                    continue
                
                # Calculate relevance score
                score = self._calculate_relevance(query, key, data)
                
                if score > 0:
                    results.append({
                        'key': key,
                        'data': data,
                        'score': score,
                        'matched_query': query
                    })
                    seen_keys.add(key)
        
        return results
    
    def _calculate_relevance(self, query: str, key: str, data: Dict) -> float:
        """Calculate relevance score for search result"""
        score = 0.0
        
        # Exact key match
        if key in query:
            score += 10.0
        
        # Partial key match
        if any(word in query for word in key.split()):
            score += 5.0
        
        # Fuzzy match
        similarity = difflib.SequenceMatcher(None, query, key).ratio()
        score += similarity * 3.0
        
        # Check data fields
        if isinstance(data, dict):
            # Crop matches
            if 'crops' in data:
                for crop in data['crops']:
                    if crop in query:
                        score += 4.0
            
            # Category match
            if 'category' in data and data['category'] in query:
                score += 3.0
            
            # Symptom matches
            if 'symptoms' in data:
                for symptom in data['symptoms']:
                    if symptom in query:
                        score += 2.0
            
            # Solution keyword matches
            if 'solution' in data:
                solution_words = data['solution'].lower().split()
                query_words = query.split()
                common_words = set(solution_words) & set(query_words)
                score += len(common_words) * 0.5
        
        return score
    
    def _rank_results(self, results: List[Dict], query: str, intent: Dict) -> List[Dict]:
        """Rank search results by relevance"""
        # Sort by score
        ranked = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Boost results matching intent
        if intent['type'] != 'general':
            for result in ranked:
                if result['data'].get('category') == intent['type'].split('_')[0]:
                    result['score'] *= 1.2
        
        # Re-sort after boosting
        ranked = sorted(ranked, key=lambda x: x['score'], reverse=True)
        
        return ranked
    
    def _apply_context(self, results: List[Dict], context: Dict) -> List[Dict]:
        """Apply user context to refine results"""
        # Location-based filtering
        if 'location' in context:
            location = context['location']
            # Could filter by region-specific recommendations
        
        # Previous query context
        if 'previous_queries' in context:
            # Boost related topics
            pass
        
        return results
    
    def _generate_suggestions(self, query: str, results: List[Dict]) -> List[str]:
        """Generate search suggestions based on results"""
        suggestions = []
        
        # Related topics from results
        for result in results[:5]:
            data = result['data']
            if isinstance(data, dict):
                # Suggest related crops
                if 'crops' in data:
                    for crop in data['crops'][:2]:
                        suggestions.append(f"How to manage {result['key']} in {crop}?")
                
                # Suggest prevention
                if 'prevention' in data and data['prevention']:
                    suggestions.append(f"How to prevent {result['key']}?")
        
        return list(set(suggestions))[:5]
    
    def _update_search_history(self, query: str, results: List[Dict]):
        """Update search history and statistics"""
        self.search_history.append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'results_count': len(results)
        })
        
        # Keep only last 100 searches
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]
    
    def get_trending_queries(self) -> List[str]:
        """Get trending search queries"""
        query_counts = defaultdict(int)
        
        for search in self.search_history[-50:]:  # Last 50 searches
            query_counts[search['query']] += 1
        
        trending = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [query for query, count in trending[:10]]
    
    def get_search_stats(self) -> Dict:
        """Get search engine statistics"""
        return {
            'total_searches': self.search_stats['total_searches'],
            'recent_searches': len(self.search_history),
            'trending_queries': self.get_trending_queries()
        }


class RealTimeChatAI:
    """Real-time chat AI with search integration and Watsonx"""
    
    def __init__(self, knowledge_base: Dict, watsonx_ai=None):
        self.knowledge_base = knowledge_base
        self.search_engine = AISearchEngine()
        self.watsonx_ai = watsonx_ai
        self.conversation_history = []
        self.user_context = {}
        
    def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Process incoming chat message with AI search and Watsonx"""
        
        # Search knowledge base
        search_results = self.search_engine.search(
            message,
            self.knowledge_base,
            self.user_context
        )
        
        # Generate AI response with Watsonx if available
        if self.watsonx_ai and self.watsonx_ai.is_available:
            watsonx_response = self.watsonx_ai.generate_response(
                message,
                {
                    'search_results': search_results['results'],
                    'intent': search_results['intent'],
                    'location': self.user_context.get('location'),
                    'previous_queries': [
                        conv['message'] for conv in self.conversation_history[-3:]
                        if conv.get('session_id') == session_id
                    ]
                }
            )
            ai_response = watsonx_response['answer']
            confidence = watsonx_response['confidence']
            source = watsonx_response['source']
        else:
            # Fallback to basic AI response
            ai_response = self._generate_ai_response(message, search_results)
            confidence = 0.80
            source = 'Knowledge Base'
        
        # Update conversation history
        self._update_conversation(message, ai_response, session_id)
        
        return {
            'message': message,
            'response': ai_response,
            'search_results': search_results,
            'suggestions': search_results['suggestions'],
            'intent': search_results['intent'],
            'confidence': confidence,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_ai_response(self, message: str, search_results: Dict) -> str:
        """Generate intelligent AI response"""
        if search_results['total_results'] == 0:
            return self._generate_fallback_response(message)
        
        # Get top result
        top_result = search_results['results'][0]
        data = top_result['data']
        
        # Build comprehensive response
        response = f"🤖 **AI Agricultural Assistant**\n\n"
        response += f"Based on your query about **{top_result['key']}**, here's what I found:\n\n"
        
        if isinstance(data, dict):
            if 'solution' in data:
                response += f"**Solution:**\n{data['solution']}\n\n"
            
            if 'symptoms' in data:
                response += f"**Symptoms:**\n"
                for symptom in data['symptoms'][:5]:
                    response += f"• {symptom.capitalize()}\n"
                response += "\n"
            
            if 'prevention' in data:
                response += f"**Prevention:**\n"
                for prevention in data['prevention'][:5]:
                    response += f"• {prevention.capitalize()}\n"
                response += "\n"
            
            if 'dosage' in data:
                response += f"**Dosage:** {data['dosage']}\n\n"
        
        # Add related information
        if search_results['total_results'] > 1:
            response += f"\n💡 I found {search_results['total_results']} related topics. "
            response += "Would you like to know more about any specific aspect?"
        
        return response
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response when no results found"""
        return f"""I understand you're asking about "{message}".

While I don't have specific information about this in my current knowledge base, here are some general recommendations:

🌱 **General Agricultural Advice:**
• Consult with local agricultural extension officers
• Conduct soil and crop health assessments
• Follow integrated pest and disease management practices
• Maintain proper irrigation and drainage
• Use recommended fertilizers based on soil tests

Would you like to rephrase your question or ask about something else?"""
    
    def _update_conversation(self, message: str, response: str, session_id: str):
        """Update conversation history"""
        self.conversation_history.append({
            'session_id': session_id,
            'message': message,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 50 conversations
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def get_conversation_context(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return [
            conv for conv in self.conversation_history
            if conv['session_id'] == session_id
        ][-10:]  # Last 10 messages