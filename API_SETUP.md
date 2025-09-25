# API Setup Instructions

## OpenAI API Key Setup

За да използваш RAG генериране (Phase 2), трябва да добавиш OpenAI API ключ.

### Вариант 1: Environment Variable (Препоръчителен)

1. Създай `.env` файл в root директорията:
```bash
# Копирай env.example в .env
cp env.example .env
```

2. Отвори `.env` файла и замени `your_openai_api_key_here` с твоя OpenAI API ключ:
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Вариант 2: Директно в config.py

1. Отвори `config.py`
2. Замени `"your_openai_api_key_here"` с твоя API ключ:
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-actual-openai-api-key-here")
```

### Как да получиш OpenAI API ключ:

1. Отиди на https://platform.openai.com/
2. Регистрирай се или влез в акаунта си
3. Отиди на API Keys секцията
4. Създай нов API ключ
5. Копирай ключа (започва с `sk-`)

### Тестване:

След като добавиш API ключа, рестартирай приложението:
```bash
streamlit run app_all_questions.py --server.port 8512
```

В sidebar-а избери "RAG генериране (Phase 2)" и опитай да генерираш въпроси.

## Без API ключ:

Ако нямаш OpenAI API ключ, можеш да използваш "Базов генератор" в dropdown менюто - той работи без API ключ.
