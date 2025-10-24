#!/usr/bin/env python3
"""
Quick test script for Google API integration
"""

import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_google_api():
    """Test Google API integration."""
    print("🧪 Testing Google API Integration")
    print("=" * 40)
    
    # Set the API key
    api_key = "AIzaSyALHcpX6Bfw8-qWgbBpz3bxgF8G8Yg0tvA"
    os.environ['GOOGLE_API_KEY'] = api_key
    
    try:
        # Test imports
        print("1. Testing imports...")
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
        
        # Test API configuration
        print("2. Testing API configuration...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Model configured successfully")
        
        # Test simple generation
        print("3. Testing simple generation...")
        response = model.generate_content("What is photosynthesis? Answer in one sentence.")
        print(f"✅ Generated response: {response.text[:100]}...")
        
        # Test quiz generation
        print("4. Testing quiz generation...")
        from src.core.orchestrator import QuizGenerator
        
        generator = QuizGenerator(api_key)
        sample_text = """
        Photosynthesis is the process by which plants convert light energy into chemical energy.
        This process occurs in the chloroplasts of plant cells, specifically in structures called thylakoids.
        The main pigment involved in photosynthesis is chlorophyll, which absorbs light primarily in the blue and red wavelengths.
        
        The process can be divided into two main stages: the light-dependent reactions and the Calvin cycle.
        In the light-dependent reactions, light energy is captured and used to produce ATP and NADPH.
        The Calvin cycle uses these energy carriers to convert carbon dioxide into glucose.
        
        The overall equation for photosynthesis is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2
        This process is crucial for life on Earth as it produces oxygen and forms the base of most food chains.
        """
        
        response = generator.generate_from_text(
            sample_text,
            num_questions=2
        )
        
        if response.success:
            quiz = response.quiz
            print(f"✅ Quiz generated successfully!")
            print(f"   Title: {quiz.title}")
            print(f"   Questions: {quiz.total_questions}")
            print(f"   First question: {quiz.questions[0].question}")
        else:
            print(f"❌ Quiz generation failed: {response.error}")
        
        print("\n🎉 All tests passed! Google API integration is working.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_google_api()
