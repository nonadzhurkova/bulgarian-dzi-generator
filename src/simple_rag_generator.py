"""
Simple RAG Question Generator - Phase 2
Uses only OpenAI API without heavy models
"""

import os
import json
import random
import logging
from typing import List, Dict, Any
from enum import Enum

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Setup logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_generator.log', encoding='utf-8', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SubjectArea(Enum):
    LANGUAGE = "language"
    LITERATURE = "literature"

class SimpleRAGGenerator:
    """Simple RAG generator using only OpenAI API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Load real questions for context
        self.real_questions = self._load_real_questions()
        
    def _load_real_questions(self) -> List[Dict]:
        """Load real questions from JSON files"""
        questions = []
        
        # Load from matura files
        for file_path in ['data/matura_21_05_2025.json', 'data/matura_2025_avgust.json']:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            questions.extend(data)
                        elif isinstance(data, dict) and 'questions' in data:
                            questions.extend(data['questions'])
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return questions
    
    def _get_openai_client(self):
        """Get OpenAI client"""
        try:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    def _find_similar_questions(self, subject: SubjectArea, count: int = 3) -> List[Dict]:
        """Find similar questions from real data"""
        logger.info(f"🔍 [RAG] Searching for similar questions in {len(self.real_questions)} real questions")
        
        # Since the data doesn't have subject field, we'll use content-based filtering
        similar = []
        
        if subject == SubjectArea.LANGUAGE:
            # Look for language-related keywords in questions
            language_keywords = [
                'правопис', 'граматика', 'синтаксис', 'морфология', 'фонетика',
                'дума', 'изречение', 'звук', 'буква', 'сричка', 'съгласна', 'гласна',
                'правописна', 'граматическа', 'синтактична', 'морфологична',
                'изписана', 'правилно', 'грешка', 'правописна грешка'
            ]
            
            for q in self.real_questions:
                question_text = q.get('question', '').lower()
                if any(keyword in question_text for keyword in language_keywords):
                    similar.append(q)
                    
        else:  # LITERATURE
            # Look for literature-related keywords
            literature_keywords = [
                'автор', 'писател', 'поет', 'роман', 'повест', 'разказ', 'стихотворение',
                'литература', 'творба', 'произведение', 'персонаж', 'герой',
                'литературен', 'художествен', 'епически', 'лирически', 'драматически'
            ]
            
            for q in self.real_questions:
                question_text = q.get('question', '').lower()
                if any(keyword in question_text for keyword in literature_keywords):
                    similar.append(q)
        
        logger.info(f"🔍 [RAG] Found {len(similar)} similar questions using keyword matching")
        
        # If no keyword matches, use random questions as fallback
        if not similar:
            logger.warning("⚠️ [RAG] No keyword matches found, using random questions as fallback")
            similar = self.real_questions[:min(count, len(self.real_questions))]
        
        # Return random sample
        return random.sample(similar, min(count, len(similar)))
    
    def _generate_with_openai(self, subject: SubjectArea, count: int, similar_questions: List[Dict]) -> List[Dict]:
        """Generate questions using OpenAI API"""
        logger.info(f"🚀 [RAG] Starting OpenAI generation for {subject.value} - {count} questions")
        logger.info(f"🔑 [RAG] API Key configured: {bool(self.api_key)}")
        
        client = self._get_openai_client()
        logger.info(f"✅ [RAG] OpenAI client initialized")
        
        # Prepare context from similar questions
        context = ""
        for i, q in enumerate(similar_questions[:3]):
            context += f"Пример {i+1}:\n"
            context += f"Въпрос: {q.get('question', 'N/A')}\n"
            context += f"Опции: {', '.join(q.get('options', []))}\n"
            context += f"Правилен отговор: {q.get('correct_answer', 'N/A')}\n\n"
        
        logger.info(f"📝 [RAG] Context prepared with {len(similar_questions)} similar questions")
        
        # Create prompt
        subject_name = "Български език" if subject == SubjectArea.LANGUAGE else "Българска литература"
        
        prompt = f"""Генерирай {count} нови въпроса за {subject_name} в стила на ДЗИ матура.

Контекст от реални въпроси:
{context}

Изисквания:
- Въпросите трябва да са на български език
- Всеки въпрос трябва да има 4 опции (A, B, C, D)
- Трябва да има само един правилен отговор
- Стилът трябва да е като на реалните въпроси
- Трудността трябва да е различна (easy, medium, hard)

