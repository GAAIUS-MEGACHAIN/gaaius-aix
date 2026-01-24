"""
ML ENHANCEMENTS FOR BUILD SYSTEM
Adds ML model support to generated projects
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class MLModel(Enum):
    """Available free ML models"""
    # Text Models
    SENTIMENT_ANALYSIS = "sentiment-analysis"
    TEXT_CLASSIFICATION = "text-classification"
    NER = "named-entity-recognition"
    TEXT_SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    QUESTION_ANSWERING = "question-answering"
    
    # Vision Models
    OBJECT_DETECTION = "object-detection"
    IMAGE_CLASSIFICATION = "image-classification"
    POSE_DETECTION = "pose-detection"
    FACE_DETECTION = "face-detection"
    SEMANTIC_SEGMENTATION = "semantic-segmentation"
    HAND_TRACKING = "hand-tracking"
    
    # Audio Models
    SPEECH_RECOGNITION = "speech-recognition"
    AUDIO_CLASSIFICATION = "audio-classification"
    
    # Generative Models
    TEXT_GENERATION = "text-generation"
    IMAGE_GENERATION = "image-generation"
    IMAGE_TO_TEXT = "image-to-text"
    
    # Embeddings
    FEATURE_EXTRACTION = "feature-extraction"
    SENTENCE_SIMILARITY = "sentence-similarity"


class MLFramework(Enum):
    """ML frameworks to integrate"""
    TENSORFLOW_JS = "tensorflow-js"
    TRANSFORMERS_JS = "transformers-js"
    PYTORCH = "pytorch"
    SCIKIT_LEARN = "scikit-learn"
    FAST_AI = "fast-ai"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


@dataclass
class MLModelConfig:
    """ML model configuration"""
    model_id: str
    model_name: str
    provider: str  # huggingface, tensorflow, pytorch, custom
    framework: str
    size_mb: int
    task: str
    languages: List[str] = None
    requires_gpu: bool = False
    supports_web: bool = False
    supports_mobile: bool = False
    npm_packages: List[str] = None
    pip_packages: List[str] = None
    setup_instructions: str = ""
    example_code: str = ""
    cost: str = "free"


# ============================================================================
# ML MODELS REGISTRY
# ============================================================================

ML_MODELS_REGISTRY = {
    # TEXT MODELS
    MLModel.SENTIMENT_ANALYSIS: MLModelConfig(
        model_id="distilbert-base-uncased-finetuned-sst-2",
        model_name="DistilBERT Sentiment",
        provider="huggingface",
        framework="transformers",
        size_mb=250,
        task="text-classification",
        languages=["en"],
        supports_web=True,
        npm_packages=["@xenova/transformers"],
        example_code="""
import { pipeline } from "@xenova/transformers";

const classifier = await pipeline('text-classification');
const result = await classifier("I love this!");
console.log(result); // { label: 'POSITIVE', score: 0.99 }
        """,
        cost="free"
    ),
    
    MLModel.NER: MLModelConfig(
        model_id="dslim-bert-base-NER",
        model_name="BERT Named Entity Recognition",
        provider="huggingface",
        framework="transformers",
        size_mb=350,
        task="token-classification",
        languages=["en"],
        supports_web=True,
        npm_packages=["@xenova/transformers"],
        example_code="""
import { pipeline } from "@xenova/transformers";

const ner = await pipeline('token-classification');
const entities = await ner("John works at Google");
console.log(entities); // Extracts PERSON, ORG, etc.
        """,
        cost="free"
    ),
    
    MLModel.TEXT_SUMMARIZATION: MLModelConfig(
        model_id="facebook/bart-large-cnn",
        model_name="BART Summarization",
        provider="huggingface",
        framework="transformers",
        size_mb=1600,
        task="summarization",
        languages=["en"],
        supports_web=True,
        npm_packages=["@xenova/transformers"],
        example_code="""
import { pipeline } from "@xenova/transformers";

