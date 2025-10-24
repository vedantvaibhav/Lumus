#!/usr/bin/env python3
"""
Enhanced Quiz Generator with Web Search + AI
Uses web search to gather data, then AI to generate quizzes
"""

import os
import sys
import json
import time
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from urllib.parse import urljoin, urlparse
import re

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class WebDataGatherer:
    """Gathers data from web sources about a topic."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def search_wikipedia(self, topic):
        """Search Wikipedia for topic information."""
        try:
            # Search Wikipedia API
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic.replace(" ", "_")
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', topic),
                    'summary': data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'source': 'Wikipedia'
                }
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        return None
    
    def search_web(self, topic, num_results=3):
        """Search web for topic information using DuckDuckGo."""
        try:
            # Use DuckDuckGo instant answer API
            search_url = f"https://api.duckduckgo.com/"
            params = {
                'q': topic,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get abstract and related topics
                abstract = data.get('Abstract', '')
                abstract_text = data.get('AbstractText', '')
                related_topics = data.get('RelatedTopics', [])[:num_results]
                
                content = abstract or abstract_text or ''
                
                # Add related topics info
                for topic_info in related_topics:
                    if isinstance(topic_info, dict) and 'Text' in topic_info:
                        content += f"\n\n{topic_info['Text']}"
                
                if content:
                    return {
                        'title': topic,
                        'summary': content,
                        'url': data.get('AbstractURL', ''),
                        'source': 'DuckDuckGo'
                    }
        except Exception as e:
            print(f"Web search error: {e}")
        
        return None
    
    def gather_topic_data(self, topic):
        """Gather comprehensive data about a topic."""
        print(f"🔍 Gathering data about: {topic}")
        
        # Try multiple sources
        sources = []
        
        # Try Wikipedia first
        wiki_data = self.search_wikipedia(topic)
        if wiki_data:
            sources.append(wiki_data)
            print(f"✅ Found Wikipedia data")
        
        # Try web search
        web_data = self.search_web(topic)
        if web_data:
            sources.append(web_data)
            print(f"✅ Found web data")
        
        # Combine all sources
        if sources:
            combined_content = "\n\n".join([f"Source: {s['source']}\n{s['summary']}" for s in sources])
            return {
                'topic': topic,
                'content': combined_content,
                'sources': sources,
                'total_length': len(combined_content)
            }
        
        return None

class EnhancedQuizGenerator:
    """Enhanced quiz generator using web data + AI."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Try different models in order of preference (prioritizing quality)
        self.models_to_try = [
            'gemini-2.5-flash',
            'gemini-2.5-flash-lite', 
            'gemini-2.0-flash',
            'gemini-flash-latest',
            'gemini-2.0-flash-lite',
            'gemini-flash-lite-latest'
        ]
        
        self.data_gatherer = WebDataGatherer()
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the first available model."""
        for model_name in self.models_to_try:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ Using model: {model_name}")
                return
            except Exception as e:
                print(f"❌ Model {model_name} failed: {e}")
                continue
        
        raise Exception("No working models found!")
    
    def generate_quiz_from_topic(self, topic, num_questions=10):
        """Generate quiz by first gathering data, then creating questions."""
        
        # Step 1: Gather data about the topic
        topic_data = self.data_gatherer.gather_topic_data(topic)
        
        if not topic_data:
            print(f"❌ Could not gather data for topic: {topic}")
            return self._create_fallback_quiz(topic)
        
        print(f"📊 Gathered {topic_data['total_length']} characters of content")
        
        # Step 2: Generate quiz using the gathered data
        return self._generate_quiz_with_data(topic_data, num_questions)
    
    def _generate_quiz_with_data(self, topic_data, num_questions):
        """Generate quiz using gathered data."""
        
        prompt = f"""
You are an expert educational quiz generator with advanced pedagogical knowledge. Create a high-quality quiz about "{topic_data['topic']}" using the following information:

{topic_data['content']}

STRICT QUALITY REQUIREMENTS:
1. Generate exactly {num_questions} questions
2. Use ONLY multiple-choice (4 options) and true/false questions
3. NO short answer questions that require typing
4. Mix question types: 60% multiple-choice, 40% true/false
5. Include easy, medium, and hard questions with proper distribution
6. Each question must have a clear, educational explanation
7. Questions MUST test understanding, not just memorization
8. Focus on IMPORTANT concepts and key information
9. Make questions challenging but fair - they should make students think
10. Avoid trivial details or overly specific information
11. Each question should teach something valuable

Format as JSON:
{{
    "title": "Quiz Title",
    "total_questions": {num_questions},
    "questions": [
        {{
            "question": "Question text?",
            "type": "multiple-choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Correct Option",
            "explanation": "Why this answer is correct",
            "difficulty": "easy|medium|hard"
        }},
        {{
            "question": "True or False statement?",
            "type": "true-false", 
            "answer": "True|False",
            "explanation": "Why this answer is correct",
            "difficulty": "easy|medium|hard"
        }}
    ]
}}

