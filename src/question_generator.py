"""
DZI Question Generator for Bulgarian Language and Literature
"""
import random
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class SubjectArea(Enum):
    LANGUAGE = "language"
    LITERATURE = "literature"

class Topic(Enum):
    NATIVE_AND_FOREIGN = "Native and Foreign"
    PAST_AND_MEMORY = "Past and Memory"
    SOCIETY_AND_POWER = "Society and Power"
    LIFE_AND_DEATH = "Life and Death"
    NATURE = "Nature"
    LOVE = "Love"
    FAITH_AND_HOPE = "Faith and Hope"
    WORK_AND_CREATIVITY = "Work and Creativity"
    CHOICE_AND_DIVISION = "Choice and Division"

@dataclass
class Question:
    id: str
    question_text: str
    question_type: QuestionType
    subject_area: SubjectArea
    topic: Topic
    difficulty: str
    points: int
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

class DZIQuestionGenerator:
    """Generator for DZI questions in Bulgarian Language and Literature"""
    
    def __init__(self):
        self.language_questions = self._create_language_questions()
        self.literature_questions = self._create_literature_questions()
    
    def _create_language_questions(self) -> List[Dict[str, Any]]:
        """Create language questions"""
        return [
            {
                "question": "В кой ред думата е изписана правилно?",
                "options": ["азиатски", "овеличение", "съчуствие", "распечатка"],
                "correct_answer": "азиатски",
                "topic": Topic.NATIVE_AND_FOREIGN,
                "difficulty": "easy",
                "points": 1
            },
            {
                "question": "В кое изречение е допусната правописна грешка?",
                "options": [
                    "Победителят взе преднина във финалния етап на състезанието.",
                    "Изследователят има публикации в авторитетни научни списания.",
                    "Алпинистът трябва да е издържлив и физически, и психически.",
                    "По учебен план дисциплината се изучава през последния семестър."
                ],
                "correct_answer": "Победителят взе преднина във финалния етап на състезанието.",
                "topic": Topic.NATIVE_AND_FOREIGN,
                "difficulty": "medium",
                "points": 1
            },
            {
                "question": "Кой от следните думи е синоним на 'изключителен'?",
                "options": ["обикновен", "необикновен", "стандартен", "типичен"],
                "correct_answer": "необикновен",
                "topic": Topic.NATIVE_AND_FOREIGN,
                "difficulty": "easy",
                "points": 1
            }
        ]
    
    def _create_literature_questions(self) -> List[Dict[str, Any]]:
        """Create literature questions"""
        return [
            {
                "question": "Кой автор е написал 'Железният светилник'?",
                "options": ["Димитър Талев", "Алеко Константинов", "Станислав Стратиев", "Иван Вазов"],
                "correct_answer": "Димитър Талев",
                "topic": Topic.NATIVE_AND_FOREIGN,
                "difficulty": "easy",
                "points": 1
            },
            {
                "question": "В коя тема се включва творбата 'Бай Ганьо журналист'?",
                "options": ["Родното и чуждото", "Миналото и паметта", "Обществото и властта", "Животът и смъртта"],
                "correct_answer": "Родното и чуждото",
                "topic": Topic.NATIVE_AND_FOREIGN,
                "difficulty": "medium",
                "points": 1
            },
            {
                "question": "Кой е главният герой в 'Железният светилник'?",
                "options": ["Бай Ганьо", "Стоян", "Манол", "Петър"],
                "correct_answer": "Стоян",
                "topic": Topic.NATIVE_AND_FOREIGN,
                "difficulty": "medium",
                "points": 1
            }
        ]
    
    def generate_question(self, subject: SubjectArea, question_type: QuestionType = None) -> Question:
        """Generate a random question"""
        if subject == SubjectArea.LANGUAGE:
            question_data = random.choice(self.language_questions)
        else:
            question_data = random.choice(self.literature_questions)
        
        # Generate unique ID
        question_id = f"{subject.value}_{question_type.value if question_type else 'mc'}_{random.randint(1000, 9999)}"
        
        return Question(
            id=question_id,
            question_text=question_data["question"],
            question_type=question_type or QuestionType.MULTIPLE_CHOICE,
            subject_area=subject,
            topic=question_data["topic"],
            difficulty=question_data["difficulty"],
            points=question_data["points"],
            options=question_data.get("options"),
            correct_answer=question_data["correct_answer"]
        )
    
    def generate_questions(self, count: int, subject: SubjectArea = None) -> List[Question]:
        """Generate multiple questions"""
        questions = []
        
        for _ in range(count):
            if subject:
                target_subject = subject
            else:
                target_subject = random.choice([SubjectArea.LANGUAGE, SubjectArea.LITERATURE])
            
            question = self.generate_question(target_subject)
            questions.append(question)
        
        return questions