const summarizer = await pipeline('summarization');
const result = await summarizer(longText);
console.log(result[0].summary_text);
        """,
        cost="free"
    ),
    
    MLModel.TRANSLATION: MLModelConfig(
        model_id="Helsinki-NLP/opus-mt-en-es",
        model_name="Helsinki Translation",
        provider="huggingface",
        framework="transformers",
        size_mb=800,
        task="translation",
        languages=["100+"],
        supports_web=True,
        npm_packages=["@xenova/transformers"],
        example_code="""
import { pipeline } from "@xenova/transformers";

const translator = await pipeline('translation_en_to_es');
const result = await translator("Hello");
console.log(result[0].translation_text);
        """,
        cost="free"
    ),
    
    MLModel.QUESTION_ANSWERING: MLModelConfig(
        model_id="deepset/roberta-base-squad2",
        model_name="RoBERTa Question Answering",
        provider="huggingface",
        framework="transformers",
        size_mb=450,
        task="question-answering",
        languages=["en"],
        supports_web=True,
        npm_packages=["@xenova/transformers"],
        example_code="""
import { pipeline } from "@xenova/transformers";

const qa = await pipeline('question-answering');
const result = await qa({
    question: "What is X?",
    context: "X is..."
});
console.log(result.answer);
        """,
        cost="free"
    ),
    
    # VISION MODELS
    MLModel.OBJECT_DETECTION: MLModelConfig(
        model_id="yolov5s",
        model_name="YOLOv5 Small",
        provider="tensorflow",
        framework="tensorflow-js",
        size_mb=100,
        task="object-detection",
        languages=[],
        supports_web=True,
        npm_packages=["@tensorflow/tfjs", "@tensorflow-models/coco-ssd"],
        example_code="""
import * as tf from "@tensorflow/tfjs";
import * as cocoSsd from "@tensorflow-models/coco-ssd";

const model = await cocoSsd.load();
const predictions = await model.estimateObjects(image);
console.log(predictions); // { class, score, bbox }
        """,
        cost="free"
    ),
    
    MLModel.POSE_DETECTION: MLModelConfig(
        model_id="posenet-mobilenet",
        model_name="PoseNet Mobile",
        provider="tensorflow",
        framework="tensorflow-js",
        size_mb=50,
        task="pose-estimation",
        languages=[],
        supports_web=True,
        supports_mobile=True,
        npm_packages=["@tensorflow/tfjs", "@tensorflow-models/pose-detection"],
        example_code="""
import * as tf from "@tensorflow/tfjs";
import * as poseDetection from "@tensorflow-models/pose-detection";

const model = await poseDetection.load();
const poses = await model.estimatePoses(video);
console.log(poses[0].keypoints); // 17 body points
        """,
        cost="free"
    ),
    
    MLModel.IMAGE_CLASSIFICATION: MLModelConfig(
        model_id="mobilenet-v2",
        model_name="MobileNet v2",
        provider="tensorflow",
        framework="tensorflow-js",
        size_mb=40,
        task="image-classification",
        languages=[],
        supports_web=True,
        supports_mobile=True,
        npm_packages=["@tensorflow/tfjs", "@tensorflow-models/mobilenet"],
        example_code="""
import * as tf from "@tensorflow/tfjs";
import * as mobilenet from "@tensorflow-models/mobilenet";

const model = await mobilenet.load();
const predictions = await model.classify(image);
console.log(predictions); // Top 3 class predictions
        """,
        cost="free"
    ),
    
    MLModel.FACE_DETECTION: MLModelConfig(
        model_id="mediapipe-face-detection",
        model_name="MediaPipe Face",
        provider="google",
        framework="tensorflow-js",
        size_mb=30,
        task="face-detection",
        languages=[],
        supports_web=True,
        supports_mobile=True,
        npm_packages=["@mediapipe/tasks-vision", "@tensorflow/tfjs"],
        example_code="""
import { FaceDetector, FilesetResolver } from "@mediapipe/tasks-vision";

