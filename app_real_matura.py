"""
Streamlit app for real DZI matura questions
"""
import streamlit as st
import random
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

def display_question(question, show_answer=False, question_index=None):
    """Display question in beautiful format"""
    # Real matura tag
    st.markdown('<div class="real-matura-tag">📚 Базиран на реална матура</div>', unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="question-box">
        {question.question_text}
    </div>
    ''', unsafe_allow_html=True)
    
    # Display context texts if available
    if question.context_texts:
        st.markdown("### 📄 Контекстни текстове")
        for text_key, text_content in question.context_texts.items():
            st.markdown(f'<div class="context-text"><strong>{text_key}:</strong><br>{text_content}</div>', unsafe_allow_html=True)
    
    if question.options:
        st.markdown('<div class="options-box">', unsafe_allow_html=True)
        st.markdown("**Изберете отговор:**")
        
        # Create checkboxes for each option with unique keys
        selected_options = []
        for i, option in enumerate(question.options):
            # Use question_index for unique keys
            key_suffix = f"_{question_index}" if question_index is not None else ""
            if st.checkbox(f"{option}", key=f"option_{question.id}_{i}{key_suffix}"):
                selected_options.append(option)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Automatic answer checking when option is selected
        if selected_options:
            # Check if selected answer is correct
            if question.correct_answer in selected_options:
                st.success("✅ Правилен отговор!")
            else:
                st.error("❌ Грешен отговор!")
                st.markdown(f"**Правилният отговор е:** {question.correct_answer}")
    
    if show_answer and question.correct_answer:
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown("**Правилен отговор:**")
        st.markdown(question.correct_answer)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if show_answer and question.explanation:
        st.markdown("**Обяснение:**")
        st.markdown(question.explanation)

def main():
    """Main app function"""
    initialize_session_state()
    
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
    if not st.session_state.generated_questions:
        st.info("👆 Изберете параметри и натиснете 'Генерирай въпроси' за да започнете")
        return
    
    questions = st.session_state.generated_questions
    
    # Show all questions mode
    if st.session_state.show_all:
        st.markdown("### 📚 Всички въпроси")
        
        # Add back button
        if st.button("🔙 Назад към единичен режим", key="back_to_single_all"):
            st.session_state.show_all = False
            st.rerun()
        
        st.markdown("---")
        
        # Display all questions with improved design
        for i, question in enumerate(questions):
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
    
    # Question display - clean version
    st.markdown(f"**{current_index + 1}.** **{current_question.question_text}**")
    
    # Real matura tag
    st.markdown('<div class="real-matura-tag">📚 Базиран на реална матура</div>', unsafe_allow_html=True)
    
    # Display options if available
    if current_question.options:
        st.markdown("**Изберете отговор:**")
        
        # Create checkboxes for each option
        selected_options = []
        for i, option in enumerate(current_question.options):
            if st.checkbox(f"{option}", key=f"option_{current_question.id}_{i}"):
                selected_options.append(option)
        
        # Automatic answer checking when option is selected
        if selected_options:
            # Check if selected answer is correct
            if current_question.correct_answer in selected_options:
                st.success("✅ Правилен отговор!")
            else:
                st.error("❌ Грешен отговор!")
                st.markdown(f"**Правилният отговор е:** {current_question.correct_answer}")
    
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
