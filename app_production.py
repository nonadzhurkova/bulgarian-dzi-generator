"""
Production Streamlit app for DZI matura questions
Reads real questions + AI questions from ai-data folder
No AI generation, no imports - just displays questions
"""
import streamlit as st
import json
import os
import glob
from src.real_matura_generator import RealMaturaGenerator, SubjectArea

# Page config
st.set_page_config(
    page_title="ДЗИ Матура Въпроси",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
/* Clean design without borders */
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
    border-radius: 4px;
    border: none;
}

/* Remove all borders and make design cleaner */
.stContainer {
    width: 100% !important;
}

/* Reduce spacing between Streamlit elements */
.stApp > div > div > div > div {
    margin: 0 !important;
    padding: 0 !important;
}

.stApp > div > div > div > div > div {
    margin: 0 !important;
    padding: 0 !important;
}

/* Reduce spacing between specific elements */
.stMarkdown {
    margin: 0 !important;
    padding: 0 !important;
}

.stButton {
    margin: 2px 0 !important;
}

.stCheckbox {
    margin: 1px 0 !important;
}

/* Reduce spacing in columns */
.stColumn {
    margin: 0 !important;
    padding: 0 4px !important;
}

/* Reduce spacing between all Streamlit elements */
div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

div[data-testid="stVerticalBlock"] > div {
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
}

div[data-testid="stHorizontalBlock"] > div {
    margin: 0 !important;
    padding: 0 !important;
}

/* Reduce spacing in main content area */
.main .block-container {
    padding: 1rem 1rem 1rem 1rem !important;
}

/* Reduce spacing between elements */
.stApp > div > div > div > div > div > div {
    margin: 0 !important;
    padding: 0 !important;
}