const detector = await FaceDetector.createFromOptions(...);
const result = detector.detect(image);
console.log(result.detections); // Face locations
        """,
        cost="free"
    ),
    
    MLModel.HAND_TRACKING: MLModelConfig(
        model_id="mediapipe-hands",
        model_name="MediaPipe Hands",
        provider="google",
        framework="tensorflow-js",
        size_mb=25,
        task="hand-tracking",
        languages=[],
        supports_web=True,
        supports_mobile=True,
        npm_packages=["@mediapipe/tasks-vision", "@tensorflow/tfjs"],
        example_code="""
import { HandLandmarker } from "@mediapipe/tasks-vision";

const landmarker = await HandLandmarker.createFromOptions(...);
const result = landmarker.detect(video);
console.log(result.landmarks); // 21-point hand mesh
        """,
        cost="free"
    ),
    
    # AUDIO MODELS
    MLModel.SPEECH_RECOGNITION: MLModelConfig(
        model_id="openai/whisper-base",
        model_name="Whisper Small",
        provider="openai",
        framework="transformers",
        size_mb=500,
        task="speech-recognition",
        languages=["99"],
        pip_packages=["openai-whisper"],
        example_code="""
import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.mp3")
print(result["text"]) # Transcribed text
        """,
        cost="free"
    ),
    
    # GENERATIVE MODELS
    MLModel.TEXT_GENERATION: MLModelConfig(
        model_id="mistral-7b",
        model_name="Mistral 7B",
        provider="mistral",
        framework="ollama",
        size_mb=4000,
        task="text-generation",
        languages=["en"],
        requires_gpu=False,
        example_code="""
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral",
        "prompt": "Write a poem about AI",
        "stream": False
    }
)
print(response.json()["response"])
        """,
        cost="free"
    ),
    
    MLModel.IMAGE_GENERATION: MLModelConfig(
        model_id="stable-diffusion-xl",
        model_name="Stable Diffusion XL",
        provider="stability",
        framework="ollama",
        size_mb=6000,
        task="image-generation",
        languages=[],
        requires_gpu=True,
        example_code="""
# Option 1: Ollama
docker run --gpus all ollama/ollama
ollama pull sdxl

# Option 2: Stability API
import requests
response = requests.post(
    "https://api.stability.ai/v1/generate/text-to-image",
    headers={"Authorization": "Bearer YOUR_KEY"},
    json={"text_prompts": [{"text": "A cat"}]}
)
        """,
        cost="free (local) / $0.025/image (API)"
    ),
}


# ============================================================================
# ML ENHANCEMENT TEMPLATES
# ============================================================================

class MLEnhancementTemplates:
    """Code templates for ML integration"""
    
    @staticmethod
    def get_react_ml_setup() -> str:
        """Setup ML for React project"""
        return """
// Install ML packages
npm install @xenova/transformers @tensorflow/tfjs @tensorflow-models/coco-ssd

// Create ML service
// src/services/mlService.js
import { pipeline } from "@xenova/transformers";

export async function loadModel(modelType) {
  return await pipeline(modelType);
}

export async function classifyText(text, model) {
  const result = await model(text);
  return result;
}

// Use in component
import { loadModel, classifyText } from './services/mlService';

export function TextAnalyzer() {
  const [result, setResult] = useState(null);
  const modelRef = useRef(null);
  
  useEffect(() => {
    loadModel('text-classification').then(m => modelRef.current = m);
  }, []);
  
  const analyze = async (text) => {
    const res = await classifyText(text, modelRef.current);
    setResult(res[0]);
  };
  
  return (
    <div>
      <input onChange={(e) => analyze(e.target.value)} />
      {result && <p>{result.label}: {result.score.toFixed(2)}</p>}
    </div>
  );
}
        """
    
    @staticmethod
    def get_fastapi_ml_setup() -> str:
        """Setup ML for FastAPI backend"""
        return """
# Install packages
pip install fastapi uvicorn transformers torch pillow

# main.py
from fastapi import FastAPI, File, UploadFile
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
classifier = pipeline("sentiment-analysis")
summarizer = pipeline("summarization")

@app.post("/classify")
async def classify(text: str):
    result = classifier(text)
    return result[0]

