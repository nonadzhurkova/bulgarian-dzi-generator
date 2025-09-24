#!/usr/bin/env python3
"""
Pre-compute embeddings for Streamlit Cloud deployment
Run this once locally, then commit the cache files to GitHub
"""

import sys
import os
sys.path.append('src')

from src.embedding_cache import EmbeddingCache

def main():
    print("🚀 Pre-computing embeddings for Streamlit Cloud...")
    print("This will create cache files that can be deployed to Streamlit Cloud")
    print("=" * 60)
    
    # Initialize cache
    cache = EmbeddingCache()
    
    # JSON files to process
    json_files = [
        "data/matura_21_05_2025.json",
        "data/matura_2025_avgust.json"
    ]
    
    # Check if files exist
    missing_files = [f for f in json_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return
    
    # Compute and cache embeddings
    print("🔄 Computing embeddings...")
    cache_data = cache.compute_and_cache_embeddings(json_files)
    
    print(f"\n✅ Pre-computation complete!")
    print(f"📊 Cached {cache_data['total_questions']} questions")
    print(f"📁 Cache file: cache/embeddings_cache.pkl")
    print(f"📏 Embedding dimension: {cache_data['model_name']}")
    
    # Test similarity search
    print("\n🔍 Testing similarity search...")
    test_query = "Кой конфликт е заложен в интерпретацията на темата за човека и властта"
    similar = cache.get_similar_questions(test_query, top_k=3)
    
    print(f"Query: {test_query}")
    for idx, similarity in similar:
        question = cache_data['questions'][idx]
        print(f"Similarity: {similarity:.3f} - {question.get('question', '')[:100]}...")
    
    print("\n📋 Next steps:")
    print("1. Commit the cache/ directory to GitHub")
    print("2. Deploy to Streamlit Cloud")
    print("3. The app will use cached embeddings (fast startup)")

if __name__ == "__main__":
    main()