/* Compact mode styling */
.compact-question {
    margin: 8px 0;
    padding: 12px;
    background-color: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #4caf50;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

/* .compact-question:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
} */

.compact-question.real {
    border-left-color: #4caf50; /* Green for real questions */
    background: linear-gradient(135deg, #f8f9fa 0%, #e8f5e8 100%);
}

.compact-question.ai {
    border-left-color: #ff6b6b; /* Red for AI questions */
    background: linear-gradient(135deg, #f8f9fa 0%, #ffe8e8 100%);
}

.compact-options {
    margin: 4px 0;
    padding: 4px 0;
}

.compact-options .stCheckbox {
    margin: 1px 0 !important;
}

.compact-options .stCheckbox > label {
    padding: 4px 8px;
    font-size: 13px;
    line-height: 1.2;
}

/* Enhanced checkbox styling */
.stCheckbox {
    margin: 2px 0 !important;
}

.stCheckbox > label {
    font-size: 14px;
    line-height: 1.3;
    padding: 6px 10px;
    border-radius: 6px;
    transition: all 0.2s ease;
    cursor: pointer;
    margin: 1px 0 !important;
}

/* .stCheckbox > label:hover {
    background-color: #e3f2fd;
    transform: translateX(4px);
} */

.stCheckbox > input[type="checkbox"]:checked + label {
    background-color: #e8f5e8;
    color: #2e7d32;
    font-weight: 500;
}

/* Progress indicator */
.progress-bar {
    width: 100%;
    height: 4px;
    background-color: #e0e0e0;
    border-radius: 2px;
    overflow: hidden;
    margin: 6px 0;
    border: none;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4caf50, #8bc34a);
    border-radius: 4px;
    transition: width 0.5s ease;
    box-shadow: 0 1px 3px rgba(76, 175, 80, 0.3);
}

/* Enhanced buttons */
.stButton > button {
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    padding: 6px 12px;
    font-size: 14px;
}

/* .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
} */

/* Question counter styling */
.question-counter {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: 500;
    text-align: center;
    margin: 8px 0;
    font-size: 14px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Success/Error animations - DISABLED */
/* @keyframes successPulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

@keyframes errorShake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.success-animation {
    animation: successPulse 0.6s ease-in-out;
}

.error-animation {
    animation: errorShake 0.6s ease-in-out;
} */

/* Enhanced success/error messages */
.stSuccess {
    background: linear-gradient(135deg, #4caf50, #8bc34a);
    color: white;
    border-radius: 8px;
    padding: 12px 16px;
    font-weight: 500;
    box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.stError {
    background: linear-gradient(135deg, #f44336, #ff7043);
    color: white;
    border-radius: 8px;
    padding: 12px 16px;
    font-weight: 500;
    box-shadow: 0 4px 8px rgba(244, 67, 54, 0.3);
}
</style>
""", unsafe_allow_html=True)

def is_duplicate_question(question, existing_questions):
    """Check if question is duplicate based on question text and options"""
    question_text = question.get('question', '').strip().lower()
    question_options = sorted([opt.strip().lower() for opt in question.get('options', [])])
    
    for existing in existing_questions:
        existing_text = existing.get('question', '').strip().lower()
        existing_options = sorted([opt.strip().lower() for opt in existing.get('options', [])])
        
        # Check if question text and options are identical
        if question_text == existing_text and question_options == existing_options:
            return True
    
    return False

def load_all_questions():
    """Load all questions: real + AI from ai-data folder"""
    all_questions = []
    duplicates_removed = 0
    
    # Load real questions
    generator = RealMaturaGenerator()
    real_questions = generator.load_real_questions()
    
    # Check if real_questions is not None
    if real_questions:
        # Add real questions with metadata
        for i, q in enumerate(real_questions):
            # Handle both dict and object formats
            if isinstance(q, dict):
                q_dict = {
                    'id': f"real_{i}",
                    'source': 'real',
                    'question': q.get('question', 'N/A'),
                    'options': q.get('options', []),
                    'correct_answer': q.get('correct_answer', ''),
                    'subject': q.get('subject', 'Unknown'),
                    'difficulty': q.get('difficulty', 'medium'),
                    'points': q.get('points', 1),
                    'context_texts': q.get('context_texts', {})
                }
            else:
                q_dict = {
                    'id': f"real_{i}",
                    'source': 'real',
                    'question': q.question_text,
                    'options': q.options,
                    'correct_answer': q.correct_answer,
                    'subject': q.subject_area.value if hasattr(q, 'subject_area') else 'Unknown',
                    'difficulty': getattr(q, 'difficulty', 'medium'),
                    'points': getattr(q, 'points', 1),
                    'context_texts': getattr(q, 'context_texts', {})
                }
            
            # Check for duplicates before adding
            if not is_duplicate_question(q_dict, all_questions):
                all_questions.append(q_dict)
            else:
                duplicates_removed += 1
    
    # Load AI questions from ai-data folder
    ai_files = glob.glob("ai-data/ai_questions_*.json")
    for ai_file in ai_files:
        try:
            with open(ai_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                ai_questions = data.get('questions', [])
                
                # Add AI questions with metadata
                for i, q in enumerate(ai_questions):
                    q_dict = {
                        'id': f"ai_{ai_file}_{i}",
                        'source': 'ai_generated',
                        'question': q.get('question', 'N/A'),
                        'options': q.get('options', []),
                        'correct_answer': q.get('correct_answer', ''),
                        'subject': q.get('subject', 'Unknown'),
                        'difficulty': q.get('difficulty', 'medium'),
                        'points': q.get('points', 1)
                    }
                    
                    # Check for duplicates before adding
                    if not is_duplicate_question(q_dict, all_questions):
                        all_questions.append(q_dict)
                    else:
                        duplicates_removed += 1
                    
        except Exception as e:
            st.error(f"Error loading {ai_file}: {e}")
    
    # Show duplicates removed info (hidden)
    # if duplicates_removed > 0:
    #     st.info(f"ℹ️ Премахнати {duplicates_removed} дублирани въпроси")
    
    return all_questions

def display_question(question, show_answer=False, question_index=None, compact_mode=False):
    """Display question in beautiful format"""
    # Show appropriate tag based on source (only in single mode)
    if not compact_mode:
        if question.get('source') == 'ai_generated':
            st.markdown('<div class="ai-generated-tag">🤖 AI Генериран</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="real-matura-tag">📚 Базиран на реална матура</div>', unsafe_allow_html=True)
    
    # Question text - compact version for "show all" mode
    if compact_mode:
        # Add icon and color class based on source
        icon = "📚" if question.get('source') == 'real' else "🤖"
        color_class = "real" if question.get('source') == 'real' else "ai"
        st.markdown(f'''
        <div class="compact-question {color_class}">
            <strong>{icon} {question_index + 1}.</strong> {question.get('question', 'N/A')}
        </div>
        ''', unsafe_allow_html=True)
    else:
            st.markdown(f'''
            <div class="question-box" style="padding: 8px 12px; margin: 8px 0;">
                <strong style="font-size: 16px;">{question.get('question', 'N/A')}</strong>
            </div>
            ''', unsafe_allow_html=True)
    
    # Display context texts if available (only for real questions and not in compact mode)
    if not compact_mode:
        context_texts = question.get('context_texts', {})
        if context_texts:
            st.markdown("### 📄 Контекстни текстове")
            for text_key, text_content in context_texts.items():
                st.markdown(f'<div class="context-text"><strong>{text_key}:</strong><br>{text_content}</div>', unsafe_allow_html=True)
    
    # Display options
    options = question.get('options', [])
    if options:
        if compact_mode:
            st.markdown('<div class="compact-options">', unsafe_allow_html=True)
        else:
            st.markdown('<div class="options-box" style="margin: 4px 0;">', unsafe_allow_html=True)
            # st.markdown("**Изберете отговор:**", help="Кликнете върху опцията, която смятате за правилна")
        
        # Create checkboxes for each option with enhanced styling
        selected_options = []
        for i, option in enumerate(options):
            question_id = question.get('id', f"q_{question_index}")
            if st.checkbox(f"{option}", key=f"option_{question_id}_{i}"):
                selected_options.append(option)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Automatic answer checking when option is selected
        if selected_options:
            correct_answer = question.get('correct_answer', '')
            if correct_answer in selected_options:
                st.success("✅ Правилен отговор!")
            else:
                st.error("❌ Грешен отговор!")
                st.markdown(f"**Правилният отговор е:** {correct_answer}")
    
    # Show answer if requested
    if show_answer and question.get('correct_answer'):
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown("**Правилен отговор:**")
        st.markdown(question.get('correct_answer', ''))
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main app function"""
    st.title("📚 ДЗИ Матура Въпроси по БЕЛ")
    st.markdown("Въпроси от истински ДЗИ изпити + AI генерирани въпроси")
    st.markdown("---")
    
    # Load all questions
    if 'all_questions' not in st.session_state:
        with st.spinner("Зареждане на въпроси..."):
            st.session_state.all_questions = load_all_questions()
            st.session_state.current_question_index = 0
            st.session_state.show_all = False
    
    questions = st.session_state.all_questions
    
    if not questions:
        st.error("❌ Няма намерени въпроси!")
        return
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Контроли")
        
        # Statistics
        st.markdown("### 📊 Статистики")
        st.markdown(f"**Общо въпроси:** {len(questions)}")
        
        real_count = len([q for q in questions if q.get('source') == 'real'])
        ai_count = len([q for q in questions if q.get('source') == 'ai_generated'])
        
        st.markdown(f"**Реални въпроси:** {real_count}")
        st.markdown(f"**AI въпроси:** {ai_count}")
        
        # Subject filter
        subjects = list(set([q.get('subject', 'Unknown') for q in questions]))
        selected_subject = st.selectbox("Филтър по предмет:", ["Всички"] + subjects)
        
        # Filter questions by subject
        if selected_subject != "Всички":
            filtered_questions = [q for q in questions if q.get('subject') == selected_subject]
        else:
            filtered_questions = questions
        
        st.markdown(f"**Показвани въпроси:** {len(filtered_questions)}")
        
        # Show all questions button
        if st.button("📊 Покажи всички", key="show_all_sidebar"):
            st.session_state.show_all = True
            st.rerun()
        
        if st.button("🔙 Назад към единичен режим", key="back_to_single"):
            st.session_state.show_all = False
            st.rerun()
    
    # Show all questions mode
    if st.session_state.show_all:
        with st.container():
            st.markdown("## 📋 Всички въпроси")
            
            # Control buttons
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🔙 Назад към единичен режим", key="back_to_single_all"):
                    st.session_state.show_all = False
                    st.rerun()
            
            with col2:
                if st.button("🎲 Разбъркай въпросите", key="shuffle_all_questions"):
                    import random
                    random.shuffle(filtered_questions)
                    st.rerun()
            
            st.markdown("---")
            
            for i, question in enumerate(filtered_questions):
                display_question(question, show_answer=False, question_index=i, compact_mode=True)
                st.markdown("---")
    else:
        # Single question mode
        if not filtered_questions:
            st.warning("Няма въпроси за избрания предмет.")
            return
        
        current_index = st.session_state.current_question_index
        if current_index >= len(filtered_questions):
            st.session_state.current_question_index = 0
            current_index = 0
        
        current_question = filtered_questions[current_index]
        
        # Question display
        st.markdown(f"**{current_index + 1}.** **{current_question.get('question', 'N/A')}**")
        
        # Show appropriate tag
        if current_question.get('source') == 'ai_generated':
            st.markdown('<div class="ai-generated-tag">🤖 AI Генериран</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="real-matura-tag">📚 Базиран на реална матура</div>', unsafe_allow_html=True)
        
        # Display options
        options = current_question.get('options', [])
        if options:
            # st.markdown("**Изберете отговор:**")
            
            selected_options = []
            for i, option in enumerate(options):
                question_id = current_question.get('id', f"q_{current_index}")
                if st.checkbox(f"{option}", key=f"option_{question_id}_{i}"):
                    selected_options.append(option)
            
            # Automatic answer checking
            if selected_options:
                correct_answer = current_question.get('correct_answer', '')
                if correct_answer in selected_options:
                    st.success("✅ Правилен отговор!")
                else:
                    st.error("❌ Грешен отговор!")
                    st.markdown(f"**Правилният отговор е:** {correct_answer}")
        
        # Navigation
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("⬅️ Предишен", key="prev_button"):
                st.session_state.current_question_index = max(0, st.session_state.current_question_index - 1)
                st.rerun()
        
        with col2:
            if st.button("🎲 Случаен", key="random_button"):
                st.session_state.current_question_index = st.session_state.rng.randint(0, len(filtered_questions) - 1)
                st.rerun()
        
        with col3:
            if st.button("🔄 Разбъркай", key="shuffle_button"):
                import random
                random.shuffle(filtered_questions)
                st.session_state.current_question_index = 0
                st.rerun()
        
        with col4:
            if st.button("➡️ Следващ", key="next_button"):
                st.session_state.current_question_index = min(len(filtered_questions) - 1, st.session_state.current_question_index + 1)
                st.rerun()
        
        # Progress bar and counter
        progress = (current_index + 1) / len(filtered_questions)
        st.markdown(f'''
        <div style="margin: 8px 0;">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress * 100}%"></div>
            </div>
            <div style="text-align: center; margin-top: 2px; font-size: 11px; color: #666;">
                {int(progress * 100)}% завършено
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # st.markdown(f'''
        # <div class="question-counter">
        #     Въпрос {current_index + 1} от {len(filtered_questions)}
        # </div>
        # ''', unsafe_allow_html=True)

if __name__ == "__main__":
    # Initialize random number generator
    if 'rng' not in st.session_state:
        import random
        st.session_state.rng = random.Random()
    
    main()
