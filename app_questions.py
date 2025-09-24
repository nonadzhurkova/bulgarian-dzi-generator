"""
Streamlit app for DZI question generation with auto-check
"""
import streamlit as st
import random
from src.question_generator import DZIQuestionGenerator, SubjectArea, QuestionType

# Page config
st.set_page_config(
    page_title="ДЗИ Генератор на Въпроси",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.question-box {
    background-color: #e3f2fd;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 5px solid #2196f3;
}

.options-box {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}

.answer-box {
    background-color: #e8f5e8;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border-left: 5px solid #4caf50;
}

.stats-box {
    background-color: #fff3e0;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'generator' not in st.session_state:
        st.session_state.generator = DZIQuestionGenerator()
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0

def display_question(question, show_answer=False, question_index=None):
    """Показва въпрос в красив формат"""
    st.markdown(f'''
    <div class="question-box">
        <h3>{question.question_text}</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    if question.options:
        st.markdown('<div class="options-box">', unsafe_allow_html=True)
        st.markdown("**Изберете отговор:**")
        
        # Създаваме чекбоксове за всеки отговор с уникален ключ
        selected_options = []
        for i, option in enumerate(question.options):
            # Използваме question_index за уникални ключове
            key_suffix = f"_{question_index}" if question_index is not None else ""
            if st.checkbox(f"{option}", key=f"option_{question.id}_{i}{key_suffix}"):
                selected_options.append(option)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Автоматична проверка при избор на отговор
        if selected_options:
            # Проверяваме дали избраният отговор е правилен
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
    
    st.title("📝 ДЗИ Генератор на Въпроси по БЕЛ")
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
                questions = st.session_state.generator.generate_questions(count, SubjectArea.LANGUAGE)
            else:  # Literature
                questions = st.session_state.generator.generate_questions(count, SubjectArea.LITERATURE)
            
            st.session_state.generated_questions = questions
            st.session_state.current_question_index = 0
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
    current_index = st.session_state.current_question_index
    current_question = questions[current_index]
    
    # Question display
    st.markdown(f"### Въпрос {current_index + 1} от {len(questions)}")
    
    # Question info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Предмет:** {current_question.subject_area.value}")
    with col2:
        st.markdown(f"**Тема:** {current_question.topic.value}")
    with col3:
        st.markdown(f"**Трудност:** {current_question.difficulty}")
    
    # Display question
    display_question(current_question)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Предишен"):
            if current_index > 0:
                st.session_state.current_question_index = current_index - 1
                st.rerun()
    
    with col2:
        if st.button("➡️ Следващ"):
            if current_index < len(questions) - 1:
                st.session_state.current_question_index = current_index + 1
                st.rerun()
    
    with col3:
        if st.button("🎲 Случаен"):
            st.session_state.current_question_index = random.randint(0, len(questions) - 1)
            st.rerun()
    
    # Additional controls
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔀 Разбъркай въпроси"):
            random.shuffle(st.session_state.generated_questions)
            st.session_state.current_question_index = 0
            st.rerun()
    
    with col2:
        if st.button("📊 Покажи всички"):
            for i, q in enumerate(questions):
                st.markdown(f"### Въпрос {i+1}")
                display_question(q, question_index=i)
                st.markdown("---")
    
    with col3:
        if st.button("🎯 Филтрирай по тип"):
            question_types = list(set([q.type.value for q in questions]))
            selected_type = st.selectbox("Изберете тип:", question_types)
            
            filtered_questions = [q for q in questions if q.type.value == selected_type]
            if filtered_questions:
                st.session_state.generated_questions = filtered_questions
                st.session_state.current_question_index = 0
                st.rerun()

if __name__ == "__main__":
    main()
