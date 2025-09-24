"""
RAG-based Question Generator
Phase 2: Generation - Generate new questions using RAG and AI
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import re
from dataclasses import dataclass
import os
from .embedding_cache import EmbeddingCache

@dataclass
class GeneratedQuestion:
    """Data class for generated questions"""
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str
    topic: str
    source_questions: List[int]  # Indices of source questions used
    similarity_scores: List[float]
    generation_method: str

class RAGQuestionGenerator:
    def __init__(self, 
                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 llm_model: str = "gpt-3.5-turbo",
                 use_cache: bool = True):
        """Initialize the RAG question generator"""
        self.embedding_model = SentenceTransformer(embedding_model)
        self.use_cache = use_cache
        
        # Initialize embedding cache
        self.embedding_cache = EmbeddingCache(embedding_model)
        
        # Set OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            self.llm = ChatOpenAI(model=llm_model, temperature=0.7)
        else:
            print("⚠️ OpenAI API key not found. LLM functionality will be limited.")
            self.llm = None
        
        self.questions = []
        self.embeddings = None
        self.question_embeddings = None
        self.cache_data = None
        
    def load_real_questions(self, json_files: List[str]) -> None:
        """Load real matura questions from JSON files"""
        if self.use_cache:
            # Try to load from cache first
            self.cache_data = self.embedding_cache.load_cached_embeddings()
            if self.cache_data:
                self.questions = self.cache_data['questions']
                self.question_embeddings = self.cache_data['question_embeddings']
                self.embeddings = self.cache_data['all_embeddings']
                print(f"✅ Loaded {len(self.questions)} questions from cache")
                return
        
        # Fallback: load from JSON files
        all_questions = []
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_questions.extend(data)
                    elif isinstance(data, dict) and 'questions' in data:
                        all_questions.extend(data['questions'])
                    else:
                        all_questions.append(data)
                print(f"✅ Loaded questions from {file_path}")
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        
        self.questions = all_questions
        print(f"📊 Total loaded: {len(self.questions)} questions")
        
    def create_embeddings(self) -> None:
        """Create embeddings for questions"""
        if self.cache_data is not None:
            print("✅ Using cached embeddings")
            return
        
        print("🔄 Creating embeddings...")
        
        # Create embeddings for questions only
        question_texts = [q.get('question', '') for q in self.questions]
        self.question_embeddings = self.embedding_model.encode(question_texts)
        
        # Create embeddings for all texts (questions + answers)
        all_texts = []
        for q in self.questions:
            all_texts.append(q.get('question', ''))
            if q.get('type') == 'multiple_choice' and 'options' in q:
                all_texts.extend(q['options'])
            if 'correct_answer' in q:
                all_texts.append(q['correct_answer'])
        
        self.embeddings = self.embedding_model.encode(all_texts)
        print(f"✅ Created embeddings for {len(self.question_embeddings)} questions")
        
    def find_similar_questions(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Find similar questions using cosine similarity"""
        if self.question_embeddings is None:
            raise ValueError("Embeddings not created. Call create_embeddings() first.")
        
        # Create embedding for query
        query_embedding = self.embedding_model.encode([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.question_embeddings)[0]
        
        # Get top-k similar questions
        similar_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in similar_indices:
            results.append((idx, similarities[idx]))
        
        return results
    
    def generate_question_variants(self, 
                                 base_question: str, 
                                 num_variants: int = 3,
                                 difficulty: str = "medium") -> List[GeneratedQuestion]:
        """Generate variants of a base question"""
        
        # Find similar questions
        similar_questions = self.find_similar_questions(base_question, top_k=3)
        
        # Prepare context from similar questions
        context_questions = []
        for idx, similarity in similar_questions:
            q = self.questions[idx]
            context_questions.append({
                'question': q.get('question', ''),
                'options': q.get('options', []),
                'correct_answer': q.get('correct_answer', ''),
                'type': q.get('type', ''),
                'similarity': similarity
            })
        
        # Generate variants using LLM
        variants = []
        for i in range(num_variants):
            variant = self._generate_single_variant(
                base_question, 
                context_questions, 
                difficulty,
                variant_number=i+1
            )
            if variant:
                variants.append(variant)
        
        return variants
    
    def _generate_single_variant(self, 
                                base_question: str, 
                                context_questions: List[Dict], 
                                difficulty: str,
                                variant_number: int) -> Optional[GeneratedQuestion]:
        """Generate a single variant of a question"""
        
        if self.llm is None:
            print("❌ LLM not available. Cannot generate variants.")
            return None
        
        # Prepare context
        context_text = "Контекст от сходни въпроси:\n"
        for i, ctx_q in enumerate(context_questions):
            context_text += f"\n{i+1}. {ctx_q['question']}\n"
            if ctx_q['options']:
                context_text += f"   Варианти: {', '.join(ctx_q['options'])}\n"
            context_text += f"   Верен отговор: {ctx_q['correct_answer']}\n"
        
        # Create system prompt
        system_prompt = f"""Ти си експерт по българска литература и език, който създава въпроси за ДЗИ матура.
Твоята задача е да създадеш нов вариант на въпрос, базиран на дадения контекст.

Правила:
1. Въпросът трябва да е на български език
2. Трябва да има 4 варианта за отговор (A, B, C, D)
3. Трябва да има само един верен отговор
4. Трудността трябва да е {difficulty}
5. Въпросът трябва да е свързан с българска литература или език
6. Използвай контекста за вдъхновение, но създай нещо ново

Формат на отговора:
ВЪПРОС: [въпросът]
A) [вариант 1]
B) [вариант 2] 
C) [вариант 3]
D) [вариант 4]
ВЕРЕН_ОТГОВОР: [буквата на верния отговор]
ОБЯСНЕНИЕ: [кратко обяснение защо отговорът е верен]
ТЕМА: [темата на въпроса]
"""
        
        # Create user prompt
        user_prompt = f"""Базирай се на този въпрос: "{base_question}"

{context_text}

Създай нов вариант на въпроса, който е сходен по тема, но различен по формулировка и отговори."""
        
        try:
            # Generate with LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            generated_text = response.content
            
            # Parse the response
            variant = self._parse_generated_question(
                generated_text, 
                base_question, 
                context_questions,
                f"variant_{variant_number}"
            )
            
            return variant
            
        except Exception as e:
            print(f"❌ Error generating variant {variant_number}: {e}")
            return None
    
    def _parse_generated_question(self, 
                                 generated_text: str, 
                                 base_question: str, 
                                 context_questions: List[Dict],
                                 generation_method: str) -> Optional[GeneratedQuestion]:
        """Parse the generated question text"""
        
        try:
            # Extract question
            question_match = re.search(r'ВЪПРОС:\s*(.+?)(?=\n[A-D]\)|$)', generated_text, re.DOTALL)
            if not question_match:
                return None
            
            question = question_match.group(1).strip()
            
            # Extract options
            options = []
            for letter in ['A', 'B', 'C', 'D']:
                option_match = re.search(rf'{letter}\)\s*(.+?)(?=\n[^A-D]|$)', generated_text, re.DOTALL)
                if option_match:
                    options.append(option_match.group(1).strip())
            
            if len(options) != 4:
                return None
            
            # Extract correct answer
            correct_match = re.search(r'ВЕРЕН_ОТГОВОР:\s*([A-D])', generated_text)
            if not correct_match:
                return None
            
            correct_answer = correct_match.group(1)
            
            # Extract explanation
            explanation_match = re.search(r'ОБЯСНЕНИЕ:\s*(.+?)(?=\n|$)', generated_text, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else ""
            
            # Extract topic
            topic_match = re.search(r'ТЕМА:\s*(.+?)(?=\n|$)', generated_text, re.DOTALL)
            topic = topic_match.group(1).strip() if topic_match else "general"
            
            # Get source question indices
            source_indices = [i for i in range(len(context_questions))]
            similarity_scores = [ctx_q['similarity'] for ctx_q in context_questions]
            
            return GeneratedQuestion(
                question=question,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                difficulty="medium",
                topic=topic,
                source_questions=source_indices,
                similarity_scores=similarity_scores,
                generation_method=generation_method
            )
            
        except Exception as e:
            print(f"❌ Error parsing generated question: {e}")
            return None
    
    def generate_questions_by_topic(self, 
                                   topic: str, 
                                   num_questions: int = 5) -> List[GeneratedQuestion]:
        """Generate questions for a specific topic"""
        
        # Find questions related to the topic
        topic_questions = []
        for i, q in enumerate(self.questions):
            if topic.lower() in q.get('question', '').lower():
                topic_questions.append((i, q))
        
        if not topic_questions:
            print(f"❌ No questions found for topic: {topic}")
            return []
        
        # Generate new questions based on topic
        generated_questions = []
        for i in range(min(num_questions, len(topic_questions))):
            base_question = topic_questions[i][1]['question']
            variants = self.generate_question_variants(base_question, num_variants=1)
            if variants:
                generated_questions.extend(variants)
        
        return generated_questions
    
    def validate_question_quality(self, question: GeneratedQuestion) -> Dict[str, Any]:
        """Validate the quality of a generated question"""
        
        validation = {
            'is_valid': True,
            'issues': [],
            'score': 0.0
        }
        
        # Check question length
        if len(question.question.split()) < 5:
            validation['issues'].append("Question too short")
            validation['is_valid'] = False
        
        # Check options count
        if len(question.options) != 4:
            validation['issues'].append("Incorrect number of options")
            validation['is_valid'] = False
        
        # Check correct answer format
        if question.correct_answer not in ['A', 'B', 'C', 'D']:
            validation['issues'].append("Invalid correct answer format")
            validation['is_valid'] = False
        
        # Check for duplicate options
        if len(set(question.options)) != len(question.options):
            validation['issues'].append("Duplicate options found")
            validation['is_valid'] = False
        
        # Calculate quality score
        score = 0.0
        if len(question.question.split()) >= 5:
            score += 0.3
        if len(question.options) == 4:
            score += 0.3
        if question.correct_answer in ['A', 'B', 'C', 'D']:
            score += 0.2
        if len(set(question.options)) == len(question.options):
            score += 0.2
        
        validation['score'] = score
        
        return validation
    
    def save_generated_questions(self, 
                                questions: List[GeneratedQuestion], 
                                output_file: str = "generated_questions.json") -> None:
        """Save generated questions to JSON file"""
        
        questions_data = []
        for q in questions:
            questions_data.append({
                'question': q.question,
                'options': q.options,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation,
                'difficulty': q.difficulty,
                'topic': q.topic,
                'source_questions': q.source_questions,
                'similarity_scores': q.similarity_scores,
                'generation_method': q.generation_method
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(questions)} generated questions to {output_file}")

def main():
    """Main function to test the RAG question generator"""
    print("🚀 Starting RAG Question Generator...")
    
    # Initialize generator
    generator = RAGQuestionGenerator()
    
    # Load real questions
    json_files = [
        "data/matura_21_05_2025.json",
        "data/matura_2025_avgust.json"
    ]
    
    generator.load_real_questions(json_files)
    generator.create_embeddings()
    
    # Test question generation
    print("\n🔍 Testing question generation...")
    test_question = "Кой конфликт е заложен в интерпретацията на темата за човека и властта в \"Бай Ганьо журналист\" на Алеко Константинов?"
    
    variants = generator.generate_question_variants(test_question, num_variants=2)
    
    print(f"\nGenerated {len(variants)} variants:")
    for i, variant in enumerate(variants):
        print(f"\n--- Variant {i+1} ---")
        print(f"Question: {variant.question}")
        print(f"Options: {variant.options}")
        print(f"Correct: {variant.correct_answer}")
        print(f"Topic: {variant.topic}")
        
        # Validate quality
        validation = generator.validate_question_quality(variant)
        print(f"Quality Score: {validation['score']:.2f}")
        if validation['issues']:
            print(f"Issues: {', '.join(validation['issues'])}")
    
    # Save generated questions
    if variants:
        generator.save_generated_questions(variants, "generated_questions_test.json")

if __name__ == "__main__":
    main()
