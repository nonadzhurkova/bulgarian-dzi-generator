"""
Embedding Cache System
Pre-compute and cache embeddings for Streamlit Cloud deployment
"""

import pickle
import numpy as np
import json
import os
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from pathlib import Path

class EmbeddingCache:
    def __init__(self, 
                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 cache_dir: str = "cache"):
        """Initialize embedding cache system"""
        self.embedding_model = SentenceTransformer(embedding_model)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def compute_and_cache_embeddings(self, json_files: List[str]) -> Dict[str, Any]:
        """Compute embeddings and cache them"""
        print("🔄 Computing embeddings...")
        
        # Load all questions
        all_questions = []
        for file_path in json_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'questions' in data:
                    all_questions.extend(data['questions'])
                else:
                    all_questions.extend(data)
        
        print(f"📊 Loaded {len(all_questions)} questions")
        
        # Prepare texts for embedding
        question_texts = []
        all_texts = []
        
        for q in all_questions:
            question_text = q.get('question', '')
            question_texts.append(question_text)
            all_texts.append(question_text)
            
            # Add options and answers
            if q.get('type') == 'multiple_choice' and 'options' in q:
                all_texts.extend(q['options'])
            if 'correct_answer' in q:
                all_texts.append(q['correct_answer'])
        
        # Create embeddings
        print("🔄 Creating question embeddings...")
        question_embeddings = self.embedding_model.encode(question_texts)
        
        print("🔄 Creating all text embeddings...")
        all_embeddings = self.embedding_model.encode(all_texts)
        
        # Cache data
        cache_data = {
            'questions': all_questions,
            'question_texts': question_texts,
            'all_texts': all_texts,
            'question_embeddings': question_embeddings,
            'all_embeddings': all_embeddings,
            'model_name': self.embedding_model.get_sentence_embedding_dimension(),
            'total_questions': len(all_questions)
        }
        
        # Save cache
        cache_file = self.cache_dir / "embeddings_cache.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"✅ Cached embeddings to {cache_file}")
        return cache_data
    
    def load_cached_embeddings(self) -> Optional[Dict[str, Any]]:
        """Load cached embeddings"""
        cache_file = self.cache_dir / "embeddings_cache.pkl"
        
        if not cache_file.exists():
            print("❌ No cached embeddings found")
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            print(f"✅ Loaded cached embeddings ({cache_data['total_questions']} questions)")
            return cache_data
        except Exception as e:
            print(f"❌ Error loading cache: {e}")
            return None
    
    def get_similar_questions(self, 
                            query: str, 
                            top_k: int = 5,
                            use_cache: bool = True) -> List[tuple]:
        """Find similar questions using cached embeddings"""
        
        if use_cache:
            cache_data = self.load_cached_embeddings()
            if cache_data is None:
                return []
            
            questions = cache_data['questions']
            question_embeddings = cache_data['question_embeddings']
        else:
            # Fallback: compute on the fly
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Calculate similarities
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(query_embedding, question_embeddings)[0]
        
        # Get top-k similar questions
        similar_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in similar_indices:
            results.append((idx, similarities[idx]))
        
        return results
    
    def clear_cache(self):
        """Clear cached embeddings"""
        cache_file = self.cache_dir / "embeddings_cache.pkl"
        if cache_file.exists():
            cache_file.unlink()
            print("✅ Cache cleared")

def main():
    """Main function to pre-compute embeddings"""
    print("🚀 Pre-computing embeddings for Streamlit Cloud...")
    
    # Initialize cache
    cache = EmbeddingCache()
    
    # JSON files to process
    json_files = [
        "data/matura_21_05_2025.json",
        "data/matura_2025_avgust.json"
    ]
    
    # Compute and cache embeddings
    cache_data = cache.compute_and_cache_embeddings(json_files)
    
    print(f"✅ Pre-computation complete!")
    print(f"📊 Cached {cache_data['total_questions']} questions")
    print(f"📁 Cache file: cache/embeddings_cache.pkl")
    
    # Test similarity search
    print("\n🔍 Testing similarity search...")
    test_query = "Кой конфликт е заложен в интерпретацията на темата за човека и властта"
    similar = cache.get_similar_questions(test_query, top_k=3)
    
    print(f"Query: {test_query}")
    for idx, similarity in similar:
        question = cache_data['questions'][idx]
        print(f"Similarity: {similarity:.3f} - {question.get('question', '')[:100]}...")

if __name__ == "__main__":
    main()
