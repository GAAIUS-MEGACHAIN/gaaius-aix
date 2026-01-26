# 🚀 AI Image Editor - Quick Start

## 30-Second Setup

1. **Get API Key** (FREE)
   ```
   Go to https://replicate.com
   Click "Sign Up" (free, no card needed)
   Copy your API token
   ```

2. **Add to Frontend**
   ```
   Create: frontend/.env.local
   Add: REACT_APP_REPLICATE_API_KEY=your_key
   ```

3. **Use It**
   ```
   Open Image Editor
   Click "AI Tools" button
   Or paste key directly in panel
   Upload image → Click any AI tool
   ```

## Available AI Effects

| Effect | What It Does | Time |
|--------|-------------|------|
| **AI Upscale 4x** | Make image 4x bigger (cleaner) | 5-10s |
| **Remove Background** | Clear white/transparent bg | 3-5s |
| **AI Enhance** | Make image sharper/clearer | 2-3s |
| **Colorize B&W** | Auto-color black & white | 3-5s |
| **Denoise** | Remove noise/grain | 2-3s |
| **Restore Photo** | Fix old/damaged photos | 5-10s |
| **Segment Objects** | Detect & isolate objects | 3-5s |
| **Depth Map** | Create 3D depth map | 3-5s |

## Feature Highlights

✅ All results become **new layers** (non-destructive)
✅ Stack multiple AI effects
✅ Combine with manual drawing/editing
✅ **FREE** (no credit card ever)
✅ **FAST** (3-10 seconds per effect)
✅ **POWERFUL** (production ML models)

## Example Workflow

```
1. Upload photo (512x512)
2. Click "AI Upscale 4x" → Gets 2048x2048
3. Click "Remove Background" → Gets transparent
4. Manually draw/paint on layer
5. Click "AI Enhance" → Sharpen result
6. Export PNG/JPG
```

## Troubleshooting

**Q: "No API key configured"**
- A: Click AI Tools → Paste Replicate key

**Q: "API request failed"**
- A: Check internet, verify API key at replicate.com

**Q: Effect takes too long**
- A: Normal (3-10 seconds), results will appear as new layer

**Q: Results look off**
- A: Try different effect or adjust original image

## Tips

1. **Best quality**: Start with high-res images
2. **Fast results**: Use enhance instead of upscale for quick edits
3. **Remove backgrounds**: Works best on solid backgrounds
4. **Restore photos**: Great for old/scanned images
5. **Stack effects**: Combine multiple AI tools for creative results

## Free vs Paid

**FREE**: 100 calls/day, all effects
**PAID**: Unlimited calls, priority queue

Both have same quality output.

---

**Get Started Now!** 🎨
