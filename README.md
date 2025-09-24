# Bulgarian DZI Question Generator

A comprehensive system for generating and practicing Bulgarian DZI (Държавна зрелостна изпитване) exam questions using AI and RAG technology.

## Features

### 📚 Real Matura Questions
- Loads questions from real DZI exam PDFs
- 36 authentic questions from 2025 exams
- Automatic answer checking
- Clean, modern interface

### 🤖 AI-Powered Generation
- RAG-based question generation
- Semantic similarity matching
- Difficulty scaling
- Topic cross-pollination

### 🎯 Question Types
- Multiple choice questions
- Short answer questions
- Extended short answer questions
- Argumentative essays

### 📊 Analytics
- Progress tracking
- Performance statistics
- Topic-based filtering

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
# For real matura questions
python run_real_matura.py

# For AI-generated questions
python run_questions.py
```

## Project Structure

```
BEL/
├── app_real_matura.py      # Real matura questions app
├── app_questions.py         # AI-generated questions app
├── src/
│   ├── real_matura_generator.py
│   ├── question_generator.py
│   ├── pdf_processor.py
│   └── bulgarian_processor.py
├── data/
│   ├── matura_21_05_2025.json
│   └── matura_2025_avgust.json
└── requirements.txt
```

## Technologies Used

- **Streamlit** - Web interface
- **OpenAI GPT** - AI question generation
- **ChromaDB** - Vector database
- **HuggingFace** - Embeddings
- **PyPDF2** - PDF processing
- **LangChain** - RAG orchestration

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy automatically

### Local Development
```bash
streamlit run app_real_matura.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details
