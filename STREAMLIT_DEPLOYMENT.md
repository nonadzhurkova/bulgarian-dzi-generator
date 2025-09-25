# 🚀 Streamlit Cloud Deployment Guide

## 📋 Quick Deployment Steps

### 1. Go to Streamlit Cloud
- Visit: https://share.streamlit.io
- Sign in with your GitHub account
- Click "New app"

### 2. Configure the App
- **Repository**: `nonadzhurkova/bulgarian-dzi-generator`
- **Branch**: `main`
- **Main file path**: `app_rag_generator.py`
- **Python version**: 3.11+

### 3. Environment Variables (Optional)
If you want to use OpenAI API for question generation:
```
OPENAI_API_KEY=your_api_key_here
```

### 4. Deploy
- Click "Deploy"
- Wait for the build to complete (~2-3 minutes)
- Your app will be available at: `https://your-app-name.streamlit.app`

## 🎯 What the App Includes

### Phase 1: Foundation ✅
- **Vector Analysis**: Analyze question patterns and topics
- **Similarity Search**: Find similar questions using embeddings
- **Cached Embeddings**: Fast startup with pre-computed vectors
- **Interactive Charts**: Visualize question patterns

### Phase 2: Generation (Requires OpenAI API)
- **Question Generation**: Generate new questions using RAG
- **Quality Validation**: Validate generated question quality
- **Topic-based Generation**: Generate questions by specific topics

## 📊 Performance Benefits

### With Pre-computed Embeddings:
- ⚡ **Fast Startup**: ~5-10 seconds (vs 30-60 seconds)
- 💾 **Memory Efficient**: No need to load large models
- 🔄 **Reliable**: No dependency on external model downloads
- 📱 **Mobile Friendly**: Faster loading on mobile devices

## 🔧 Local Testing

### Test Locally First:
```bash
# Test the RAG generator
python run_rag_generator.py
# Opens at http://localhost:8503

# Test the real matura app
python run_real_matura.py
# Opens at http://localhost:8502

# Test the basic generator
python run_questions.py
# Opens at http://localhost:8501
```

## 🎉 Expected Results

### After Deployment:
1. **Fast Loading**: App starts in ~5-10 seconds
2. **Vector Analysis**: Interactive charts showing question patterns
3. **Similarity Search**: Find similar questions instantly
4. **Question Generation**: Generate new questions (with OpenAI API)

## 🛠️ Troubleshooting

### Common Issues:
1. **Slow Startup**: Ensure `cache/embeddings_cache.pkl` is committed
2. **Memory Issues**: Use pre-computed embeddings
3. **Import Errors**: Check that all files are in the repository

### Cache Management:
```bash
# Re-generate cache if needed
python precompute_embeddings.py
git add cache/
git commit -m "Update embeddings cache"
git push
```

## 📈 Monitoring

### Streamlit Cloud Metrics:
- **Startup Time**: Should be < 10 seconds with cache
- **Memory Usage**: Should be < 1GB with cache
- **User Sessions**: Monitor active users

## 🎯 Success Criteria

### Phase 1 Complete ✅
- [x] Vector analysis working
- [x] Similarity search functional
- [x] Cached embeddings deployed
- [x] Fast startup achieved

### Phase 2 Goals
- [ ] OpenAI API integration
- [ ] Question generation working
- [ ] Quality validation implemented

---

**Ready for Deployment! 🚀**
