# LLM Service Setup Guide

The CPSC Regulation System now supports real LLM models for generating analysis, summaries, and justifications.

## Two Options Available

### Option 1: Local Model (FLAN-T5) - FREE & DEFAULT ✅

Uses Google's FLAN-T5-base model that runs on your machine.

**Advantages:**
- ✅ Completely free
- ✅ No API keys needed
- ✅ Works offline
- ✅ Good quality for regulatory text

**Setup:**

1. Install the required dependencies (if not already installed):
   ```bash
   cd cpsc-regulation-system/backend
   pip install -r requirements.txt
   ```

2. That's it! The system will automatically download and use FLAN-T5 on first run.

**First-time startup:** The model download may take 1-2 minutes. Subsequent runs will be instant.

---

### Option 2: Azure OpenAI - CLOUD-BASED (Optional)

Uses Microsoft Azure's OpenAI service for potentially higher quality results.

**Advantages:**
- ✅ Higher quality responses
- ✅ Faster inference
- ✅ No local GPU needed

**Requirements:**
- Azure account with OpenAI service enabled
- API keys and endpoint

**Setup:**

1. Install the OpenAI library (already in requirements.txt):
   ```bash
   pip install openai==1.12.0
   ```

2. Create a `.env` file in the `backend` directory:
   ```env
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_TEMPERATURE=0.7
   AZURE_OPENAI_MAX_TOKENS=1000
   ```

3. The system will automatically detect and use Azure OpenAI if configured.

---

## Current Status

✅ **ImportError Fixed**: Added missing Azure OpenAI configuration variables to `config.py`

✅ **LLM Service Updated**: Now uses actual FLAN-T5 model instead of mock responses

✅ **Requirements Updated**: Added OpenAI library for Azure support

---

## How to Start the System

### On Windows:

```powershell
# Navigate to backend
cd cpsc-regulation-system\backend

# Activate virtual environment
.venv\Scripts\activate

# Start the server
python run.py
```

### First Run Notes:

1. **Model Download**: On first run, FLAN-T5 (~900MB) will be downloaded automatically
2. **Loading Time**: First startup takes 1-2 minutes, subsequent runs are much faster
3. **GPU Support**: If you have CUDA-enabled GPU, the model will automatically use it for faster inference

---

## Verify Installation

After starting the server, you should see:

```
Loading LLM model: google/flan-t5-base
✓ LLM model (FLAN-T5) loaded on cpu
```

Or if using Azure:

```
✓ Azure OpenAI initialized with deployment: your-deployment-name
```

---

## Troubleshooting

### Issue: "ImportError: cannot import name 'AZURE_OPENAI_TEMPERATURE'"
**Fixed!** Pull the latest changes from this branch.

### Issue: Model download is slow
First download can take time depending on your internet speed. The model is ~900MB.

### Issue: Out of memory
FLAN-T5-base requires ~3GB RAM. If you have less:
- Close other applications
- Or use Azure OpenAI instead (no local resources needed)

### Issue: Azure OpenAI not working
1. Verify your API key and endpoint are correct
2. Check that your deployment name matches what's in Azure
3. Ensure you have credits/quota in your Azure account
4. The system will automatically fall back to local FLAN-T5 if Azure fails

---

## Performance Comparison

| Feature | FLAN-T5 (Local) | Azure OpenAI |
|---------|----------------|--------------|
| Cost | Free | Pay per token |
| Speed | Medium (depends on CPU/GPU) | Fast |
| Quality | Good | Excellent |
| Offline | ✅ Yes | ❌ No |
| Setup | Easy | Requires Azure account |

---

## Recommendations

- **For Development/Testing**: Use FLAN-T5 (default) - it's free and works great
- **For Production/High-Volume**: Consider Azure OpenAI for better quality and speed
- **For Privacy-Sensitive Data**: Use FLAN-T5 (runs locally, data never leaves your machine)

---

## Next Steps

1. **Pull the latest code** to get the fixes
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Start the server**: `python run.py`
4. The system will automatically use FLAN-T5 and start working!

Enjoy using real AI-powered analysis! 🚀
