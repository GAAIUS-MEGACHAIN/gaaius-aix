# ML + Build System - Quick Reference Card

## 🚀 Start Server
```bash
python -m uvicorn backend.ml_api_server:app --reload --port 8000
```

## 📋 CLI Commands

### Model Operations
```bash
# List all models
python -m backend.ml_cli models

# Load model
python -m backend.ml_cli load-model --model distilbert-sentiment

# Unload model
python -m backend.ml_cli unload-model --model distilbert-sentiment

# Run inference
python -m backend.ml_cli infer --text "Your text here" --model distilbert-sentiment

# Benchmark model (10 runs)
python -m backend.ml_cli benchmark --models distilbert-sentiment bert-ner --runs 10
```

### Framework Operations
```bash
# List frameworks
python -m backend.ml_cli frameworks

# Build with ML integration
python -m backend.ml_cli build \
  --framework fastapi \
  --models distilbert-sentiment bert-ner \
  --optimize int8 \
  --device cuda \
  --build-type release
```

### System Operations
```bash
# Check health
python -m backend.ml_cli health

# View statistics
python -m backend.ml_cli stats

# Initialize database
python -m backend.ml_cli init-db
```

## 🌐 API Endpoints

### Text Analysis
```bash
# Sentiment Analysis
curl -X POST http://localhost:8000/api/v1/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "This is great!", "model": "distilbert-sentiment"}'

# Named Entity Recognition
curl -X POST http://localhost:8000/api/v1/ner \
  -H "Content-Type: application/json" \
  -d '{"text": "John works at Google in NYC"}'

# Summarization
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Long text to summarize...", "model": "t5-base"}'

# Translation
curl -X POST http://localhost:8000/api/v1/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "source_lang": "en", "target_lang": "es"}'

# Question Answering
curl -X POST http://localhost:8000/api/v1/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "context": "Python is a programming language",
    "model": "roberta-qa"
  }'
```

### Model Management
```bash
# List all models
curl http://localhost:8000/api/v1/models

# Get model info
curl http://localhost:8000/api/v1/models/distilbert-sentiment

# Load model
curl -X POST http://localhost:8000/api/v1/models/distilbert-sentiment/load \
  -H "Content-Type: application/json" \
  -d '{"optimize": true}'

# Unload model
curl -X POST http://localhost:8000/api/v1/models/distilbert-sentiment/unload

# Benchmark model
curl -X POST http://localhost:8000/api/v1/benchmark/distilbert-sentiment \
  -H "Content-Type: application/json" \
  -d '{"num_runs": 10}'
```

### Monitoring
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Server statistics
curl http://localhost:8000/api/v1/stats
```

## 📊 Available Models

| Model | Task | Command |
|-------|------|---------|
| distilbert-sentiment | Sentiment Analysis | `--model distilbert-sentiment` |
| bert-ner | Named Entity Recognition | `--model bert-ner` |
| t5-base | Summarization | `--model t5-base` |
| marian-translation | Translation | `--model marian-translation` |
| roberta-qa | Question Answering | `--model roberta-qa` |
| yolov5s | Object Detection | `--model yolov5s` |
| mobilenet-v2 | Image Classification | `--model mobilenet-v2` |
| posenet | Pose Estimation | `--model posenet` |
| whisper-base | Speech Recognition | `--model whisper-base` |
| mistral-7b | Text Generation | `--model mistral-7b` |

## 🏗️ Supported Frameworks

### Desktop
- tauri, electron, pyqt6, wxwidgets

### Mobile
- flutter, react-native, expo, ionic, nativescript

### Web
- react, angular, vue, svelte, vite, next, nuxt, remix, sveltekit, astro, qwik, solidstart

### Backend
- fastapi, django, flask, fastapi-ml, express, nestjs

### ML/Data
- streamlit, gradio, jupyter

## 🐳 Docker Deployment

```bash
# Build image
docker build -f Dockerfile.ml -t ml-api-server .

# Run container
docker run -p 8000:8000 \
  -e CUDA_VISIBLE_DEVICES=0 \
  ml-api-server

# Run with GPU support
docker run --gpus all -p 8000:8000 ml-api-server

# Run with volume mount
docker run -p 8000:8000 \
  -v /path/to/models:/app/models \
  ml-api-server
```

## 📦 Python API Usage

```python
import asyncio
from backend.ml_build_executor import MLBuildExecutor, MLBuildConfig
from backend.ml_database import MLDatabaseManager

