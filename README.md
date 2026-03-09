# simple-ai-provider-proxy
Easy CORS Proxy for xAI API (and others)

**Problem**: Your browser blocks direct calls to AI APIs (CORS error).  
**Solution**: This tiny Python proxy runs on your computer and fixes it!

**Works with**: xAI Grok, OpenAI, Claude, Groq, and more.

## 🎯 Why You Need This (xAI Specific)

**~March 4, 2026**: xAI changed their API server config and started blocking browser requests.

```
❌ Direct browser calls fail with this exact error:
fetch('https://api.x.ai/v1/chat/completions') 
Response: 405 Method Not Allowed
Request: OPTIONS https://api.x.ai/v1/chat/completions (CORS preflight blocked)

✅ Server tools (curl, Node.js) still work fine
✅ This proxy fixes browser access
```

xAI hasn't announced this change or provided browser-friendly CORS headers.

## 📋 3-Step Setup (2 minutes)

### 1. Save the Code
Copy `proxy.py` to a folder on your computer.

### 2. Run the Proxy
Open terminal/command prompt in that folder:
```bash
python proxy.py
```
```
Proxy running at http://localhost:8000 ✅
(Leave this terminal open)
```

### 3. Use in Your Code
Replace your API calls:
```javascript
// OLD (broken since March 4, 2026)
fetch('https://api.x.ai/v1/chat/completions', {
  headers: { 'Authorization': 'Bearer YOUR_KEY' }
})

// NEW (works!)
fetch('http://localhost:8000/proxy?url=https://api.x.ai/v1/chat/completions', {
  headers: { 'Authorization': 'Bearer YOUR_KEY' }
})
```

## ✨ Copy-Paste Examples

> **⚠️ IMPORTANT**: Replace `YOUR_XAI_API_KEY` with your real key from [console.x.ai](https://console.x.ai). Use current model name from xAI docs (like `grok-2-1212` - `grok-beta` is outdated!)

### Chat with Grok (Browser JavaScript)
```javascript
async function askGrok(question) {
  const response = await fetch('http://localhost:8000/proxy?url=https://api.x.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_XAI_API_KEY_HERE',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'grok-2-1212',  // Use current model from xAI docs
      messages: [{ role: 'user', content: question }]
    })
  });
  
  const data = await response.json();
  console.log(data.choices[0].message.content);
}
```

### Test with curl
```bash
curl "http://localhost:8000/proxy?url=https://api.x.ai/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-1212",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 🔗 All Supported APIs

| AI Service | Use This URL |
|------------|-------------|
| **xAI Grok** | `?url=https://api.x.ai/v1/chat/completions` |
| **OpenAI** | `?url=https://api.openai.com/v1/chat/completions` |
| **Claude** | `?url=https://api.anthropic.com/v1/messages` |
| **Groq** | `?url=https://api.groq.com/openai/v1/chat/completions` |

## ⚠️ Important Limitations

| ❌ Doesn't Work | Why |
|----------------|-----|
| Streaming (`"stream": true`) | Single response only |
| Production deployment | Local dev tool only |
| File uploads | JSON requests only |

**Quick local fix - not for production!**

## ❓ Common Questions

**Q: "Domain not allowed"?**  
A: Edit `proxy.py` → add domain to `ALLOWED_DOMAINS`

**Q: "Invalid model"?**  
A: Check [console.x.ai](https://console.x.ai) for current models

**Q: Proxy not responding?**  
A: Visit `http://localhost:8000` in browser or `curl http://localhost:8000`

## 🛡️ Safe for Local Use
- HTTPS-only targets
- Domain whitelist
- Runs only on YOUR machine

---

## 🔧 Advanced: Background Mode + Logs (Optional)

**Logs saved to**: `proxy.log` (same folder)

### macOS/Linux
```bash
# Start in background
nohup python proxy.py > proxy.log 2>&1 &

# View live logs
tail -f proxy.log

# Stop (safest - kills via PID file)
pkill -f proxy.py
```

### Windows
```cmd
REM Start in background
start /B python proxy.py > proxy.log 2>&1

REM View logs
type proxy.log

REM Stop (Task Manager → python.exe OR)
taskkill /IM python.exe /F
```

**Pro tip**: Always use `pkill -f proxy.py` (Mac/Linux) or Task Manager to stop cleanly.

**Quick workaround for xAI's March 4, 2026 CORS change. Simple local fix! 🚀**
