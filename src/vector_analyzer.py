"""
Vector Analyzer for Real Matura Questions
Phase 1: Foundation - Vectorize and analyze real questions
"""

import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

class MaturaVectorAnalyzer:
    def __init__(self, embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize the vector analyzer with embedding model"""
        self.embedding_model = SentenceTransformer(embedding_model)
        self.questions = []
        self.embeddings = None
        self.analysis_results = {}
        
    def load_real_questions(self, json_files: List[str]) -> None:
        """Load real matura questions from JSON files"""
        all_questions = []
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle different JSON structures
                    if isinstance(data, list):
                        all_questions.extend(data)
                        print(f"✅ Loaded {len(data)} questions from {file_path}")
                    elif isinstance(data, dict):
                        # Check if it has a 'questions' key
                        if 'questions' in data:
                            questions = data['questions']
                            all_questions.extend(questions)
                            print(f"✅ Loaded {len(questions)} questions from {file_path}")
                        else:
                            # Single question object
                            all_questions.append(data)
                            print(f"✅ Loaded 1 question from {file_path}")
                    else:
                        all_questions.append(data)
                        print(f"✅ Loaded 1 question from {file_path}")
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        
        self.questions = all_questions
        print(f"📊 Total loaded: {len(self.questions)} questions")
        
    def create_embeddings(self) -> None:
        """Create embeddings for all questions and answers"""
        print("🔄 Creating embeddings...")
        
        # Prepare texts for embedding
        texts = []
        for q in self.questions:
            # Question text
            texts.append(q.get('question', ''))
            
            # Answer options (for multiple choice)
            if q.get('type') == 'multiple_choice' and 'options' in q:
                texts.extend(q['options'])
            
            # Correct answer
            if 'correct_answer' in q:
                texts.append(q['correct_answer'])
        
        # Create embeddings
        self.embeddings = self.embedding_model.encode(texts)
        print(f"✅ Created {len(self.embeddings)} embeddings")
        
    def analyze_question_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the questions"""
        print("🔍 Analyzing question patterns...")
        
        analysis = {
            'total_questions': len(self.questions),
            'question_types': Counter([q.get('type', 'unknown') for q in self.questions]),
            'question_lengths': [],
            'answer_lengths': [],
            'topics': [],
            'difficulty_patterns': [],
            'common_words': Counter(),
            'question_structures': []
        }
        
        for q in self.questions:
            # Question length analysis
            question_text = q.get('question', '')
            analysis['question_lengths'].append(len(question_text.split()))
            
            # Answer length analysis
            if 'correct_answer' in q:
                answer_text = q['correct_answer']
                analysis['answer_lengths'].append(len(answer_text.split()))
            
            # Topic analysis (extract from question text)
            topics = self._extract_topics(question_text)
            analysis['topics'].extend(topics)
            
            # Common words analysis
            words = re.findall(r'\b\w+\b', question_text.lower())
            analysis['common_words'].update(words)
            
            # Question structure analysis
            structure = self._analyze_question_structure(question_text)
            analysis['question_structures'].append(structure)
        
        # Calculate statistics
        analysis['avg_question_length'] = np.mean(analysis['question_lengths'])
        analysis['avg_answer_length'] = np.mean(analysis['answer_lengths'])
        analysis['most_common_topics'] = Counter(analysis['topics']).most_common(10)
        analysis['most_common_words'] = analysis['common_words'].most_common(20)
        analysis['structure_patterns'] = Counter(analysis['question_structures'])
        
        self.analysis_results = analysis
        return analysis
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from question text"""
        topics = []
        
        # Literature topics
        literature_keywords = ['автор', 'произведение', 'роман', 'разказ', 'поезия', 'стихотворение', 'герой', 'персонаж']
        if any(keyword in text.lower() for keyword in literature_keywords):
            topics.append('literature')
        
        # Language topics
        language_keywords = ['език', 'граматика', 'правопис', 'синтаксис', 'морфология', 'фонетика']
        if any(keyword in text.lower() for keyword in language_keywords):
            topics.append('language')
        
        # Analysis topics
        analysis_keywords = ['анализ', 'интерпретация', 'значение', 'смисъл', 'тема', 'идея']
        if any(keyword in text.lower() for keyword in analysis_keywords):
            topics.append('analysis')
        
        return topics
    
    def _analyze_question_structure(self, text: str) -> str:
        """Analyze the structure of a question"""
        if text.startswith('Кой') or text.startswith('Коя') or text.startswith('Кое'):
            return 'which_question'
        elif text.startswith('Какво') or text.startswith('Каква'):
            return 'what_question'
        elif text.startswith('Защо') or text.startswith('Почему'):
            return 'why_question'
        elif text.startswith('Как'):
            return 'how_question'
        elif '?' in text:
            return 'question_mark'
        else:
            return 'statement'
    
    def find_similar_questions(self, query_text: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Find similar questions using cosine similarity"""
        if self.embeddings is None:
            raise ValueError("Embeddings not created. Call create_embeddings() first.")
        
        # Create embedding for query
        query_embedding = self.embedding_model.encode([query_text])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k similar questions
        similar_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in similar_indices:
            if idx < len(self.questions):
                results.append((idx, similarities[idx]))
        
        return results
    
    def cluster_questions(self, n_clusters: int = 5) -> Dict[int, List[int]]:
        """Cluster questions based on embeddings"""
        if self.embeddings is None:
            raise ValueError("Embeddings not created. Call create_embeddings() first.")
        
        # Adjust n_clusters if we have fewer samples
        n_clusters = min(n_clusters, len(self.embeddings))
        
        if n_clusters < 2:
            print("⚠️ Not enough data for clustering")
            return {0: list(range(len(self.embeddings)))}
        
        # Use K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(self.embeddings)
        
        # Group questions by cluster
        clusters = defaultdict(list)
        for idx, label in enumerate(cluster_labels):
            clusters[label].append(idx)
        
        return dict(clusters)
    
    def generate_analysis_report(self) -> str:
        """Generate a comprehensive analysis report"""
        if not self.analysis_results:
            self.analyze_question_patterns()
        
        report = f"""
# 📊 Matura Questions Analysis Report

## 📈 Basic Statistics
- **Total Questions**: {self.analysis_results['total_questions']}
- **Average Question Length**: {self.analysis_results['avg_question_length']:.1f} words
- **Average Answer Length**: {self.analysis_results['avg_answer_length']:.1f} words

## 🏷️ Question Types
"""
        for q_type, count in self.analysis_results['question_types'].items():
            report += f"- **{q_type}**: {count} questions\n"
        
        report += f"""
## 🎯 Most Common Topics
"""
        for topic, count in self.analysis_results['most_common_topics']:
            report += f"- **{topic}**: {count} questions\n"
        
        report += f"""
## 📝 Question Structures
"""
        for structure, count in self.analysis_results['structure_patterns'].items():
            report += f"- **{structure}**: {count} questions\n"
        
        report += f"""
## 🔤 Most Common Words
"""
        for word, count in self.analysis_results['most_common_words']:
            report += f"- **{word}**: {count} occurrences\n"
        
        return report
    
    def save_analysis(self, output_file: str = "analysis_results.json") -> None:
        """Save analysis results to JSON file"""
        results = {
            'analysis': self.analysis_results,
            'embeddings_shape': self.embeddings.shape if self.embeddings is not None else None,
            'total_questions': len(self.questions)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Analysis saved to {output_file}")

def main():
    """Main function to run the analysis"""
    print("🚀 Starting Matura Vector Analysis...")
    
    # Initialize analyzer
    analyzer = MaturaVectorAnalyzer()
    
    # Load real questions
    json_files = [
        "data/matura_21_05_2025.json",
        "data/matura_2025_avgust.json"
    ]
    
    analyzer.load_real_questions(json_files)
    
    # Create embeddings
    analyzer.create_embeddings()
    
    # Analyze patterns
    analysis = analyzer.analyze_question_patterns()
    
    # Generate report
    report = analyzer.generate_analysis_report()
    print(report)
    
    # Save analysis
    analyzer.save_analysis()
    
    # Test similarity search
    print("\n🔍 Testing similarity search...")
    test_query = "Кой конфликт е заложен в интерпретацията на темата за човека и властта"
    similar = analyzer.find_similar_questions(test_query, top_k=3)
    
    print(f"Query: {test_query}")
    for idx, similarity in similar:
        question = analyzer.questions[idx]
        print(f"Similarity: {similarity:.3f} - {question.get('question', '')[:100]}...")
    
    # Test clustering
    print("\n🎯 Testing clustering...")
    clusters = analyzer.cluster_questions(n_clusters=3)
    for cluster_id, question_indices in clusters.items():
        print(f"Cluster {cluster_id}: {len(question_indices)} questions")

if __name__ == "__main__":
    main()
