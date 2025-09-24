# 🚀 Deployment Guide for Streamlit Cloud

## 📋 Overview
This guide explains how to deploy the RAG Question Generator to Streamlit Cloud with pre-computed embeddings for fast startup.

## 🔧 Pre-deployment Setup

### 1. Pre-compute Embeddings
```bash
# Run this once locally to create cache files
python precompute_embeddings.py
```

This creates:
- `cache/embeddings_cache.pkl` - Pre-computed embeddings
- Fast startup on Streamlit Cloud (no need to compute embeddings each time)

### 2. Commit Cache Files
```bash
# Add cache files to git
git add cache/
git commit -m "Add pre-computed embeddings for Streamlit Cloud"
git push
```

## 🌐 Streamlit Cloud Deployment

### 1. Connect GitHub Repository
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository: `nonadzhurkova/bulgarian-dzi-generator`

### 2. Configure App Settings
- **Main file path**: `app_rag_generator.py`
- **Python version**: 3.11+
- **Branch**: `main`

### 3. Environment Variables (Optional)
If you want to use OpenAI API for question generation:
```
OPENAI_API_KEY=your_api_key_here
```

### 4. Deploy
Click "Deploy" and wait for the build to complete.

## 🎯 App Features

### Phase 1: Foundation ✅
- **Vector Analysis**: Analyze question patterns and topics
- **Similarity Search**: Find similar questions using embeddings
- **Cached Embeddings**: Fast startup with pre-computed vectors

### Phase 2: Generation (Requires OpenAI API)
- **Question Generation**: Generate new questions using RAG
- **Quality Validation**: Validate generated question quality
- **Topic-based Generation**: Generate questions by specific topics

### Phase 3: Optimization (Future)
- **User Testing**: Collect feedback on generated questions
- **Parameter Tuning**: Optimize generation parameters
- **Feedback Loop**: Improve based on user interactions

## 📊 Performance Benefits

### With Pre-computed Embeddings:
- ⚡ **Fast Startup**: ~5-10 seconds (vs 30-60 seconds)
- 💾 **Memory Efficient**: No need to load large models
- 🔄 **Reliable**: No dependency on external model downloads
- 📱 **Mobile Friendly**: Faster loading on mobile devices

### Without Pre-computed Embeddings:
- 🐌 **Slow Startup**: 30-60 seconds to compute embeddings
- 💸 **Expensive**: High memory usage on Streamlit Cloud
- ⚠️ **Unreliable**: May fail due to memory limits

## 🛠️ Local Development

### Run RAG Generator Locally
```bash
# Start the RAG generator app
python run_rag_generator.py
# Opens at http://localhost:8503
```

### Run Real Matura App
```bash
# Start the real matura questions app
python run_real_matura.py
# Opens at http://localhost:8502
```

### Run Question Generator
```bash
# Start the basic question generator
python run_questions.py
# Opens at http://localhost:8501
```

## 🔍 Troubleshooting

### Common Issues

1. **Slow Startup**
   - Ensure `cache/embeddings_cache.pkl` exists
   - Check that cache files are committed to GitHub

2. **Memory Issues**
   - Use pre-computed embeddings
   - Reduce batch size in embedding computation

3. **API Key Issues**
   - Set `OPENAI_API_KEY` environment variable
   - Check API key validity

### Cache Management
```bash
# Clear cache (if needed)
rm -rf cache/
python precompute_embeddings.py
```

## 📈 Monitoring

### Streamlit Cloud Metrics
- **Startup Time**: Should be < 10 seconds with cache
- **Memory Usage**: Should be < 1GB with cache
- **User Sessions**: Monitor active users

### Performance Optimization
- Use smaller embedding models for faster computation
- Implement lazy loading for large datasets
- Add progress bars for long operations

## 🎉 Success Metrics

### Phase 1 Complete ✅
- [x] Vector analysis working
- [x] Similarity search functional
- [x] Cached embeddings deployed
- [x] Fast startup achieved

### Phase 2 Goals
- [ ] OpenAI API integration
- [ ] Question generation working
- [ ] Quality validation implemented

### Phase 3 Goals
- [ ] User feedback collection
- [ ] Parameter optimization
- [ ] Performance monitoring

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Streamlit Cloud logs
3. Test locally first
4. Check GitHub issues

---

**Happy Deploying! 🚀**