Отговори в JSON формат:
{{
  "questions": [
    {{
      "question": "Текст на въпроса",
      "options": ["Опция A", "Опция B", "Опция C", "Опция D"],
      "correct_answer": "Правилната опция",
      "subject": "{subject_name}",
      "difficulty": "easy/medium/hard",
      "points": 1
    }}
  ]
}}"""
        
        try:
            logger.info(f"🌐 [RAG] Sending request to OpenAI API...")
            
            # Try gpt-5-nano first, fallback to gpt-3.5-turbo
            try:
                logger.info(f"📊 [RAG] Trying gpt-5-nano, Max completion tokens: 2000")
                response = client.chat.completions.create(
                    model="gpt-4.1-nano",
                    messages=[
                        {"role": "system", "content": "Ти си експерт по български език и литература, специализиран в създаване на въпроси за ДЗИ матура."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=2000
                )
                logger.info(f"✅ [RAG] Successfully used gpt-5-nano")
            except Exception as nano_error:
                logger.warning(f"⚠️ [RAG] gpt-5-nano failed: {nano_error}")
                logger.info(f"📊 [RAG] Falling back to gpt-4.1-nano-2025-04-14, Max completion tokens: 2000")
                response = client.chat.completions.create(
                    model="gpt-4.1-nano-2025-04-14",
                    messages=[
                        {"role": "system", "content": "Ти си експерт по български език и литература, специализиран в създаване на въпроси за ДЗИ матура."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=2000
                )
                logger.info(f"✅ [RAG] Successfully used gpt-4.1-nano-2025-04-14 fallback")
            
            logger.info(f"✅ [RAG] OpenAI API response received!")
            logger.info(f"📝 [RAG] Response length: {len(response.choices[0].message.content)} characters")
            
            # Parse response
            content = response.choices[0].message.content.strip()
            logger.info(f"📝 [RAG] Raw response content: '{content}'")
            
            # Check if response is empty (gpt-5-nano issue)
            if not content:
                logger.warning(f"⚠️ [RAG] Empty response received, trying fallback to gpt-4.1-nano-2025-04-14")
                response = client.chat.completions.create(
                    model="gpt-4.1-nano-2025-04-14",
                    messages=[
                        {"role": "system", "content": "Ти си експерт по български език и литература, специализиран в създаване на въпроси за ДЗИ матура."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=2000
                )
                content = response.choices[0].message.content.strip()
                logger.info(f"✅ [RAG] Fallback response: '{content[:100]}...'")
            
            # Try to extract JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            elif "{" in content and "}" in content:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_content = content[json_start:json_end]
            else:
                logger.error(f"❌ [RAG] No JSON found in response. Content: '{content}'")
                raise ValueError("No JSON found in response")
            
            result = json.loads(json_content)
            questions = result.get("questions", [])
            logger.info(f"🎯 [RAG] Successfully parsed {len(questions)} questions from OpenAI response")
            return questions
            
        except Exception as e:
            logger.error(f"❌ [RAG] Error generating with OpenAI: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def generate_questions(self, count: int, subject: SubjectArea) -> List[Dict]:
        """Generate new questions using RAG approach"""
        logger.info(f"🎯 [RAG] Starting question generation: {count} questions for {subject.value}")
        
        if not self.api_key:
            logger.error("❌ [RAG] OpenAI API key not configured")
            raise ValueError("OpenAI API key not configured")
        
        logger.info(f"✅ [RAG] API key found: {self.api_key[:10]}...")
        
        # Find similar questions for context
        similar_questions = self._find_similar_questions(subject, 3)
        logger.info(f"🔍 [RAG] Found {len(similar_questions)} similar questions for context")
        
        if not similar_questions:
            logger.warning("⚠️ [RAG] No similar questions found, using basic generation")
            return self._generate_basic_questions(count, subject)
        
        # Generate with OpenAI
        logger.info(f"🚀 [RAG] Proceeding with OpenAI generation...")
        generated = self._generate_with_openai(subject, count, similar_questions)
        
        if not generated:
            logger.warning("⚠️ [RAG] OpenAI generation failed, using basic generation")
            return self._generate_basic_questions(count, subject)
        
        logger.info(f"✅ [RAG] Successfully generated {len(generated)} questions!")
        return generated
    
    def _generate_basic_questions(self, count: int, subject: SubjectArea) -> List[Dict]:
        """Fallback basic generation without API"""
        questions = []
        
        if subject == SubjectArea.LANGUAGE:
            templates = [
                {
                    "question": "Кой от следните думи е синоним на 'изключителен'?",
                    "options": ["обикновен", "редовен", "извънреден", "стандартен"],
                    "correct_answer": "извънреден"
                },
                {
                    "question": "Кой от следните думи е антоним на 'добър'?",
                    "options": ["хубав", "лош", "добър", "отличен"],
                    "correct_answer": "лош"
                }
            ]
        else:
            templates = [
                {
                    "question": "Кой е авторът на романа 'Под игото'?",
                    "options": ["Иван Вазов", "Христо Ботев", "Пейо Яворов", "Димчо Дебелянов"],
                    "correct_answer": "Иван Вазов"
                },
                {
                    "question": "В кой период е създадена поемата 'Хайдушки'?",
                    "options": ["Възраждането", "Средновековието", "Античността", "Модернизма"],
                    "correct_answer": "Възраждането"
                }
            ]
        
        # Generate requested number of questions
        for i in range(count):
            template = random.choice(templates)
            question = template.copy()
            question["subject"] = "Български език" if subject == SubjectArea.LANGUAGE else "Българска литература"
            question["difficulty"] = random.choice(["easy", "medium", "hard"])
            question["points"] = 1
            questions.append(question)
        
        return questions
    
    def add_question_to_database(self, question: Dict):
        """Add a new question to the real questions database"""
        logger.info(f"📝 [RAG] Adding new question to database: {question.get('question', 'N/A')[:50]}...")
        self.real_questions.append(question)
        logger.info(f"✅ [RAG] Question added. Total questions: {len(self.real_questions)}")
    
    def add_questions_to_database(self, questions: List[Dict]):
        """Add multiple questions to the real questions database"""
        logger.info(f"📝 [RAG] Adding {len(questions)} new questions to database")
        for question in questions:
            self.real_questions.append(question)
        logger.info(f"✅ [RAG] All questions added. Total questions: {len(self.real_questions)}")
