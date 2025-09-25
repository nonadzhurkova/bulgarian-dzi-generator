"""
Streamlit app for real DZI matura questions
"""
import streamlit as st
import random
import json
import os
from src.real_matura_generator import RealMaturaGenerator, SubjectArea

# Page config
st.set_page_config(
    page_title="Реални ДЗИ Въпроси",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
/* Remove all borders and make design cleaner */
.question-box {
    background-color: #ffffff;
    padding: 16px;
    margin: 8px 0;
    font-size: 16px;
    line-height: 1.5;
    border: none;
    box-shadow: none;
}

.options-box {
    background-color: #ffffff;
    padding: 16px;
    margin: 8px 0;
    border: none;
    box-shadow: none;
}

.answer-box {
    background-color: #e8f5e8;
    padding: 12px;
    margin: 8px 0;
    border: none;
    box-shadow: none;
}

.real-matura-tag {
    background-color: #4caf50;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    display: inline-block;
    margin-bottom: 8px;
    font-weight: 500;
    border: none;
}

.ai-generated-tag {
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 8px;
}

.context-text {
    background-color: #fff3e0;
    padding: 12px;
    margin: 8px 0;
    border: none;
    box-shadow: none;
    font-size: 14px;
}

/* Remove all borders from Streamlit elements */
.stCheckbox > label > div[data-testid="stMarkdownContainer"] {
    border: none !important;
}

.stCheckbox > label {
    border: none !important;
    box-shadow: none !important;
}

.stButton > button {
    border: 1px solid #d1d5db !important;
    box-shadow: none !important;
}

/* Remove extra spacing and make more compact */
.stMarkdown h3 {
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
    font-size: 18px;
}

.stMarkdown p {
    margin-bottom: 0.2rem;
}

/* Reduce spacing in checkboxes */
.stCheckbox {
    margin-bottom: 0.1rem;
}

/* Reduce spacing in success/error messages */
.stSuccess, .stError {
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
}

/* Remove borders from all containers */
div[data-testid="stVerticalBlock"] {
    border: none !important;
}

div[data-testid="stHorizontalBlock"] {
    border: none !important;
}

/* Full width for show all mode */
.main .block-container {
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Better spacing for show all questions */
.stContainer {
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'generator' not in st.session_state:
        st.session_state.generator = RealMaturaGenerator()
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'show_all' not in st.session_state:
        st.session_state.show_all = False
    if 'ai_questions' not in st.session_state:
        st.session_state.ai_questions = []
    if 'all_questions' not in st.session_state:
        st.session_state.all_questions = []

def load_ai_generated_questions():
    """Load AI generated questions from export file"""
    try:
        if os.path.exists("generated_questions_export.json"):
            with open("generated_questions_export.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("questions", [])
    except Exception as e:
        st.error(f"Error loading AI questions: {e}")
    return []

def merge_questions(real_questions, ai_questions):
    """Merge real and AI generated questions"""
    all_questions = []
    
    # Add real questions first (if available)
    if real_questions:
        for i, q in enumerate(real_questions):
            q_copy = q.copy()
            q_copy['id'] = f"real_{i}"
            q_copy['source'] = 'real'
            all_questions.append(q_copy)
    
    # Add AI generated questions (if available)
    if ai_questions:
        for i, q in enumerate(ai_questions):
            q_copy = q.copy()
            q_copy['id'] = f"ai_{i}"
            q_copy['source'] = 'ai_generated'
            all_questions.append(q_copy)
    
    return all_questions

def display_question(question, show_answer=False, question_index=None):
    """Display question in beautiful format"""
    # Show appropriate tag based on source
    if isinstance(question, dict) and question.get('source') == 'ai_generated':
        st.markdown('<div class="ai-generated-tag">🤖 AI Генериран</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="real-matura-tag">📚 Базиран на реална матура</div>', unsafe_allow_html=True)
    
    # Handle both dict and object formats
    if isinstance(question, dict):
        question_text = question.get('question', 'N/A')
        options = question.get('options', [])
        correct_answer = question.get('correct_answer', '')
    else:
        question_text = question.question_text
        options = question.options
        correct_answer = question.correct_answer
    
    st.markdown(f'''
    <div class="question-box">
        {question_text}
    </div>
    ''', unsafe_allow_html=True)
    
    # Display context texts if available (only for real questions)
    if not isinstance(question, dict) and hasattr(question, 'context_texts') and question.context_texts:
        st.markdown("### 📄 Контекстни текстове")
        for text_key, text_content in question.context_texts.items():
            st.markdown(f'<div class="context-text"><strong>{text_key}:</strong><br>{text_content}</div>', unsafe_allow_html=True)
    
    if options:
        st.markdown('<div class="options-box">', unsafe_allow_html=True)
        st.markdown("**Изберете отговор:**")
        
        # Create checkboxes for each option with unique keys
        selected_options = []
        for i, option in enumerate(options):
            # Use question_index for unique keys
            key_suffix = f"_{question_index}" if question_index is not None else ""
            question_id = question.get('id', f"q_{question_index}") if isinstance(question, dict) else question.id
            if st.checkbox(f"{option}", key=f"option_{question_id}_{i}{key_suffix}"):
                selected_options.append(option)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Automatic answer checking when option is selected
        if selected_options:
            # Check if selected answer is correct
            if correct_answer in selected_options:
                st.success("✅ Правилен отговор!")
            else:
                st.error("❌ Грешен отговор!")
                st.markdown(f"**Правилният отговор е:** {correct_answer}")
    
    if show_answer and correct_answer:
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown("**Правилен отговор:**")
        st.markdown(correct_answer)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if show_answer and not isinstance(question, dict) and hasattr(question, 'explanation') and question.explanation:
        st.markdown("**Обяснение:**")
        st.markdown(question.explanation)

def main():
    """Main app function"""
    initialize_session_state()
    
    # Load AI generated questions if available
    if not st.session_state.ai_questions:
        ai_questions = load_ai_generated_questions()
        if ai_questions:
            st.session_state.ai_questions = ai_questions
            # Get real questions safely
            real_questions = st.session_state.generator.load_real_questions()
            st.session_state.all_questions = merge_questions(real_questions, ai_questions)
    
    st.title("📚 Реални ДЗИ Въпроси по БЕЛ")
    st.markdown("Въпроси от истински ДЗИ изпити")
    st.markdown("---")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Контроли")
        
        # Subject selection
        subject = st.selectbox(
            "Изберете предмет:",
            ["Всички", "Български език", "Литература"]
        )
        
        # Question count
        count = st.slider("Брой въпроси:", 1, 20, 5)
        
        # Import AI questions button
        if st.button("🤖 Импортирай AI въпроси", key="import_ai"):
            ai_questions = load_ai_generated_questions()
            if ai_questions:
                st.session_state.ai_questions = ai_questions
                # Get real questions safely
                real_questions = st.session_state.generator.load_real_questions()
                st.session_state.all_questions = merge_questions(real_questions, ai_questions)
                st.success(f"✅ Импортирани {len(ai_questions)} AI въпроса!")
                st.rerun()
            else:
                st.warning("⚠️ Няма намерен файл с AI въпроси (generated_questions_export.json)")
        
        # Generate button
        if st.button("🎲 Генерирай въпроси", type="primary"):
            if subject == "Всички":
                questions = st.session_state.generator.generate_questions(count)
            elif subject == "Български език":
                questions = st.session_state.generator.get_questions_by_subject(SubjectArea.LANGUAGE)[:count]
            else:  # Literature
                questions = st.session_state.generator.get_questions_by_subject(SubjectArea.LITERATURE)[:count]
            
            st.session_state.generated_questions = questions
            st.session_state.current_question_index = 0
            st.session_state.show_all = False
            st.rerun()
        
        # Show all questions button
        if st.session_state.generated_questions:
            if st.button("📊 Покажи всички", key="show_all_sidebar"):
                st.session_state.show_all = True
                st.rerun()
            
            if st.button("🔙 Назад към единичен режим", key="back_to_single"):
                st.session_state.show_all = False
                st.rerun()
        
        # Statistics
        if st.session_state.generated_questions:
            st.markdown("### 📊 Статистики")
            st.markdown(f"**Общо въпроси:** {len(st.session_state.generated_questions)}")
            
            language_count = len([q for q in st.session_state.generated_questions if q.subject_area == SubjectArea.LANGUAGE])
            literature_count = len([q for q in st.session_state.generated_questions if q.subject_area == SubjectArea.LITERATURE])
            
            st.markdown(f"**Български език:** {language_count}")
            st.markdown(f"**Литература:** {literature_count}")
    
    # Main content
    if not st.session_state.generated_questions and not st.session_state.all_questions:
        st.info("👆 Изберете параметри и натиснете 'Генерирай въпроси' или 'Импортирай AI въпроси' за да започнете")
        return
    
    # Use merged questions if available, otherwise use generated questions
    if st.session_state.all_questions:
        questions = st.session_state.all_questions
    else:
        questions = st.session_state.generated_questions
    
    # Show all questions mode
    if st.session_state.show_all:
        # Full width container for all questions
        with st.container():
            st.markdown("### 📚 Всички въпроси")
            
            # Add back button
            if st.button("🔙 Назад към единичен режим", key="back_to_single_all"):
                st.session_state.show_all = False
                st.rerun()
            
            st.markdown("---")
            
            # Display all questions with improved design
            for i, question in enumerate(questions):
                # Question container with full width
                with st.container():
                    # Question header - clean version
                    st.markdown(f"**{i+1}.** **{question.question_text}**")
                    
                    # Real matura tag
                    st.markdown('<div class="real-matura-tag">📚 Базиран на реална матура</div>', unsafe_allow_html=True)
                    
                    # Display options if available
                    if question.options:
                        st.markdown("**Изберете отговор:**")
                        
                        # Create checkboxes for each option
                        selected_options = []
                        for j, option in enumerate(question.options):
                            if st.checkbox(f"{option}", key=f"option_all_{question.id}_{j}"):
                                selected_options.append(option)
                        
                        # Automatic answer checking when option is selected
                        if selected_options:
                            # Check if selected answer is correct
                            if question.correct_answer in selected_options:
                                st.success("✅ Правилен отговор!")
                            else:
                                st.error("❌ Грешен отговор!")
                                st.markdown(f"**Правилният отговор е:** {question.correct_answer}")
                    
                    st.markdown("---")
        return
    
    # Single question mode
    current_index = st.session_state.current_question_index
    current_question = questions[current_index]
    
    # Handle both dict and object formats
    if isinstance(current_question, dict):
        question_text = current_question.get('question', 'N/A')
        options = current_question.get('options', [])
        correct_answer = current_question.get('correct_answer', '')
    else:
        question_text = current_question.question_text
        options = current_question.options
        correct_answer = current_question.correct_answer
    
    # Question display - clean version
    st.markdown(f"**{current_index + 1}.** **{question_text}**")
    
    # Show appropriate tag based on source
    if isinstance(current_question, dict) and current_question.get('source') == 'ai_generated':
        st.markdown('<div class="ai-generated-tag">🤖 AI Генериран</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="real-matura-tag">📚 Базиран на реална матура</div>', unsafe_allow_html=True)
    
    # Display options if available
    if options:
        st.markdown("**Изберете отговор:**")
        
        # Create checkboxes for each option
        selected_options = []
        for i, option in enumerate(options):
            question_id = current_question.get('id', f"q_{current_index}") if isinstance(current_question, dict) else current_question.id
            if st.checkbox(f"{option}", key=f"option_{question_id}_{i}"):
                selected_options.append(option)
        
        # Automatic answer checking when option is selected
        if selected_options:
            # Check if selected answer is correct
            if correct_answer in selected_options:
                st.success("✅ Правилен отговор!")
            else:
                st.error("❌ Грешен отговор!")
                st.markdown(f"**Правилният отговор е:** {correct_answer}")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Предишен", key="prev_button"):
            if current_index > 0:
                st.session_state.current_question_index = current_index - 1
                st.rerun()
    
    with col2:
        if st.button("➡️ Следващ", key="next_button"):
            if current_index < len(questions) - 1:
                st.session_state.current_question_index = current_index + 1
                st.rerun()
    
    with col3:
        if st.button("🎲 Случаен", key="random_button"):
            st.session_state.current_question_index = random.randint(0, len(questions) - 1)
            st.rerun()
    
    # Additional controls
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔀 Разбъркай въпроси", key="shuffle_button"):
            random.shuffle(st.session_state.generated_questions)
            st.session_state.current_question_index = 0
            st.rerun()
    
    with col2:
        if st.button("📊 Покажи всички", key="show_all_main_button"):
            st.session_state.show_all = True
            st.rerun()
    
    with col3:
        if st.button("🎯 Филтрирай по тип", key="filter_button"):
            question_types = list(set([q.type.value for q in questions]))
            selected_type = st.selectbox("Изберете тип:", question_types, key="type_selector")
            
            filtered_questions = [q for q in questions if q.type.value == selected_type]
            if filtered_questions:
                st.session_state.generated_questions = filtered_questions
                st.session_state.current_question_index = 0
                st.rerun()

if __name__ == "__main__":
    main()