async def main():
    # Initialize
    db = MLDatabaseManager()
    executor = MLBuildExecutor(db)
    await executor.initialize()
    
    # Build with ML
    config = MLBuildConfig(
        framework="fastapi",
        include_ml_models=["distilbert-sentiment", "bert-ner"],
        ml_optimization="int8",
        optimize_for_device="cuda",
        compress_artifacts=True
    )
    
    result = await executor.build_with_ml(config)
    
    print(f"Status: {result.status}")
    print(f"Time: {result.total_time_seconds:.2f}s")
    print(f"Binary: {result.binary_path}")
    
    await executor.shutdown()

asyncio.run(main())
```

## 🧪 Testing

```bash
# All tests
pytest backend/test_ml_production.py -v

# Specific test class
pytest backend/test_ml_production.py::TestMLDatabase -v

# With coverage
pytest backend/test_ml_production.py --cov=backend --cov-report=html

# Run quickly
pytest backend/test_ml_production.py -x --tb=short
```

## 🔧 Configuration

### Environment Variables (.env.ml)
```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ML_DEVICE=cuda              # cuda or cpu
ML_OPTIMIZATION=int8        # none, int8, float16, distill
DATABASE_URL=sqlite:///./ml_models.db
LOG_LEVEL=INFO
OLLAMA_HOST=http://localhost:11434
```

### Build Config
```python
MLBuildConfig(
    framework="fastapi",           # Required
    build_type="release",          # debug, release, optimize
    include_ml_models=[...],       # List of model keys
    ml_optimization="int8",        # none, int8, float16, distill
    optimize_for_device="cpu",     # cpu, cuda, metal
    quantize_models=True,          # Enable quantization
    bundle_ollama=False,           # Bundle Ollama server
    compress_artifacts=True,       # Compress output
    enable_inference_cache=True    # Enable caching
)
```

## 📈 Performance Tips

1. **Use Quantization**: Reduces size by 75%, minimal accuracy loss
   ```bash
   --optimize int8
   ```

2. **Batch Requests**: 5-10x faster for multiple inputs
   ```bash
   /api/v1/batch-sentiment
   ```

3. **Use GPU**: 10-50x faster
   ```bash
   python -m backend.ml_cli build --device cuda
   ```

4. **Cache Results**: Keep models loaded
   ```bash
   python -m backend.ml_cli load-model --model distilbert-sentiment
   ```

5. **Monitor Stats**: Track performance
   ```bash
   python -m backend.ml_cli stats
   ```

## 🐛 Troubleshooting

### Check CUDA
```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

### Reset Database
```bash
rm ml_models.db
python -m backend.ml_cli init-db
```

### View Logs
```bash
tail -f ml_api.log
```

### Test Inference
```bash
python -m backend.ml_cli infer --text "test" --model distilbert-sentiment
```

## 📚 Documentation Files

- `ML_PRODUCTION_GUIDE.md` - Complete user guide (1000+ lines)
- `ML_PRODUCTION_COMPLETE.md` - Status and features
- `ML_API_QUICK_REFERENCE.md` - This file

## 🚨 Important Paths

```
backend/
├── ml_inference_engine.py      # ML inference core
├── ml_api_server.py             # FastAPI REST server
├── ml_database.py               # Database layer
├── ml_build_executor.py         # Build orchestration
├── ml_cli.py                    # CLI tools
├── test_ml_production.py        # Test suite
└── ML_PRODUCTION_GUIDE.md       # Documentation

Deployment:
├── deploy_production.py         # One-click setup
├── Dockerfile.ml                # Docker image
└── .env.ml                      # Configuration
```

## ✅ Pre-Flight Checklist

Before deployment:
- [ ] `python deploy_production.py` completed successfully
- [ ] `pytest backend/test_ml_production.py` all passing
- [ ] `python -m backend.ml_cli health` shows all healthy
- [ ] `python -m backend.ml_cli models` lists 10 models
- [ ] `curl http://localhost:8000/api/v1/health` returns 200

## 🎯 Common Tasks

### Run a sentiment analysis
```bash
python -m backend.ml_cli infer --text "I love this!" --model distilbert-sentiment
```

### Build React app with ML
```bash
python -m backend.ml_cli build \
  --framework react \
  --models distilbert-sentiment mobilenet-v2 \
  --optimize int8
```

### Benchmark all models
```bash
python -m backend.ml_cli benchmark \
  --models distilbert-sentiment bert-ner roberta-qa \
  --runs 10
```

### Monitor system
```bash
while true; do
  python -m backend.ml_cli stats
  sleep 5
done
```

---

**Last Updated**: January 23, 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
