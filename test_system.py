#!/usr/bin/env python3
"""
Simple test script for Self-Quiz Generator Agent
Tests basic functionality without requiring API calls
"""

import os
import sys
import traceback

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from src.core.models import SourceType, DifficultyLevel, QuestionType, Quiz, QuizQuestion
        print("✅ Core models imported successfully")
        
        from src.agents.reader_agent import ReaderAgent, TextCleaner
        print("✅ Reader agent imported successfully")
        
        from src.utils.formatters import QuizFormatter
        print("✅ Formatters imported successfully")
        
        from src.core.orchestrator import QuizGenerator
        print("✅ Orchestrator imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_text_cleaning():
    """Test text cleaning functionality."""
    print("\n🧹 Testing text cleaning...")
    
    try:
        from src.agents.reader_agent import TextCleaner
        
        sample_text = """
        This is a sample text with    extra spaces.
        It has [bracketed content] and (parenthetical content).
        Page 1
        Some meaningful content here.
        """
        
        cleaner = TextCleaner()
        cleaned = cleaner.clean_text(sample_text)
        sentences = cleaner.extract_sentences(cleaned)
        
        print(f"✅ Original length: {len(sample_text)}")
        print(f"✅ Cleaned length: {len(cleaned)}")
        print(f"✅ Sentences extracted: {len(sentences)}")
        
        return True
    except Exception as e:
        print(f"❌ Text cleaning error: {e}")
        return False

def test_reader_agent():
    """Test reader agent with sample text."""
    print("\n📖 Testing reader agent...")
    
    try:
        from src.agents.reader_agent import ReaderAgent
        from src.core.models import SourceType
        
        reader = ReaderAgent()
        sample_text = "Photosynthesis is the process by which plants convert light energy into chemical energy."
        
        result = reader.read(sample_text, SourceType.TEXT)
        
        if result['success']:
            print(f"✅ Text read successfully")
            print(f"✅ Content length: {len(result['text'])}")
            print(f"✅ Source type detected: {reader.detect_source_type(sample_text)}")
            return True
        else:
            print(f"❌ Failed to read text: {result.get('source_info', {}).get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Reader agent error: {e}")
        return False

def test_formatters():
    """Test quiz formatters."""
    print("\n📄 Testing formatters...")
    
    try:
        from src.utils.formatters import QuizFormatter
        from src.core.models import Quiz, QuizQuestion, QuestionType, DifficultyLevel
        
        # Create a sample quiz
        sample_question = QuizQuestion(
            question="What is photosynthesis?",
            answer="The process by which plants convert light energy into chemical energy",
            type=QuestionType.SHORT_ANSWER,
            difficulty=DifficultyLevel.EASY,
            explanation="Photosynthesis is a fundamental biological process",
            topic="Biology"
        )
        
        sample_quiz = Quiz(
            title="Test Quiz",
            source="Test Source",
            questions=[sample_question],
            total_questions=1,
            difficulty_distribution={"easy": 1},
            topics=["Biology"]
        )
        
        formatter = QuizFormatter()
        
        # Test JSON export
        json_file = formatter.export_to_json(sample_quiz, "test_quiz.json")
        print(f"✅ JSON export: {json_file}")
        
        # Test CSV export
        csv_file = formatter.export_to_csv(sample_quiz, "test_quiz.csv")
        print(f"✅ CSV export: {csv_file}")
        
        # Test HTML export
        html_file = formatter.export_to_html(sample_quiz, "test_quiz.html")
        print(f"✅ HTML export: {html_file}")
        
        # Clean up test files
        for file in [json_file, csv_file, html_file]:
            if os.path.exists(file):
                os.remove(file)
        
        return True
    except Exception as e:
        print(f"❌ Formatter error: {e}")
        return False

def test_api_key():
    """Test if API key is available."""
    print("\n🔑 Testing API key...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"✅ Google API key found: {api_key[:10]}...")
        return True
    else:
        print("⚠️  No Google API key found in environment variables")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        return False

def test_web_ui_imports():
    """Test if web UI dependencies are available."""
    print("\n🌐 Testing web UI dependencies...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
        
        import plotly
        print(f"✅ Plotly {plotly.__version__}")
        
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Install with: pip install streamlit plotly")
        return False

def main():
    """Run all tests."""
    print("🧪 Self-Quiz Generator Agent - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Text Cleaning", test_text_cleaning),
        ("Reader Agent", test_reader_agent),
        ("Formatters", test_formatters),
        ("API Key", test_api_key),
        ("Web UI Dependencies", test_web_ui_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\nNext steps:")
        print("1. Set your Google API key: export GOOGLE_API_KEY='your-key'")
        print("2. Launch web UI: python launch_ui.py")
        print("3. Or run demo: python demo_ui.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("• Install missing dependencies: pip install -r requirements.txt")
        print("• Set API key: export GOOGLE_API_KEY='your-key'")
        print("• Check Python version (3.8+ recommended)")

if __name__ == "__main__":
    main()
