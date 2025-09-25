"""
Configuration settings for Bulgarian DZU RAG System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "your_huggingface_api_key_here")

# Database settings
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

# Model settings - Use only gpt-5-nano, no heavy embedding models
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL = "gpt-5-nano"

# Bulgarian language processing
SPACY_MODEL = os.getenv("SPACY_MODEL", "bg_core_news_sm")

# RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5

# Bulgarian DZU subjects
DZU_SUBJECTS = [
    "Български език и литература",
    "Математика", 
    "История",
    "География",
    "Биология",
    "Химия",
    "Физика",
    "Английски език",
    "Немски език",
    "Френски език",
    "Руски език",
    "Информатика"
]

# File paths
DATA_DIR = "data"
MODELS_DIR = "models"
SRC_DIR = "src"
