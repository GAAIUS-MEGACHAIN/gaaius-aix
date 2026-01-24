// Replicate AI Services for Image Editing
// Free tier ML models for professional image processing

const REPLICATE_API_URL = "https://api.replicate.com/v1";

// Free tier model versions (Replicate)
const FREE_MODELS = {
  UPSCALE: {
    id: "upscale",
    name: "AI Upscale 4x",
    version: "f217e1e4b61a1ce8f840d4ef722ba271c05fbbcb2couupc6pobahjyrf",
    description: "Real-ESRGAN upscaling"
  },
  BACKGROUND_REMOVE: {
    id: "bg_remove",
    name: "Remove Background",
    version: "fb9c5385f45748999f760f7a9aaf529352a53b582cb48aad66118b521309672a",
    description: "AI background removal"
  },
  ENHANCE: {
    id: "enhance",
    name: "AI Enhance",
    version: "42fed136c30513cc581f723a6fd569f27ef149f2486ad0d137cdbf2917b46589",
    description: "General image enhancement"
  },
  COLORIZE: {
    id: "colorize",
    name: "Colorize B&W",
    version: "c0c8e32f7a11f9e4b60bbf70a1f0cebdbbb91b3c1d7b5c1e8f0f5b7e7c5d5e3d",
    description: "Auto-colorize black & white images"
  },
  DENOISE: {
    id: "denoise",
    name: "Denoise",
    version: "63283c40c4534a00e1c1c6f36df629c0575933ea0439e82c41c03e2dcf55f41d",
    description: "Remove image noise"
  },
  RESTORE: {
    id: "restore",
    name: "Restore Photo",
    version: "c926b31c2b5e7c0c6e1b4a2d5e8f1c3e7a0d2b5c8e1f4a7d0b3e6f9c2e5a8d",
    description: "Restore old photos"
  },
  SEGMENT: {
    id: "segment",
    name: "Segment Objects",
    version: "87da227f51a5626af8cb53fc6f1939eaab82314eeb339970d7d309a3985e7d48",
    description: "Detect & segment objects"
  },
  DEPTH: {
    id: "depth",
    name: "Depth Map",
    version: "b6e3c7f0a2d1e4f8b5c9d2a6e1f4a8b3c6d9e2a5f8b1c4d7a0e3f6a9c2d5e",
    description: "Estimate depth map"
  }
};

class ReplicateAI {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.REACT_APP_REPLICATE_API_KEY;
    this.isConfigured = !!this.apiKey;
  }

  setApiKey(apiKey) {
    this.apiKey = apiKey;
    this.isConfigured = !!apiKey;
  }

  async request(endpoint, data) {
    if (!this.apiKey) {
      throw new Error("Replicate API key not configured");
    }

    const response = await fetch(`${REPLICATE_API_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Authorization": `Token ${this.apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.[0]?.msg || error.detail || "API request failed");
    }

    return response.json();
  }

  async pollPrediction(predictionId, onProgress) {
    let prediction = null;
    let attempts = 0;
    const maxAttempts = 600; // 10 minutes max

    while (attempts < maxAttempts) {
      const response = await fetch(
        `${REPLICATE_API_URL}/predictions/${predictionId}`,
        { headers: { "Authorization": `Token ${this.apiKey}` } }
      );

      prediction = await response.json();

      if (onProgress) {
        onProgress({
          status: prediction.status,
          completed_count: prediction.completed_count || 0,
          total_count: prediction.total_count || 1
        });
      }

      if (prediction.status === "succeeded") {
        return prediction.output;
      }
      if (prediction.status === "failed") {
        throw new Error(prediction.error || "Processing failed");
      }

      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
    }

    throw new Error("Processing timeout (10+ minutes)");
  }

  // Upscale image 4x using Real-ESRGAN
  async upscaleImage(imageUrl, onProgress) {
    const prediction = await this.request("/predictions", {
      version: FREE_MODELS.UPSCALE.version,
      input: { image: imageUrl }
    });
    return this.pollPrediction(prediction.id, onProgress);
  }

  // Remove background
  async removeBackground(imageUrl, onProgress) {
    const prediction = await this.request("/predictions", {
      version: FREE_MODELS.BACKGROUND_REMOVE.version,
      input: { image: imageUrl }
    });
    return this.pollPrediction(prediction.id, onProgress);
  }

  // Enhance image
  async enhanceImage(imageUrl, onProgress) {
    const prediction = await this.request("/predictions", {
      version: FREE_MODELS.ENHANCE.version,
      input: { image: imageUrl }
    });
    return this.pollPrediction(prediction.id, onProgress);
  }

  // Colorize black & white image
  async colorizeImage(imageUrl, onProgress) {
    const prediction = await this.request("/predictions", {
      version: FREE_MODELS.COLORIZE.version,
      input: { image: imageUrl }
    });
    return this.pollPrediction(prediction.id, onProgress);
  }

  // Denoise image
  async denoiseImage(imageUrl, strength = 0.5, onProgress) {
    const prediction = await this.request("/predictions", {
      version: FREE_MODELS.DENOISE.version,
      input: {
        image: imageUrl,
        denoise_strength: strength
      }
    });
    return this.pollPrediction(prediction.id, onProgress);
  }

  // Restore old photo
  async restorePhoto(imageUrl, onProgress) {
    const prediction = await this.request("/predictions", {
      version: FREE_MODELS.RESTORE.version,
      input: { image: imageUrl }
    });
    return this.pollPrediction(prediction.id, onProgress);
  }

  // Segment objects
  async segmentImage(imageUrl, onProgress) {
    const prediction = await this.request("/predictions", {
      version: FREE_MODELS.SEGMENT.version,
      input: { image: imageUrl }
    });
    return this.pollPrediction(prediction.id, onProgress);
  }

  // Depth estimation
  async depthMap(imageUrl, onProgress) {
    const prediction = await this.request("/predictions", {
      version: FREE_MODELS.DEPTH.version,
      input: { image: imageUrl }
    });
    return this.pollPrediction(prediction.id, onProgress);
  }

  // Utility: Convert canvas to data URL
  canvasToDataUrl(canvas) {
    return canvas.toDataURL("image/png");
  }

  // Utility: Load image from URL into canvas
  async loadImageIntoCanvas(imageUrl, canvas) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => {
        const ctx = canvas.getContext("2d");
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        resolve();
      };
      img.onerror = reject;
      img.src = imageUrl;
    });
  }

  // Get all available models
  getAvailableModels() {
    return Object.values(FREE_MODELS);
  }

  // Check if API is configured
  isReady() {
    return this.isConfigured;
  }
}

export default ReplicateAI;
export { FREE_MODELS };
