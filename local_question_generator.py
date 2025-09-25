"""
Local AI Question Generator
Generates new questions based on real matura data using RAG and OpenAI
This is for local development only - not for deployment
"""
import streamlit as st
import json
import os
import time
from typing import List, Dict, Any

# Set page config
st.set_page_config(
    page_title="🧠 Local AI Question Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .generated-tag {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin: 5px 0;
    }
    .question-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .question-number {
        font-size: 18px;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 10px;
    }
    .question-text {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .option-item {
        margin: 8px 0;
        padding: 8px;
        background: white;
        border-radius: 4px;
        border-left: 3px solid #4ECDC4;
    }
</style>
""", unsafe_allow_html=True)

def load_real_questions():
    """Load real matura questions from JSON files"""
    questions = []
    
    json_files = [
        "data/matura_21_05_2025.json",
        "data/matura_2025_avgust.json"
    ]
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    questions.extend(data)
                elif isinstance(data, dict) and 'questions' in data:
                    questions.extend(data['questions'])
                else:
                    questions.append(data)
        except Exception as e:
            st.error(f"❌ Error loading {file_path}: {e}")
    
    return questions

def display_question(question, index, show_checkboxes=True):
    """Display a single question with proper formatting"""
    with st.container():
        st.markdown(f"""
        <div class="question-box">
            <div class="question-number">Въпрос {index + 1}</div>
            <div class="question-text"><strong>{question.get('question', 'N/A')}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show generated tag
        st.markdown('<div class="generated-tag">🤖 AI Генериран</div>', unsafe_allow_html=True)
        
        # Display options with checkboxes if available
        if question.get('options') and show_checkboxes:
            st.markdown("**Изберете отговор:**")
            selected_options = []
            
            for j, option in enumerate(question['options']):
                # Create a simple but unique key
                unique_key = f"option_{index}_{j}_{int(time.time() * 1000000) % 1000000}"
                
                if st.checkbox(f"{option}", key=unique_key):
                    selected_options.append(option)
            
            # Automatic answer checking when option is selected
            if selected_options:
                # Check if selected answer is correct
                if question.get('correct_answer') in selected_options:
                    st.success("✅ Правилен отговор!")
                else:
                    st.error("❌ Грешен отговор!")
                    if question.get('correct_answer'):
                        st.markdown(f"**Правилният отговор е:** {question['correct_answer']}")
        elif question.get('options'):
            st.markdown("**Опции:**")
            for j, option in enumerate(question['options']):
                st.markdown(f"**{chr(65+j)}.** {option}")
        
        # Display correct answer if not using checkboxes
        if question.get('correct_answer') and not show_checkboxes:
            st.markdown(f"""
            <div class="correct-answer">
                <strong>Правилен отговор:</strong> {question['correct_answer']}
            </div>
            """, unsafe_allow_html=True)
        
        # Display metadata
        if question.get('subject'):
            st.markdown(f"**Предмет:** {question['subject']}")
        
        if question.get('difficulty'):
            st.markdown(f"**Трудност:** {question['difficulty']}")
        
        if question.get('points'):
            st.markdown(f"**Точки:** {question['points']}")
        
        st.markdown("---")

def main():
    st.markdown('<h1 class="main-header">🧠 Local AI Question Generator</h1>', unsafe_allow_html=True)
    
    st.info("""
    **🎯 Цел:** Генериране на нови въпроси за ДЗИ матура използвайки AI и RAG система.
    **📍 Забележка:** Това е за локална разработка. За deployment използвай `app_real_matura.py`.
    """)
    
    # Initialize session state
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎛️ AI Контроли")
        
        # Generate new questions
        st.subheader("🤖 Генерирай нови въпроси")
        num_language = st.number_input("Брой въпроси за език:", min_value=1, max_value=50, value=5, key="num_language")
        num_literature = st.number_input("Брой въпроси за литература:", min_value=1, max_value=50, value=5, key="num_literature")
        
        # Generation method selection
        generation_method = st.selectbox(
            "Метод на генериране:",
            ["Базов генератор", "RAG генериране (AI)"],
            key="generation_method"
        )
        
        if st.button("🚀 Генерирай нови въпроси", key="generate_new"):
            with st.spinner("Генериране на нови въпроси с AI..."):
                try:
                    import sys
                    sys.path.append('src')
                    from src.question_generator import DZIQuestionGenerator, SubjectArea
                    
                    generator = DZIQuestionGenerator()
                    
                    if generation_method == "RAG генериране (AI)":
                        # Try to use RAG generator
                        try:
                            from src.simple_rag_generator import SimpleRAGGenerator
                            rag_generator = SimpleRAGGenerator()
                            
                            # Generate new questions using RAG
                            new_language_questions = rag_generator.generate_questions(count=num_language, subject=SubjectArea.LANGUAGE)
                            new_literature_questions = rag_generator.generate_questions(count=num_literature, subject=SubjectArea.LITERATURE)
                            
                            st.success("🧠 Използвам RAG генериране с OpenAI API!")
                            
                        except Exception as e:
                            st.warning(f"⚠️ RAG генераторът не е наличен: {e}")
                            st.info("🔄 Използвам базов генератор")
                            
                            # Fallback to basic generator
                            new_language_questions = generator.generate_questions(count=num_language, subject=SubjectArea.LANGUAGE)
                            new_literature_questions = generator.generate_questions(count=num_literature, subject=SubjectArea.LITERATURE)
                    else:
                        # Use basic generator
                        new_language_questions = generator.generate_questions(count=num_language, subject=SubjectArea.LANGUAGE)
                        new_literature_questions = generator.generate_questions(count=num_literature, subject=SubjectArea.LITERATURE)
                    
                    # Convert to dict format
                    new_questions = []
                    
                    # Handle RAG generator output (already dictionaries)
                    if generation_method == "RAG генериране (AI)":
                        # RAG generator returns dictionaries directly
                        for q in new_language_questions:
                            q['subject'] = 'Български език'
                            new_questions.append(q)
                        
                        for q in new_literature_questions:
                            q['subject'] = 'Българска литература'
                            new_questions.append(q)
                    else:
                        # Basic generator returns objects with attributes
                        for q in new_language_questions:
                            new_questions.append({
                                'question': q.question_text,
                                'options': q.options,
                                'correct_answer': q.correct_answer,
                                'subject': 'Български език',
                                'difficulty': q.difficulty,
                                'points': q.points,
                                'type': 'multiple_choice'
                            })
                        
                        for q in new_literature_questions:
                            new_questions.append({
                                'question': q.question_text,
                                'options': q.options,
                                'correct_answer': q.correct_answer,
                                'subject': 'Българска литература',
                                'difficulty': q.difficulty,
                                'points': q.points,
                                'type': 'multiple_choice'
                            })
                    
                    # Add to existing generated questions
                    if 'generated_questions' not in st.session_state:
                        st.session_state.generated_questions = []
                    
                    st.session_state.generated_questions.extend(new_questions)
                    
                    st.success(f"✅ Генерирани {len(new_questions)} нови AI въпроси!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Грешка при генериране: {e}")
        
        st.markdown("---")
        
        # Clear all questions
        if st.button("🗑️ Изчисти всички въпроси", key="clear_all"):
            st.session_state.generated_questions = []
            st.success("✅ Всички въпроси изчистени")
            st.rerun()
        
        # Export questions
        if st.button("📤 Експортирай въпроси", key="export"):
            if st.session_state.generated_questions:
                try:
                    export_data = {
                        "metadata": {
                            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "total_questions": len(st.session_state.generated_questions),
                            "generation_method": generation_method
                        },
                        "questions": st.session_state.generated_questions
                    }
                    
                    # Create ai-data directory if it doesn't exist
                    os.makedirs("ai-data", exist_ok=True)
                    
                    # Generate unique filename with timestamp
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"ai-data/ai_questions_{timestamp}.json"
                    
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"✅ Въпросите са експортирани в `{filename}`")
                except Exception as e:
                    st.error(f"❌ Грешка при експорт: {e}")
            else:
                st.warning("⚠️ Няма въпроси за експорт")
    
    # Display generated questions
    st.subheader("🤖 AI Генерирани въпроси")
    if st.session_state.generated_questions:
        st.markdown(f"**Брой генерирани въпроси:** {len(st.session_state.generated_questions)}")
        
        for i, question in enumerate(st.session_state.generated_questions):
            display_question(question, i, show_checkboxes=True)
    else:
        st.warning("Няма генерирани въпроси. Използвай страничния панел за генериране.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px;">
        🧠 Local AI Question Generator | За локална разработка | Deployment: app_real_matura.py
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
