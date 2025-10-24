"""
Streamlit Web UI for Self-Quiz Generator Agent
Interactive interface for testing and using the quiz generation system.
"""

import streamlit as st
import os
import sys
import time
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Optional, List

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.orchestrator import QuizGenerator
from src.core.models import SourceType, DifficultyLevel, QuestionType, ProcessingRequest
from src.utils.formatters import QuizFormatter


# Page configuration
st.set_page_config(
    page_title="Self-Quiz Generator Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .question-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .difficulty-easy { color: #28a745; font-weight: bold; }
    .difficulty-medium { color: #ffc107; font-weight: bold; }
    .difficulty-hard { color: #dc3545; font-weight: bold; }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'quiz_generator' not in st.session_state:
        st.session_state.quiz_generator = None
    if 'generated_quiz' not in st.session_state:
        st.session_state.generated_quiz = None
    if 'processing_time' not in st.session_state:
        st.session_state.processing_time = 0
    if 'api_key_status' not in st.session_state:
        st.session_state.api_key_status = False


def check_api_key(api_key: str) -> bool:
    """Check if API key is valid."""
    if not api_key:
        return False
    
    try:
        generator = QuizGenerator(api_key)
        # Try a simple test to validate the key
        test_response = generator.generate_from_text("Test", num_questions=1)
        return True
    except Exception:
        return False


def create_quiz_generator(api_key: str) -> QuizGenerator:
    """Create and return a QuizGenerator instance."""
    return QuizGenerator(api_key)


def display_quiz_summary(quiz):
    """Display quiz summary with metrics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", quiz.total_questions)
    
    with col2:
        st.metric("Topics Covered", len(quiz.topics))
    
    with col3:
        easy_count = quiz.difficulty_distribution.get('easy', 0)
        st.metric("Easy Questions", easy_count)
    
    with col4:
        hard_count = quiz.difficulty_distribution.get('hard', 0)
        st.metric("Hard Questions", hard_count)
    
    # Difficulty distribution chart
    if quiz.difficulty_distribution:
        fig = px.pie(
            values=list(quiz.difficulty_distribution.values()),
            names=list(quiz.difficulty_distribution.keys()),
            title="Difficulty Distribution",
            color_discrete_map={
                'easy': '#28a745',
                'medium': '#ffc107', 
                'hard': '#dc3545'
            }
        )
        st.plotly_chart(fig, use_container_width=True)


def display_quiz_questions(quiz):
    """Display quiz questions in an interactive format."""
    st.subheader("📝 Generated Questions")
    
    for i, question in enumerate(quiz.questions, 1):
        with st.expander(f"Question {i} - {question.difficulty.value.upper()}", expanded=False):
            st.markdown(f"**Q:** {question.question}")
            
            if question.options:
                st.markdown("**Options:**")
                for j, option in enumerate(question.options):
                    is_correct = option == question.answer
                    if is_correct:
                        st.markdown(f"✅ **{chr(65+j)}.** {option}")
                    else:
                        st.markdown(f"❌ **{chr(65+j)}.** {option}")
            else:
                st.markdown(f"**Answer:** {question.answer}")
            
            if question.explanation:
                st.markdown(f"**Explanation:** {question.explanation}")
            
            if question.topic:
                st.markdown(f"**Topic:** {question.topic}")


def create_download_buttons(quiz):
    """Create download buttons for different formats."""
    formatter = QuizFormatter()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        json_data = json.dumps({
            "title": quiz.title,
            "source": quiz.source,
            "total_questions": quiz.total_questions,
            "difficulty_distribution": quiz.difficulty_distribution,
            "topics": quiz.topics,
            "generated_at": datetime.now().isoformat(),
            "questions": [
                {
                    "question": q.question,
                    "answer": q.answer,
                    "type": q.type.value,
                    "difficulty": q.difficulty.value,
                    "options": q.options,
                    "explanation": q.explanation,
                    "topic": q.topic
                } for q in quiz.questions
            ]
        }, indent=2)
        
        st.download_button(
            label="📄 Download JSON",
            data=json_data,
            file_name=f"{quiz.title.replace(' ', '_')}_quiz.json",
            mime="application/json"
        )
    
    with col2:
        csv_data = formatter.export_to_csv(quiz, None)
        with open(csv_data, 'r') as f:
            csv_content = f.read()
        
        st.download_button(
            label="📊 Download CSV",
            data=csv_content,
            file_name=f"{quiz.title.replace(' ', '_')}_quiz.csv",
            mime="text/csv"
        )
    
    with col3:
        html_content = formatter._generate_html_content(quiz)
        st.download_button(
            label="🌐 Download HTML",
            data=html_content,
            file_name=f"{quiz.title.replace(' ', '_')}_quiz.html",
            mime="text/html"
        )
    
    with col4:
        anki_data = formatter.export_to_anki(quiz, None)
        with open(anki_data, 'r') as f:
            anki_content = f.read()
        
        st.download_button(
            label="🃏 Download Anki",
            data=anki_content,
            file_name=f"{quiz.title.replace(' ', '_')}_anki.csv",
            mime="text/csv"
        )


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🎓 Self-Quiz Generator Agent</h1>', unsafe_allow_html=True)
    st.markdown("Generate intelligent quizzes from any document, webpage, or text content using AI.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key. Get one from https://platform.openai.com/api-keys",
            value=os.getenv('OPENAI_API_KEY', '')
        )
        
        if api_key:
            if st.button("🔑 Validate API Key"):
                with st.spinner("Validating API key..."):
                    if check_api_key(api_key):
                        st.success("✅ API key is valid!")
                        st.session_state.api_key_status = True
                        st.session_state.quiz_generator = create_quiz_generator(api_key)
                    else:
                        st.error("❌ Invalid API key. Please check and try again.")
                        st.session_state.api_key_status = False
        else:
            st.warning("⚠️ Please enter your OpenAI API key to continue.")
            st.session_state.api_key_status = False
        
        st.divider()
        
        # Quiz parameters
        st.header("📋 Quiz Parameters")
        
        num_questions = st.slider("Number of Questions", 1, 20, 10)
        
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Any", "Easy", "Medium", "Hard"],
            help="Select preferred difficulty level"
        )
        
        question_types = st.multiselect(
            "Question Types",
            ["Multiple Choice", "Short Answer", "True/False"],
            default=["Multiple Choice", "Short Answer"],
            help="Select types of questions to generate"
        )
        
        st.divider()
        
        # Sample content
        st.header("📚 Sample Content")
        if st.button("Load Sample Text"):
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
            st.session_state.sample_text = sample_text
    
    # Main content area
    if not st.session_state.api_key_status:
        st.info("👆 Please configure your OpenAI API key in the sidebar to start generating quizzes.")
        return
    
    # Source input section
    st.header("📖 Source Content")
    
    source_type = st.radio(
        "Select Source Type",
        ["Text Input", "URL", "File Upload"],
        horizontal=True
    )
    
    source_content = ""
    
    if source_type == "Text Input":
        source_content = st.text_area(
            "Enter your text content",
            height=200,
            placeholder="Paste your text content here...",
            value=st.session_state.get('sample_text', '')
        )
        
    elif source_type == "URL":
        url = st.text_input("Enter URL", placeholder="https://example.com/article")
        if url:
            source_content = url
            
    elif source_type == "File Upload":
        uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf'])
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                source_content = str(uploaded_file.read(), "utf-8")
            else:
                st.warning("PDF upload not supported in this demo. Please use text files or URLs.")
    
    # Generate quiz button
    if source_content and st.button("🚀 Generate Quiz", type="primary"):
        if not st.session_state.api_key_status:
            st.error("Please configure a valid API key first.")
            return
        
        # Prepare parameters
        difficulty_level = None
        if difficulty != "Any":
            difficulty_level = DifficultyLevel(difficulty.lower())
        
        question_type_objects = []
        for qtype in question_types:
            if qtype == "Multiple Choice":
                question_type_objects.append(QuestionType.MULTIPLE_CHOICE)
            elif qtype == "Short Answer":
                question_type_objects.append(QuestionType.SHORT_ANSWER)
            elif qtype == "True/False":
                question_type_objects.append(QuestionType.TRUE_FALSE)
        
        # Determine source type
        if source_type == "Text Input":
            source_type_enum = SourceType.TEXT
        elif source_type == "URL":
            source_type_enum = SourceType.URL
        else:
            source_type_enum = SourceType.FILE
        
        # Create request
        request = ProcessingRequest(
            source=source_content,
            source_type=source_type_enum,
            num_questions=num_questions,
            difficulty_preference=difficulty_level,
            question_types=question_type_objects if question_type_objects else None
        )
        
        # Generate quiz
        with st.spinner("🤖 Generating quiz questions..."):
            start_time = time.time()
            response = st.session_state.quiz_generator.generate_quiz(request)
            processing_time = time.time() - start_time
        
        if response.success:
            st.session_state.generated_quiz = response.quiz
            st.session_state.processing_time = processing_time
            st.success(f"✅ Quiz generated successfully in {processing_time:.2f} seconds!")
        else:
            st.error(f"❌ Error generating quiz: {response.error}")
    
    # Display results
    if st.session_state.generated_quiz:
        quiz = st.session_state.generated_quiz
        
        st.header("📊 Quiz Results")
        
        # Quiz summary
        display_quiz_summary(quiz)
        
        # Topics
        if quiz.topics:
            st.subheader("🏷️ Topics Covered")
            topic_cols = st.columns(len(quiz.topics))
            for i, topic in enumerate(quiz.topics):
                with topic_cols[i]:
                    st.markdown(f"**{topic}**")
        
        # Questions
        display_quiz_questions(quiz)
        
        # Download options
        st.header("💾 Download Options")
        create_download_buttons(quiz)
        
        # Processing info
        st.info(f"⏱️ Generated in {st.session_state.processing_time:.2f} seconds | Source: {quiz.source}")


if __name__ == "__main__":
    main()