@app.post("/summarize")
async def summarize(text: str):
    result = summarizer(text, max_length=100)
    return result[0]

# Run: uvicorn main:app --reload
        """
    
    @staticmethod
    def get_ollama_setup() -> str:
        """Setup local Ollama LLM"""
        return """
# Install Ollama
# Windows: Download from ollama.ai
# Linux: curl https://ollama.ai/install.sh | sh
# macOS: brew install ollama

# Start Ollama
ollama serve

# Pull models
ollama pull mistral      # Fast and smart (7B)
ollama pull llama2       # Balanced (7B)
ollama pull phi          # Ultra-fast (2.7B)
ollama pull neural-chat  # Conversation optimized (7B)

# Test
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Hello!",
  "stream": false
}'

# Python integration
import requests
import json

def chat_with_ollama(message):
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'mistral',
            'prompt': message,
            'stream': False
        }
    )
    return response.json()['response']
        """


# ============================================================================
# ML FRAMEWORK TEMPLATES
# ============================================================================

ML_FRAMEWORK_TEMPLATES = {
    "react-with-ml": {
        "description": "React project with ML capabilities",
        "packages": ["@xenova/transformers", "@tensorflow/tfjs", "@tensorflow-models/coco-ssd"],
        "setup": MLEnhancementTemplates.get_react_ml_setup(),
        "features": ["sentiment-analysis", "object-detection", "text-classification"]
    },
    "fastapi-ml": {
        "description": "FastAPI backend with ML models",
        "packages": ["transformers", "torch", "pillow"],
        "setup": MLEnhancementTemplates.get_fastapi_ml_setup(),
        "features": ["sentiment-analysis", "summarization", "translation"]
    },
    "ollama-llm": {
        "description": "Local LLM with Ollama",
        "packages": ["ollama"],
        "setup": MLEnhancementTemplates.get_ollama_setup(),
        "features": ["text-generation", "chat", "code-generation"]
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_by_task(task: str) -> Optional[MLModelConfig]:
    """Get model recommendation for a task"""
    for model, config in ML_MODELS_REGISTRY.items():
        if config.task == task:
            return config
    return None


def get_web_compatible_models() -> List[tuple]:
    """Get all models that run in browser"""
    return [
        (model, config) 
        for model, config in ML_MODELS_REGISTRY.items() 
        if config.supports_web
    ]


def get_mobile_compatible_models() -> List[tuple]:
    """Get all models that run on mobile"""
    return [
        (model, config) 
        for model, config in ML_MODELS_REGISTRY.items() 
        if config.supports_mobile
    ]


def get_free_models() -> List[tuple]:
    """Get all free models"""
    return [
        (model, config) 
        for model, config in ML_MODELS_REGISTRY.items() 
        if "free" in config.cost.lower()
    ]


def add_ml_to_build_config(framework: str, models: List[str]) -> Dict:
    """Add ML configuration to build config"""
    return {
        "framework": framework,
        "ml_models": models,
        "npm_packages": [],
        "pip_packages": [],
        "setup_instructions": ""
    }


if __name__ == "__main__":
    print("=" * 70)
    print("ML ENHANCEMENTS REGISTRY")
    print("=" * 70)
    
    print(f"\nTotal Models: {len(ML_MODELS_REGISTRY)}")
    print(f"Web-compatible: {len(get_web_compatible_models())}")
    print(f"Mobile-compatible: {len(get_mobile_compatible_models())}")
    print(f"Free Models: {len(get_free_models())}")
    
    print("\n" + "=" * 70)
    print("ALL AVAILABLE MODELS")
    print("=" * 70)
    
    for model_enum, config in ML_MODELS_REGISTRY.items():
        print(f"\n{model_enum.value}")
        print(f"  Name: {config.model_name}")
        print(f"  Task: {config.task}")
        print(f"  Size: {config.size_mb}MB")
        print(f"  Web: {'✓' if config.supports_web else '✗'}")
        print(f"  Mobile: {'✓' if config.supports_mobile else '✗'}")
        print(f"  Cost: {config.cost}")
