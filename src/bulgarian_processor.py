"""
Bulgarian text processing utilities for DZI materials
"""
import re
import spacy
from typing import List, Dict, Any
import config

class BulgarianTextProcessor:
    """Bulgarian text processor for DZI materials"""
    
    def __init__(self):
        self.nlp = None
        self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load Bulgarian spaCy model"""
        try:
            self.nlp = spacy.load(config.SPACY_MODEL)
        except OSError:
            print(f"Bulgarian spaCy model not found. Please install with: python -m spacy download {config.SPACY_MODEL}")
            self.nlp = None
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess Bulgarian text"""
        if not text:
            return ""
        
        # Basic cleaning
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = text.strip()
        
        # If spaCy is available, use it for better processing
        if self.nlp:
            doc = self.nlp(text)
            # Extract lemmatized tokens
            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            return ' '.join(tokens)
        
        return text
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from Bulgarian text"""
        if not text:
            return []
        
        # Simple keyword extraction
        words = re.findall(r'\b[а-я]+\b', text.lower())
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Only words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def detect_subject(self, text: str) -> str:
        """Detect subject area from text"""
        literature_keywords = ['литература', 'автор', 'творба', 'стихотворение', 'роман', 'разказ', 'драма']
        language_keywords = ['език', 'граматика', 'правопис', 'синтаксис', 'лексика', 'морфология']
        
        text_lower = text.lower()
        
        literature_score = sum(1 for keyword in literature_keywords if keyword in text_lower)
        language_score = sum(1 for keyword in language_keywords if keyword in text_lower)
        
        if literature_score > language_score:
            return 'literature'
        elif language_score > literature_score:
            return 'language'
        else:
            return 'general'
    
    def is_bulgarian(self, text: str) -> bool:
        """Check if text is in Bulgarian"""
        if not text:
            return False
        
        # Count Bulgarian characters
        bulgarian_chars = len(re.findall(r'[а-я]', text.lower()))
        total_chars = len(re.findall(r'[а-яa-z]', text.lower()))
        
        if total_chars == 0:
            return False
        
        return (bulgarian_chars / total_chars) > 0.5
