# Groq Integration Guide

## Overview

Groq provides **fast AI inference** (< 100ms) for intelligent copyright detection and claim assessment. Integrated into Phase 6+ for production-grade copyright management.

## Setup

### 1. Get Groq API Key
- Visit: https://console.groq.com
- Sign up (free account)
- Get your API key

### 2. Set Environment Variable
```bash
export GROQ_API_KEY="your-api-key-here"
```

Or in `.env`:
```
GROQ_API_KEY=your-api-key-here
```

### 3. Groq Automatically Initializes
```python
# In server.py, on startup:
groq_checker = GroqCopyrightChecker(os.environ.get('GROQ_API_KEY'))
```

## Usage Examples

### Example 1: Check if Track is Copyrighted
```python
from backend.phase6_groq import GroqCopyrightChecker

checker = GroqCopyrightChecker(api_key="your-key")

# Check a track
is_copyrighted, confidence = await checker.check_track(
    title="Blinding Lights",
    artist="The Weeknd"
)

print(f"Copyrighted: {is_copyrighted}")
print(f"Confidence: {confidence:.2%}")
```

**Response Example**:
```
Copyrighted: True
Confidence: 95%
```

### Example 2: Assess Copyright Claim
```python
claim_data = {
    "claimant": "Universal Music Group",
    "content_id": "video_12345",
    "reason": "Unauthorized use of 'Blinding Lights'",
    "evidence": ["audio_fingerprint", "metadata_match"]
}

assessment = checker.assess_claim(claim_data)
print(assessment)
```

**Response Example**:
```json
{
    "validity": "strong",
    "likelihood": "high",
    "action": "takedown",
    "risk": "high"
}
```

### Example 3: Integration in API Endpoint
```python
from fastapi import APIRouter, HTTPException
from backend.phase6_groq import GroqCopyrightChecker

router = APIRouter()
checker = GroqCopyrightChecker()

@router.post("/api/music/copyright-check")
async def check_copyright(title: str, artist: str):
    """Check if track is copyrighted using Groq AI"""
    try:
        is_copyrighted, confidence = await checker.check_track(title, artist)
        return {
            "title": title,
            "artist": artist,
            "is_copyrighted": is_copyrighted,
            "confidence": confidence,
            "recommendation": "flag" if is_copyrighted and confidence > 0.8 else "allow"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/copyright/assess-claim")
async def assess_claim(claim_data: dict):
    """Assess copyright claim validity using Groq"""
    assessment = checker.assess_claim(claim_data)
    return {
        "claim_assessment": assessment,
        "auto_action": assessment.get("action", "review")
    }
```

## Groq Model Options

**Current Model**: `mixtral-8x7b-32768` (recommended)
- Fast inference
- Good for copyright detection
- Handles structured output
- Free tier includes

**Alternative Models**:
- `llama-3.1-8b-instant` - Faster, less capable
- `llama-3.1-70b-versatile` - More powerful, slower

## Response Format

### Copyright Check Response
```python
is_copyrighted: bool       # True if copyrighted
confidence: float          # 0.0-1.0 confidence score
```

### Claim Assessment Response
```json
{
    "validity": "strong|moderate|weak",
    "likelihood": "high|medium|low",
    "action": "takedown|monitor|dismiss",
    "risk": "high|medium|low"
}
```

## Error Handling

### Groq Unavailable Fallback
```python
checker = GroqCopyrightChecker()  # No key provided

is_copyrighted, confidence = await checker.check_track("title", "artist")
# Returns: (False, 0.5) - neutral fallback

assessment = checker.assess_claim(claim_data)
# Returns: {"validity": "unknown"} - safe fallback
```

### API Errors
```python
try:
    result = await checker.check_track(title, artist)
except Exception as e:
    logger.error(f"Groq error: {e}")
    # Fallback to conservative approach
    return fallback_result
```

## Performance Metrics

- **Latency**: < 100ms per request
- **Cache**: 24-hour analysis cache
- **Throughput**: Suitable for production scale
- **Cost**: Free tier available (recommended for initial setup)

## Advanced Usage

### Batch Copyright Checks
```python
tracks = [
    {"title": "Song 1", "artist": "Artist 1"},
    {"title": "Song 2", "artist": "Artist 2"},
]

results = []
for track in tracks:
    is_copy, conf = await checker.check_track(
        track["title"], 
        track["artist"]
    )
    results.append({
        "track": track,
        "is_copyrighted": is_copy,
        "confidence": conf
    })

return results
```

### Custom Prompt Engineering
```python
# Modify check_track() in phase6_groq.py to customize behavior:
prompt = f"""
You are a copyright expert. Analyze if this is likely a copyrighted work.
Consider: major labels, known artists, track patterns.

Title: {title}
Artist: {artist}

Respond ONLY with: yes/no and 0.0-1.0 confidence
"""
```

## When to Use Groq vs. Local Detection

**Use Groq for**:
- Claim assessment
- Metadata analysis
- Contextual decisions
- When confidence needed
- High-stakes claims

**Use Local Detection for**:
- Audio fingerprinting (client-side)
- Real-time filtering
- High-volume scanning
- Bandwidth-limited environments

## Cost Estimation

**Free Tier**: 
- Up to 30K requests/month
- Enough for: ~1M tracks (1 check per month)
- No credit card required

**Paid Tiers**:
- Per-request pricing after free tier
- Typically < $0.001 per request

## Troubleshooting

### "Groq not installed"
```bash
pip install groq
```

### "API key not found"
```bash
# Check environment
python -c "import os; print(os.environ.get('GROQ_API_KEY'))"
```

### "Rate limit exceeded"
```python
# Built-in caching handles this
# Results cached for 24 hours
# Retry after cache miss succeeds
```

## Best Practices

1. **Always have fallback**: Groq unavailability shouldn't break platform
2. **Cache aggressively**: Same track checked multiple times = waste
3. **Use appropriate thresholds**: confidence > 0.7 for action
4. **Log all assessments**: Track Groq decisions for improvement
5. **Monitor latency**: Watch for performance degradation
6. **Batch when possible**: Reduce API calls

## Integration Checklist

- ✅ API key in environment
- ✅ Groq package installed (`pip install groq`)
- ✅ GroqCopyrightChecker initialized
- ✅ Fallback system in place
- ✅ Error handling configured
- ✅ Logging enabled
- ✅ Performance monitoring ready

## Example: Full Integration

```python
import os
import asyncio
from backend.phase6_groq import GroqCopyrightChecker

async def main():
    # Initialize with API key
    api_key = os.environ.get('GROQ_API_KEY')
    checker = GroqCopyrightChecker(api_key=api_key)
    
    # Check a track
    title = "Blinding Lights"
    artist = "The Weeknd"
    
    is_copyrighted, confidence = await checker.check_track(title, artist)
    
    print(f"Track: {title} by {artist}")
    print(f"Copyrighted: {is_copyrighted}")
    print(f"Confidence: {confidence:.2%}")
    
    if is_copyrighted and confidence > 0.8:
        print("Action: Flag for review")
    else:
        print("Action: Allow upload")

if __name__ == "__main__":
    asyncio.run(main())
```

## Support

- Groq Docs: https://console.groq.com/docs
- Discord: https://discord.gg/groq
- Status: https://status.groq.com