Make sure all questions are relevant to the topic and based on the provided information.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,  # Lower temperature for more consistent quality
                    max_output_tokens=6000,  # Increased token limit
                )
            )
            
            # Parse JSON response
            quiz_text = response.text.strip()
            
            # Clean up the response (remove markdown formatting if present)
            if quiz_text.startswith('```json'):
                quiz_text = quiz_text[7:]
            if quiz_text.endswith('```'):
                quiz_text = quiz_text[:-3]
            
            quiz_data = json.loads(quiz_text)
            
            # Validate and clean the quiz
            quiz_data = self._validate_quiz(quiz_data, topic_data['topic'])
            
            print(f"✅ Generated quiz with {len(quiz_data['questions'])} questions")
            return quiz_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response: {response.text[:500]}...")
            return self._create_fallback_quiz(topic_data['topic'])
        except Exception as e:
            print(f"❌ Quiz generation error: {e}")
            return self._create_fallback_quiz(topic_data['topic'])
    
    def _validate_quiz(self, quiz_data, topic):
        """Validate and clean quiz data."""
        
        # Ensure required fields
        if 'questions' not in quiz_data:
            quiz_data['questions'] = []
        
        if 'title' not in quiz_data:
            quiz_data['title'] = f"{topic} Quiz"
        
        if 'total_questions' not in quiz_data:
            quiz_data['total_questions'] = len(quiz_data['questions'])
        
        # Clean questions
        cleaned_questions = []
        for q in quiz_data['questions']:
            if self._is_valid_question(q):
                cleaned_questions.append(q)
        
        quiz_data['questions'] = cleaned_questions
        quiz_data['total_questions'] = len(cleaned_questions)
        
        return quiz_data
    
    def _is_valid_question(self, question):
        """Check if a question is valid."""
        required_fields = ['question', 'type', 'answer', 'explanation']
        
        for field in required_fields:
            if field not in question or not question[field]:
                return False
        
        # Check question type
        if question['type'] not in ['multiple-choice', 'true-false']:
            return False
        
        # For multiple choice, check options
        if question['type'] == 'multiple-choice':
            if 'options' not in question or len(question['options']) != 4:
                return False
        
        return True
    
    def _create_fallback_quiz(self, topic):
        """Create a simple fallback quiz when data gathering fails."""
        return {
            "title": f"{topic} Quiz",
            "total_questions": 5,
            "questions": [
                {
                    "question": f"What is {topic}?",
                    "type": "multiple-choice",
                    "options": [f"A field related to {topic}", "A type of technology", "A historical event", "A scientific concept"],
                    "answer": f"A field related to {topic}",
                    "explanation": f"This is a general question about {topic}.",
                    "difficulty": "easy"
                },
                {
                    "question": f"True or False: {topic} is an important subject.",
                    "type": "true-false",
                    "answer": "True",
                    "explanation": f"{topic} is indeed an important subject worth studying.",
                    "difficulty": "easy"
                },
                {
                    "question": f"Which best describes {topic}?",
                    "type": "multiple-choice",
                    "options": ["A complex subject", "A simple concept", "A practical skill", "An abstract idea"],
                    "answer": "A complex subject",
                    "explanation": f"{topic} typically involves multiple aspects and concepts.",
                    "difficulty": "medium"
                },
                {
                    "question": f"True or False: {topic} requires specialized knowledge.",
                    "type": "true-false",
                    "answer": "True",
                    "explanation": "Most topics require some level of specialized knowledge to understand fully.",
                    "difficulty": "easy"
                },
                {
                    "question": f"What is the main focus of {topic}?",
                    "type": "multiple-choice",
                    "options": ["Understanding core concepts", "Memorizing facts", "Practical application", "All of the above"],
                    "answer": "All of the above",
                    "explanation": f"{topic} typically involves understanding, memorization, and application.",
                    "difficulty": "medium"
                }
            ]
        }

def main():
    """Test the enhanced quiz generator."""
    api_key = "AIzaSyALHcpX6Bfw8-qWgbBpz3bxgF8G8Yg0tvA"
    
    print("🚀 Enhanced Quiz Generator with Web Search")
    print("=" * 50)
    
    try:
        generator = EnhancedQuizGenerator(api_key)
        
        # Test topics
        test_topics = ["Photosynthesis", "Machine Learning", "Climate Change"]
        
        for topic in test_topics:
            print(f"\n📚 Testing topic: {topic}")
            print("-" * 30)
            
            quiz = generator.generate_quiz_from_topic(topic, num_questions=5)
            
            print(f"✅ Generated: {quiz['title']}")
            print(f"📊 Questions: {quiz['total_questions']}")
            
            # Show first question as example
            if quiz['questions']:
                first_q = quiz['questions'][0]
                print(f"🎯 Sample question: {first_q['question']}")
                print(f"📝 Type: {first_q['type']}")
                if first_q['type'] == 'multiple-choice':
                    print(f"🔤 Options: {len(first_q['options'])}")
            
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
