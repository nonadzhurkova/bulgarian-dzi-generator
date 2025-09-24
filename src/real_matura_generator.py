"""
Real Matura Question Generator based on actual DZI exams
"""
import json
import random
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class SubjectArea(Enum):
    LANGUAGE = "language"
    LITERATURE = "literature"

@dataclass
class Question:
    id: str
    question_text: str
    question_type: QuestionType
    subject_area: SubjectArea
    topic: str
    difficulty: str
    points: int
    options: List[str] = None
    correct_answer: str = None
    explanation: str = None
    is_real_matura: bool = True
    context_texts: Dict[str, str] = None

class RealMaturaGenerator:
    """Generator for questions based on real DZI matura exams"""
    
    def __init__(self):
        self.questions_data = []
        self.load_real_questions()
    
    def load_real_questions(self):
        """Load questions from processed JSON files"""
        try:
            # Load first matura file
            with open('data/matura_21_05_2025.json', 'r', encoding='utf-8') as f:
                data1 = json.load(f)
                questions1 = data1.get('questions', [])
                self.questions_data.extend(questions1)
                print(f"Loaded {len(questions1)} questions from matura_21_05_2025.json")
            
            # Load second matura file
            with open('data/matura_2025_avgust.json', 'r', encoding='utf-8') as f:
                data2 = json.load(f)
                questions2 = data2.get('questions', [])
                self.questions_data.extend(questions2)
                print(f"Loaded {len(questions2)} questions from matura_2025_avgust.json")
            
            print(f"Total loaded: {len(self.questions_data)} real matura questions")
            
        except Exception as e:
            print(f"Error loading real questions: {e}")
            self.questions_data = []
    
    def convert_real_question(self, real_question: Dict[str, Any]) -> Question:
        """Convert real question data to Question object"""
        # Generate unique ID
        question_id = f"real_{real_question.get('number', 'unknown')}_{random.randint(1000, 9999)}"
        
        # Determine subject area
        subject = SubjectArea.LANGUAGE
        if real_question.get('subject') == 'literature':
            subject = SubjectArea.LITERATURE
        
        # Create Question object
        question = Question(
            id=question_id,
            question_text=real_question['question'],
            question_type=QuestionType.MULTIPLE_CHOICE if real_question.get('type') == 'multiple_choice' else QuestionType.SHORT_ANSWER,
            subject_area=subject,
            topic="Real Matura",
            difficulty="medium",
            points=real_question.get('points', 1),
            options=real_question.get('options', []),
            correct_answer=real_question.get('correct_answer', ''),
            is_real_matura=True,
            context_texts=real_question.get('context_texts')
        )
        
        return question
    
    def generate_question(self) -> Question:
        """Generate a random real question"""
        if not self.questions_data:
            raise ValueError("No real questions loaded")
        
        real_question = random.choice(self.questions_data)
        return self.convert_real_question(real_question)
    
    def generate_questions(self, count: int) -> List[Question]:
        """Generate multiple real questions"""
        if not self.questions_data:
            return []
        
        questions = []
        for _ in range(count):
            real_question = random.choice(self.questions_data)
            question = self.convert_real_question(real_question)
            questions.append(question)
        
        return questions
    
    def get_questions_by_subject(self, subject: SubjectArea) -> List[Question]:
        """Get questions filtered by subject"""
        filtered_questions = []
        for real_question in self.questions_data:
            if real_question.get('subject') == subject.value:
                question = self.convert_real_question(real_question)
                filtered_questions.append(question)
        
        return filtered_questions
    
    def get_all_questions(self) -> List[Question]:
        """Get all available real questions"""
        return [self.convert_real_question(q) for q in self.questions_data]
