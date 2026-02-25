# 🔑 API Key Setup Guide

## Quick Setup

### Option 1: Interactive Setup (Recommended)

**Windows:**
```bash
# Double-click or run:
setup_api_keys.bat
```

**Command Line:**
```bash
python setup_api_keys.py
```

### Option 2: Manual Setup

Edit the `.env` file and add your credentials:

```env
WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_actual_project_id_here
WATSONX_REGION=us-south
```

### Option 3: Environment Variables

**Windows (Command Prompt):**
```cmd
set WATSONX_API_KEY=your_api_key
set WATSONX_PROJECT_ID=your_project_id
set WATSONX_REGION=us-south
python flask_backend.py
```

**Windows (PowerShell):**
```powershell
$env:WATSONX_API_KEY="your_api_key"
$env:WATSONX_PROJECT_ID="your_project_id"
$env:WATSONX_REGION="us-south"
python flask_backend.py
```

## Getting Your Credentials

### Step 1: Get IBM Cloud API Key

1. Go to: https://cloud.ibm.com/iam/apikeys
2. Log in to your IBM Cloud account
3. Click **"Create an IBM Cloud API key"**
4. Give it a name (e.g., "KrishiSahay-Watsonx")
5. Click **"Create"**
6. **Copy the API key** (you won't see it again!)
7. Save it securely

### Step 2: Get Watsonx Project ID

1. Go to: https://dataplatform.cloud.ibm.com/wx/home
2. Log in with your IBM Cloud account
3. Navigate to **"Projects"**
4. Create a new project or select existing one
5. Click on the **"Manage"** tab
6. Find **"Project ID"** in the General section
7. Copy the Project ID

### Step 3: Choose Region

Available regions:
- `us-south` (Dallas, USA) - **Default**
- `eu-gb` (London, UK)
- `eu-de` (Frankfurt, Germany)
- `jp-tok` (Tokyo, Japan)

Choose the region closest to you for better performance.

## Verification

### Check Configuration

```bash
# Run the setup script
python setup_api_keys.py

# Or check manually
python -c "from watsonx_integration import WatsonxGraniteAI; w = WatsonxGraniteAI(); print('✅ Configured' if w.is_available else '❌ Not configured')"
```

### Test API Connection

```bash
# Check Watsonx status
curl http://localhost:5000/api/watsonx/status

# Expected response:
{
  "success": true,
  "watsonx": {
    "is_available": true,
    "model": "ibm/granite-3-8b-instruct",
    "region": "us-south",
    "authenticated": true
  }
}
```

### Test AI Generation

```bash
# Test direct generation
curl -X POST http://localhost:5000/api/watsonx/generate \
  -H "Content-Type: application/json" \
  -d '{"query":"How to control aphids?"}'
```

## Troubleshooting

### Issue: "Watsonx: DISABLED"

**Cause:** API credentials not configured

**Solution:**
1. Run `python setup_api_keys.py`
2. Enter your API key and Project ID
3. Restart the server

### Issue: "Authentication failed"

**Cause:** Invalid API key or Project ID

**Solution:**
1. Verify your API key at: https://cloud.ibm.com/iam/apikeys
2. Verify your Project ID at: https://dataplatform.cloud.ibm.com/wx/home
3. Make sure the API key has Watsonx access
4. Re-run the setup script

### Issue: "Module 'requests' not found"

**Cause:** Missing Python package

**Solution:**
```bash
pip install requests
```

### Issue: "Connection timeout"

**Cause:** Network or region issues

**Solution:**
1. Check your internet connection
2. Try a different region in `.env`:
   ```env
   WATSONX_REGION=eu-de
   ```
3. Restart the server

## Security Best Practices

### ✅ DO:
- Store API keys in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables in production
- Rotate API keys periodically
- Limit API key permissions

### ❌ DON'T:
- Commit API keys to Git
- Share API keys publicly
- Use same keys for dev and production
- Store keys in code files
- Leave default/placeholder keys

## Configuration Files

### .env File Location
```
D:\AI AGRICULTURAL\.env
```

### .gitignore Entry
Make sure `.env` is in your `.gitignore`:
```
.env
*.env
.env.local
```

## After Configuration

### 1. Restart the Server

```bash
python flask_backend.py
```

You should see:
```
🤖 Watsonx: ENABLED ✅
```

### 2. Test the Chat

Open: http://localhost:5000

Ask a question like:
- "How to control aphids in mustard?"
- "Best fertilizer for wheat crop?"

### 3. Check Response Quality

With Watsonx enabled:
- **Confidence**: 92%+
- **Response Quality**: Detailed, context-aware
- **Source**: IBM Watsonx Granite LLM

Without Watsonx:
- **Confidence**: 75-80%
- **Response Quality**: Knowledge base only
- **Source**: Offline fallback

## Cost Management

### Free Tier
- IBM Cloud offers free tier for Watsonx
- Limited tokens per month
- Check usage at: https://cloud.ibm.com/billing

### Optimization
- Responses are cached for 30 minutes
- Reduces API calls by ~60-70%
- Adjust cache TTL in `watsonx_integration.py`:
  ```python
  self.cache_ttl = 1800  # 30 minutes
  ```

### Monitor Usage
```bash
# Check cache statistics
curl http://localhost:5000/api/watsonx/status

# Clear cache if needed
curl -X POST http://localhost:5000/api/watsonx/clear-cache
```

## Support

### Documentation
- Full guide: `WATSONX_SETUP_GUIDE.md`
- Backend docs: `BACKEND_README.md`
- Quick start: `QUICK_START.md`

### IBM Resources
- Watsonx Docs: https://www.ibm.com/docs/en/watsonx-as-a-service
- IBM Cloud Support: https://cloud.ibm.com/unifiedsupport/supportcenter
- API Reference: https://cloud.ibm.com/apidocs/watsonx-ai

### Check Logs
```bash
# View server logs
type logs\backend.log

# Check for errors
findstr "ERROR" logs\backend.log
```

---

**Ready to enable IBM Watsonx! Run the setup script now! 🚀**