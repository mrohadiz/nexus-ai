# Nexus-AI Domain Setup - chat.mrohadiz.my.id

## 🌐 Domain Configuration

**Public URL:** https://chat.mrohadiz.my.id/  
**Backend API:** http://localhost:8000  
**Frontend Port:** 5008  
**SSL:** Enabled (via Cloudflare)  

---

## ✅ Current Status

### Services Running:
- ✅ **Frontend**: Serving on port 5008 → tunneled to chat.mrohadiz.my.id
- ✅ **Backend**: API on port 8000 (healthy)
- ✅ **DuckAI Proxy**: On port 3000 (required for AI processing)
- ✅ **PostgreSQL**: Database active

### Features Available:
- ✅ Basic chat interface
- ✅ Message history
- ✅ Model selection (GPT-4o-mini, Claude Haiku 4.5, etc.)
- ✅ Streaming responses
- ⏳ **Tool calling UI** (rebuilding with new components)

---

## 🚀 Access Points

### Public Access:
```
https://chat.mrohadiz.my.id/
```

### Local Access:
```
Frontend: http://localhost:5008
Backend:  http://localhost:8000
DuckAI:   http://localhost:3000
```

---

## 🔧 Management Commands

### Using nexus.sh Script:
```bash
cd /root/nexus-ai

# Check status
bash nexus.sh status

# Restart all services
bash nexus.sh restart

# View logs
bash nexus.sh logs

# Stop services
bash nexus.sh stop

# Start services
bash nexus.sh start
```

### Manual Service Control:
```bash
# Backend only
cd /root/nexus-ai/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend only
cd /root/nexus-ai/frontend
npm run dev  # Development mode
npm run start # Production mode
```

---

## 📊 Monitoring

### Check Backend Health:
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "0.1.0"}
```

### Check Frontend:
```bash
curl https://chat.mrohadiz.my.id/ | grep "Nexus AI"
```

### View Logs:
```bash
# Backend logs
tail -f /root/nexus-ai/backend.log

# Frontend logs (PM2)
pm2 logs nexus-frontend

# All logs via nexus.sh
bash nexus.sh logs
```

---

## 🎨 Upcoming Features (After Rebuild)

Once the frontend rebuild completes, you'll get:

### Tool Calling Visualization:
- 🟡 Real-time tool execution status
- 🟢 Expandable cards showing arguments/results
- 🔵 Tool-specific icons (web_search, research_topic, etc.)
- ⚫ Dark theme optimized UI

### New Endpoints:
- `/chat/tools` - Chat with tool calling support
- `/research/autonomous` - Autonomous research workflows
- `/planning/task` - Task planning and decomposition

---

## 🔒 Security Notes

### Current Setup:
- ✅ HTTPS enabled via Cloudflare
- ✅ Cloudflare protection active (rocket-loader detected)
- ⚠️ No authentication on backend API yet

### Recommendations:
1. **Add API authentication** for production use
2. **Rate limiting** to prevent abuse
3. **CORS configuration** if needed
4. **Environment variables** for sensitive data

---

## 🐛 Troubleshooting

### Issue: Domain not loading
```bash
# Check if services are running
bash nexus.sh status

# Check port 5008 is accessible
lsof -i :5008

# Verify tunnel is active
# (Check your tunneling service - ngrok/cloudflared/etc)
```

### Issue: Backend API errors
```bash
# Check backend health
curl http://localhost:8000/health

# View backend logs
tail -f /root/nexus-ai/backend.log

# Restart backend
cd /root/nexus-ai && bash nexus.sh restart
```

### Issue: Tool calling not working
```bash
# Ensure DuckAI is running
curl http://localhost:3000/health

# Check backend supports tools
curl -X POST http://localhost:8000/chat/tools \
  -H "Content-Type: application/json" \
  -d '{"message":"test","session_id":"test"}'
```

### Issue: Port already in use
```bash
# Find process using port
lsof -i :8000 -P -n

# Kill it
kill -9 <PID>

# Restart services
bash nexus.sh restart
```

---

## 📈 Performance Tips

### For Better Response Times:
1. **Use production build** (not dev mode)
2. **Enable caching** for static assets
3. **Optimize database queries**
4. **Monitor rate limits** on DuckAI (20 req/min)

### Current Build Mode:
- Frontend: Production (`npm run start`)
- Backend: Production (uvicorn via PM2)

---

## 🔄 Update Workflow

When making changes to the codebase:

```bash
# 1. Make your changes
# Edit files in /root/nexus-ai/frontend/src or /root/nexus-ai/backend

# 2. Rebuild frontend (if UI changes)
cd /root/nexus-ai/frontend
npm run build

# 3. Restart services
cd /root/nexus-ai
bash nexus.sh restart

# 4. Verify
curl https://chat.mrohadiz.my.id/
```

---

## 📝 Environment Variables

### Backend (.env):
```bash
DUCKAI_URL=http://localhost:3000/v1/chat/completions
DUCKAI_API_KEY=dummy-key
```

### Frontend:
No environment variables needed (uses relative API paths)

---

## 🎯 Testing Your Domain

### Test Basic Chat:
1. Open https://chat.mrohadiz.my.id/
2. Type a message: "Hello, how are you?"
3. Verify you get a response

### Test Tool Calling (after rebuild):
1. Ask: "What are the latest AI developments?"
2. Look for tool call cards appearing
3. Verify web_search tool executes

### Test API Directly:
```bash
curl -X POST https://chat.mrohadiz.my.id/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"test","history":[],"model":"gpt-4o-mini"}'
```

---

## 📞 Support

If you encounter issues:

1. **Check logs**: `bash nexus.sh logs`
2. **Verify services**: `bash nexus.sh status`
3. **Test endpoints**: Use curl commands above
4. **Review documentation**: 
   - `/root/TOOL_CALLING_IMPLEMENTATION.md`
   - `/root/nexus-ai/frontend/TOOL_CALLING_UI.md`
   - `/root/nexus-ai/frontend/README_TOOL_CALLING.md`

---

## 🚀 Quick Reference

| Component | URL/Port | Status |
|-----------|----------|--------|
| **Public Site** | https://chat.mrohadiz.my.id/ | ✅ Active |
| **Frontend** | localhost:5008 | ✅ Running |
| **Backend API** | localhost:8000 | ✅ Healthy |
| **DuckAI Proxy** | localhost:3000 | ✅ Running |
| **Database** | PostgreSQL | ✅ Active |

---

**Your Nexus-AI is now accessible worldwide at https://chat.mrohadiz.my.id/!** 🎉
