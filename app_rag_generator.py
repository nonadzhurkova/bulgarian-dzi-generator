"""
Streamlit App for RAG-based Question Generation
Phase 2: Generation - Interactive interface for generating new questions
"""

import streamlit as st
import json
import os
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import our custom modules
from src.vector_analyzer import MaturaVectorAnalyzer
from src.question_generator_rag import RAGQuestionGenerator, GeneratedQuestion

def main():
    st.set_page_config(
        page_title="RAG Question Generator",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 RAG Question Generator")
    st.markdown("**Phase 2: Generation** - Generate new questions using RAG and AI")
    
    # Initialize session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'generator' not in st.session_state:
        st.session_state.generator = None
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Model selection
        embedding_model = st.selectbox(
            "Embedding Model",
            ["sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"],
            help="Model for creating embeddings"
        )
        
        llm_model = st.selectbox(
            "LLM Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            help="Language model for question generation"
        )
        
        # Initialize button
        if st.button("🚀 Initialize System", key="init_system"):
            with st.spinner("Initializing system..."):
                st.session_state.analyzer = MaturaVectorAnalyzer(embedding_model)
                st.session_state.generator = RAGQuestionGenerator(embedding_model, llm_model, use_cache=True)
                
                # Load questions
                json_files = [
                    "data/matura_21_05_2025.json",
                    "data/matura_2025_avgust.json"
                ]
                
                st.session_state.analyzer.load_real_questions(json_files)
                st.session_state.generator.load_real_questions(json_files)
                
                # Create embeddings (will use cache if available)
                st.session_state.analyzer.create_embeddings()
                st.session_state.generator.create_embeddings()
                
                st.success("✅ System initialized successfully!")
    
    # Main content
    if st.session_state.analyzer is None or st.session_state.generator is None:
        st.warning("⚠️ Please initialize the system first using the sidebar.")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "🔍 Similarity Search", "🎯 Question Generation", "📈 Quality Assessment"])
    
    with tab1:
        st.header("📊 Question Analysis")
        
        if st.button("🔍 Analyze Questions", key="analyze_questions"):
            with st.spinner("Analyzing questions..."):
                analysis = st.session_state.analyzer.analyze_question_patterns()
                
                # Display basic statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Questions", analysis['total_questions'])
                
                with col2:
                    st.metric("Avg Question Length", f"{analysis['avg_question_length']:.1f} words")
                
                with col3:
                    st.metric("Avg Answer Length", f"{analysis['avg_answer_length']:.1f} words")
                
                # Question types
                st.subheader("📋 Question Types")
                q_types = analysis['question_types']
                fig_types = px.pie(
                    values=list(q_types.values()),
                    names=list(q_types.keys()),
                    title="Distribution of Question Types"
                )
                st.plotly_chart(fig_types, use_container_width=True)
                
                # Most common topics
                st.subheader("🎯 Most Common Topics")
                topics = analysis['most_common_topics']
                if topics:
                    topics_df = pd.DataFrame(topics, columns=['Topic', 'Count'])
                    fig_topics = px.bar(
                        topics_df,
                        x='Count',
                        y='Topic',
                        orientation='h',
                        title="Most Common Topics"
                    )
                    st.plotly_chart(fig_topics, use_container_width=True)
                
                # Question structures
                st.subheader("📝 Question Structures")
                structures = analysis['structure_patterns']
                fig_structures = px.bar(
                    x=list(structures.keys()),
                    y=list(structures.values()),
                    title="Question Structure Patterns"
                )
                st.plotly_chart(fig_structures, use_container_width=True)
    
    with tab2:
        st.header("🔍 Similarity Search")
        
        # Search interface
        query = st.text_input(
            "Enter a question or topic to search for similar questions:",
            placeholder="e.g., Кой конфликт е заложен в интерпретацията на темата за човека и властта"
        )
        
        top_k = st.slider("Number of similar questions to find:", 1, 10, 5)
        
        if st.button("🔍 Search Similar Questions", key="search_similar"):
            if query:
                with st.spinner("Searching for similar questions..."):
                    similar_questions = st.session_state.generator.find_similar_questions(query, top_k)
                    
                    st.subheader(f"🔍 Found {len(similar_questions)} similar questions:")
                    
                    for i, (idx, similarity) in enumerate(similar_questions):
                        question = st.session_state.analyzer.questions[idx]
                        
                        with st.expander(f"Question {i+1} (Similarity: {similarity:.3f})"):
                            st.write(f"**Question:** {question.get('question', '')}")
                            
                            if question.get('type') == 'multiple_choice' and 'options' in question:
                                st.write("**Options:**")
                                for j, option in enumerate(question['options']):
                                    st.write(f"{chr(65+j)}) {option}")
                            
                            if 'correct_answer' in question:
                                st.write(f"**Correct Answer:** {question['correct_answer']}")
                            
                            if 'points' in question:
                                st.write(f"**Points:** {question['points']}")
            else:
                st.warning("Please enter a search query.")
    
    with tab3:
        st.header("🎯 Question Generation")
        
        # Generation options
        col1, col2 = st.columns(2)
        
        with col1:
            generation_method = st.selectbox(
                "Generation Method",
                ["Similarity-based", "Topic-based", "Random"],
                help="Method for generating new questions"
            )
        
        with col2:
            num_variants = st.slider("Number of variants to generate:", 1, 5, 2)
        
        if generation_method == "Similarity-based":
            st.subheader("🔍 Generate from Similar Questions")
            
            base_question = st.text_area(
                "Enter a base question:",
                placeholder="Enter a question to generate variants from...",
                height=100
            )
            
            if st.button("🎯 Generate Variants", key="generate_variants"):
                if base_question:
                    with st.spinner("Generating question variants..."):
                        variants = st.session_state.generator.generate_question_variants(
                            base_question, 
                            num_variants
                        )
                        
                        st.session_state.generated_questions = variants
                        
                        st.subheader(f"🎯 Generated {len(variants)} variants:")
                        
                        for i, variant in enumerate(variants):
                            with st.expander(f"Generated Question {i+1}"):
                                st.write(f"**Question:** {variant.question}")
                                st.write("**Options:**")
                                for j, option in enumerate(variant.options):
                                    st.write(f"{chr(65+j)}) {option}")
                                st.write(f"**Correct Answer:** {variant.correct_answer}")
                                st.write(f"**Explanation:** {variant.explanation}")
                                st.write(f"**Topic:** {variant.topic}")
                                st.write(f"**Difficulty:** {variant.difficulty}")
                                
                                # Quality validation
                                validation = st.session_state.generator.validate_question_quality(variant)
                                if validation['is_valid']:
                                    st.success(f"✅ Quality Score: {validation['score']:.2f}")
                                else:
                                    st.error(f"❌ Issues: {', '.join(validation['issues'])}")
                else:
                    st.warning("Please enter a base question.")
        
        elif generation_method == "Topic-based":
            st.subheader("🎯 Generate by Topic")
            
            topic = st.text_input(
                "Enter a topic:",
                placeholder="e.g., literature, language, analysis"
            )
            
            if st.button("🎯 Generate by Topic", key="generate_by_topic"):
                if topic:
                    with st.spinner("Generating questions by topic..."):
                        generated = st.session_state.generator.generate_questions_by_topic(
                            topic, 
                            num_variants
                        )
                        
                        st.session_state.generated_questions = generated
                        
                        st.subheader(f"🎯 Generated {len(generated)} questions for topic '{topic}':")
                        
                        for i, question in enumerate(generated):
                            with st.expander(f"Question {i+1}"):
                                st.write(f"**Question:** {question.question}")
                                st.write("**Options:**")
                                for j, option in enumerate(question.options):
                                    st.write(f"{chr(65+j)}) {option}")
                                st.write(f"**Correct Answer:** {question.correct_answer}")
                                st.write(f"**Explanation:** {question.explanation}")
                                st.write(f"**Topic:** {question.topic}")
                else:
                    st.warning("Please enter a topic.")
    
    with tab4:
        st.header("📈 Quality Assessment")
        
        if st.session_state.generated_questions:
            st.subheader("📊 Generated Questions Quality Analysis")
            
            # Quality metrics
            quality_scores = []
            valid_questions = 0
            
            for question in st.session_state.generated_questions:
                validation = st.session_state.generator.validate_question_quality(question)
                quality_scores.append(validation['score'])
                if validation['is_valid']:
                    valid_questions += 1
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Generated", len(st.session_state.generated_questions))
            
            with col2:
                st.metric("Valid Questions", valid_questions)
            
            with col3:
                avg_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
                st.metric("Average Quality Score", f"{avg_score:.2f}")
            
            # Quality distribution
            if quality_scores:
                fig_quality = px.histogram(
                    x=quality_scores,
                    nbins=10,
                    title="Quality Score Distribution",
                    labels={'x': 'Quality Score', 'y': 'Count'}
                )
                st.plotly_chart(fig_quality, use_container_width=True)
            
            # Save generated questions
            if st.button("💾 Save Generated Questions", key="save_questions"):
                st.session_state.generator.save_generated_questions(
                    st.session_state.generated_questions,
                    "generated_questions.json"
                )
                st.success("✅ Questions saved successfully!")
        else:
            st.info("No generated questions to analyze. Please generate some questions first.")
    
    # Footer
    st.markdown("---")
    st.markdown("**RAG Question Generator** - Phase 2: Generation")
    st.markdown("Generate new questions using RAG and AI based on real matura data")

if __name__ == "__main__":
    main()
