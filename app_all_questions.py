"""
All Questions Viewer - Shows both real and generated questions
Simple interface to view all questions at once
"""
import streamlit as st
import json
import os
import time
from typing import List, Dict, Any

# Set page config
st.set_page_config(
    page_title="📚 All Questions Viewer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .real-matura-tag {
        background-color: #e8f4fd;
        color: #1f77b4;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin: 5px 0;
    }
    .generated-tag {
        background-color: #f0f8e8;
        color: #2e7d32;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin: 5px 0;
    }
    .question-number {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .question-text {
        font-size: 16px;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    .options {
        margin: 10px 0;
    }
    .option {
        margin: 5px 0;
        padding: 5px 0;
    }
    .correct-answer {
        background-color: #d4edda;
        color: #155724;
        padding: 8px;
        border-radius: 4px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
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
    
    # Remove duplicates from real questions too
    unique_questions = []
    seen_questions = set()
    
    for q in questions:
        # Create a unique identifier for the question
        question_text = q.get('question', '').strip().lower()
        options = sorted([opt.strip().lower() for opt in q.get('options', [])])
        question_id = f"{question_text}_{'_'.join(options)}"
        
        if question_id not in seen_questions:
            seen_questions.add(question_id)
            unique_questions.append(q)
    
    return unique_questions

def load_generated_questions():
    """Load generated questions from the question generator"""
    try:
        # Import the question generator
        import sys
        sys.path.append('src')
        from src.question_generator import DZIQuestionGenerator, SubjectArea
        
        # Create generator and generate some questions
        generator = DZIQuestionGenerator()
        
        # Generate some questions for each subject
        generated_questions = []
        
        # Generate Bulgarian Language questions
        language_questions = generator.generate_questions(count=10, subject=SubjectArea.LANGUAGE)
        for q in language_questions:
            generated_questions.append({
                'question': q.question_text,
                'options': q.options,
                'correct_answer': q.correct_answer,
                'subject': 'Български език',
                'difficulty': q.difficulty,
                'points': q.points,
                'type': 'multiple_choice'
            })
        
        # Generate Literature questions
        literature_questions = generator.generate_questions(count=10, subject=SubjectArea.LITERATURE)
        for q in literature_questions:
            generated_questions.append({
                'question': q.question_text,
                'options': q.options,
                'correct_answer': q.correct_answer,
                'subject': 'Литература',
                'difficulty': q.difficulty,
                'points': q.points,
                'type': 'multiple_choice'
            })
        
        return generated_questions
        
    except Exception as e:
        st.error(f"❌ Error generating questions: {e}")
        return []

def display_question(question, index, question_type="real", show_checkboxes=True):
    """Display a single question with proper formatting"""
    with st.container():
        st.markdown(f"""
        <div class="question-box">
            <div class="question-number">Въпрос {index + 1}</div>
            <div class="question-text"><strong>{question.get('question', 'N/A')}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show question type tag
        if question_type == "real":
            st.markdown('<div class="real-matura-tag">📚 Реална матура</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="generated-tag">🤖 Генериран</div>', unsafe_allow_html=True)
        
        # Display options with checkboxes if available
        if question.get('options') and show_checkboxes:
            st.markdown("**Изберете отговор:**")
            selected_options = []
            
            for j, option in enumerate(question['options']):
                # Create a simple but unique key
                unique_key = f"option_{question_type}_{index}_{j}_{int(time.time() * 1000000) % 1000000}"
                
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
    st.markdown('<h1 class="main-header">📚 Всички въпроси - Реални и генерирани</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'real_questions' not in st.session_state:
        st.session_state.real_questions = []
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    
    # Auto-load data on first run
    if not st.session_state.real_questions:
        # Try to load saved state first
        try:
            import json
            with open('app_state.json', 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            st.session_state.real_questions = state_data.get('real_questions', [])
            st.session_state.generated_questions = state_data.get('generated_questions', [])
            st.success(f"✅ Заредено запазено състояние: {len(st.session_state.real_questions)} реални, {len(st.session_state.generated_questions)} генерирани въпроси")
        except:
            # If no saved state, load real questions
            with st.spinner("Зареждане на реални въпроси..."):
                st.session_state.real_questions = load_real_questions()
                st.success(f"✅ Заредени {len(st.session_state.real_questions)} реални въпроси")
    
    if not st.session_state.generated_questions:
        with st.spinner("Генериране на начални въпроси..."):
            try:
                import sys
                sys.path.append('src')
                from src.question_generator import DZIQuestionGenerator, SubjectArea
                
                generator = DZIQuestionGenerator()
                
                # Generate some initial questions
                language_questions = generator.generate_questions(count=10, subject=SubjectArea.LANGUAGE)
                literature_questions = generator.generate_questions(count=10, subject=SubjectArea.LITERATURE)
                
                # Convert to dict format
                initial_questions = []
                for q in language_questions:
                    initial_questions.append({
                        'question': q.question_text,
                        'options': q.options,
                        'correct_answer': q.correct_answer,
                        'subject': 'Български език',
                        'difficulty': q.difficulty,
                        'points': q.points,
                        'type': 'multiple_choice'
                    })
                
                for q in literature_questions:
                    initial_questions.append({
                        'question': q.question_text,
                        'options': q.options,
                        'correct_answer': q.correct_answer,
                        'subject': 'Литература',
                        'difficulty': q.difficulty,
                        'points': q.points,
                        'type': 'multiple_choice'
                    })
                
                st.session_state.generated_questions = initial_questions
                st.success(f"✅ Генерирани {len(initial_questions)} начални въпроси")
                
            except Exception as e:
                st.warning(f"⚠️ Не можах да генерирам начални въпроси: {e}")
                st.session_state.generated_questions = []
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎛️ Контроли")
        
        # Generate more questions
        st.subheader("🤖 Генерирай нови въпроси")
        num_language = st.number_input("Брой въпроси за език:", min_value=1, max_value=50, value=10, key="num_language")
        num_literature = st.number_input("Брой въпроси за литература:", min_value=1, max_value=50, value=10, key="num_literature")
        
        # Generation method selection
        generation_method = st.selectbox(
            "Метод на генериране:",
            ["Базов генератор", "RAG генериране (Phase 2)"],
            key="generation_method"
        )
        
        if st.button("🚀 Генерирай нови въпроси", key="generate_new"):
            with st.spinner("Генериране на нови въпроси..."):
                try:
                    import sys
                    sys.path.append('src')
                    from src.question_generator import DZIQuestionGenerator, SubjectArea
                    
                    generator = DZIQuestionGenerator()
                    
                    if generation_method == "RAG генериране (Phase 2)":
                        # Try to use simple RAG generator
                        try:
                            from src.simple_rag_generator import SimpleRAGGenerator
                            rag_generator = SimpleRAGGenerator()
                            
                            # Generate new questions using RAG
                            new_language_questions = rag_generator.generate_questions(count=num_language, subject=SubjectArea.LANGUAGE)
                            new_literature_questions = rag_generator.generate_questions(count=num_literature, subject=SubjectArea.LITERATURE)
                            
                            st.success("🧠 Използвам RAG генериране (Phase 2) с OpenAI API!")
                            
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
                    if generation_method == "RAG генериране (Phase 2)":
                        # RAG generator returns dictionaries directly
                        for q in new_language_questions:
                            q['subject'] = 'Български език'
                            new_questions.append(q)
                        
                        for q in new_literature_questions:
                            q['subject'] = 'Литература'
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
                                'subject': 'Литература',
                                'difficulty': q.difficulty,
                                'points': q.points,
                                'type': 'multiple_choice'
                            })
                    
                    # Add to existing generated questions (avoid duplicates)
                    if 'generated_questions' not in st.session_state:
                        st.session_state.generated_questions = []
                    
                    # Check for duplicates before adding (by question text AND options)
                    def is_duplicate_question(new_q, existing_questions):
                        """Check if question is duplicate by comparing question text and options"""
                        for existing_q in existing_questions:
                            # Compare question text
                            if new_q.get('question', '').strip().lower() == existing_q.get('question', '').strip().lower():
                                # Compare options if they exist
                                new_options = new_q.get('options', [])
                                existing_options = existing_q.get('options', [])
                                if len(new_options) == len(existing_options):
                                    # Check if all options match (order doesn't matter)
                                    new_options_sorted = sorted([opt.strip().lower() for opt in new_options])
                                    existing_options_sorted = sorted([opt.strip().lower() for opt in existing_options])
                                    if new_options_sorted == existing_options_sorted:
                                        return True
                        return False
                    
                    unique_new_questions = []
                    skipped_count = 0
                    
                    for new_q in new_questions:
                        if not is_duplicate_question(new_q, st.session_state.generated_questions):
                            unique_new_questions.append(new_q)
                        else:
                            skipped_count += 1
                    
                    st.session_state.generated_questions.extend(unique_new_questions)
                    
                    # Add generated questions to RAG database for future context
                    if generation_method == "RAG генериране (Phase 2)":
                        try:
                            # Add questions to RAG database
                            rag_generator.add_questions_to_database(unique_new_questions)
                            st.info("🧠 Новогенерираните въпроси са добавени във векторната база!")
                        except Exception as e:
                            st.warning(f"⚠️ Не можах да добавя въпросите във векторната база: {e}")
                    
                    st.success(f"✅ Генерирани {len(unique_new_questions)} нови уникални въпроси!")
                    if skipped_count > 0:
                        st.info(f"ℹ️ Игнорирани {skipped_count} дублиращи се въпроси (еднакви текст и опции)")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Грешка при генериране: {e}")
        
        st.markdown("---")
        
        # Load real questions
        if st.button("📚 Зареди реални въпроси", key="load_real"):
            with st.spinner("Зареждане на реални въпроси..."):
                st.session_state.real_questions = load_real_questions()
                st.success(f"✅ Заредени {len(st.session_state.real_questions)} реални въпроси")
                st.rerun()
        
        # Clear all questions
        if st.button("🗑️ Изчисти всички въпроси", key="clear_all"):
            st.session_state.real_questions = []
            st.session_state.generated_questions = []
            st.success("✅ Всички въпроси изчистени")
            st.rerun()
        
        # Save/Load state
        st.markdown("---")
        st.subheader("💾 Запазване на състоянието")
        
        if st.button("💾 Запази състоянието", key="save_state"):
            try:
                import json
                state_data = {
                    'real_questions': st.session_state.real_questions,
                    'generated_questions': st.session_state.generated_questions
                }
                with open('app_state.json', 'w', encoding='utf-8') as f:
                    json.dump(state_data, f, ensure_ascii=False, indent=2)
                st.success("✅ Състоянието е запазено в app_state.json")
            except Exception as e:
                st.error(f"❌ Грешка при запазване: {e}")
        
        if st.button("📂 Зареди запазено състояние", key="load_state"):
            try:
                import json
                with open('app_state.json', 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                st.session_state.real_questions = state_data.get('real_questions', [])
                st.session_state.generated_questions = state_data.get('generated_questions', [])
                st.success("✅ Състоянието е заредено от app_state.json")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Грешка при зареждане: {e}")
    
    # Load questions
    if st.button("🔄 Зареди всички въпроси", key="load_all"):
        with st.spinner("Зареждане на въпроси..."):
            st.session_state.real_questions = load_real_questions()
            st.session_state.generated_questions = load_generated_questions()
            
            total_real = len(st.session_state.real_questions)
            total_generated = len(st.session_state.generated_questions)
            
            st.success(f"✅ Заредени {total_real} реални въпроси и {total_generated} генерирани въпроси")
    
    if not st.session_state.real_questions and not st.session_state.generated_questions:
        st.info("👆 Натисни 'Зареди всички въпроси' за да започнеш")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📚 Всички въпроси", "🎯 Реални въпроси", "🤖 Генерирани въпроси"])
    
    with tab1:
        st.header("📚 Всички въпроси")
        
        all_questions = []
        question_types = []
        
        # Add real questions
        for i, question in enumerate(st.session_state.real_questions):
            all_questions.append(question)
            question_types.append("real")
        
        # Add generated questions
        for i, question in enumerate(st.session_state.generated_questions):
            all_questions.append(question)
            question_types.append("generated")
        
        if all_questions:
            st.markdown(f"**Общо въпроси:** {len(all_questions)}")
            
            # Display all questions
            for i, (question, q_type) in enumerate(zip(all_questions, question_types)):
                display_question(question, i, q_type, show_checkboxes=True)
        else:
            st.warning("Няма заредени въпроси")
    
    with tab2:
        st.header("🎯 Реални въпроси")
        
        if st.session_state.real_questions:
            st.markdown(f"**Брой реални въпроси:** {len(st.session_state.real_questions)}")
            
            for i, question in enumerate(st.session_state.real_questions):
                display_question(question, i, "real", show_checkboxes=True)
        else:
            st.warning("Няма заредени реални въпроси")
    
    with tab3:
        st.header("🤖 Генерирани въпроси")
        
        if st.session_state.generated_questions:
            st.markdown(f"**Брой генерирани въпроси:** {len(st.session_state.generated_questions)}")
            
            for i, question in enumerate(st.session_state.generated_questions):
                display_question(question, i, "generated", show_checkboxes=True)
        else:
            st.warning("Няма заредени генерирани въпроси")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 14px;">
        📚 Bulgarian DZI Question Generator - All Questions Viewer
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
