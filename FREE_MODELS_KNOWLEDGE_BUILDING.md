# Free Models Setup for Central Knowledge Building

## Overview

Nexus AI sudah di-configure dengan **automatic fallback chain** ke free models via OpenRouter. Ini perfect untuk building central knowledge base tentang pola pikir Anda tanpa biaya.

---

## Current Configuration

### Free Models Available (Auto-Fetched)

Sistem otomatis fetch free models dari OpenRouter API setiap 10 menit:

```python
# Default fallback chain (jika API fetch gagal):
[
    "google/gemini-2.0-flash-001",          # Fast, good for chat
    "google/gemma-3-27b-it:free",           # Good reasoning
    "meta-llama/llama-3.1-8b-instruct:free", # Balanced
    "mistralai/mistral-7b-instruct:free",   # Lightweight
    "qwen/qwen-2.5-7b-instruct:free"        # Multilingual support
]
```

### How It Works

1. **Primary Model**: User selects model di UI (default: `google/gemma-3-27b-it:free`)
2. **Auto-Fallback**: Jika primary model error/rate limit → automatic switch ke next free model
3. **Transparent**: Frontend shows notification saat model switching
4. **No Cost**: Semua models di fallback chain adalah FREE (prompt_price = 0)

---

## Recommended Setup for Knowledge Building

### Best Free Models untuk Pattern Recognition

Untuk membangun central knowledge tentang pola pikir Anda, recommend models ini:

#### 1. **Google Gemma 3 27B IT:free** ⭐ RECOMMENDED
```
Model ID: google/gemma-3-27b-it:free
Context: 8192 tokens
Best for: Deep conversations, pattern recognition, strategic thinking
Why: Large parameter count (27B) = better understanding of nuance
```

**Use Case:**
- Strategic discussions (Grill-Me mode)
- Complex problem solving
- Pattern analysis dari conversation history

#### 2. **Qwen 2.5 7B Instruct:free**
```
Model ID: qwen/qwen-2.5-7b-instruct:free
Context: 32768 tokens (LARGE!)
Best for: Long context retention, Bahasa Indonesia
Why: Excellent multilingual support, huge context window
```

**Use Case:**
- Long-form reflection journals
- Detailed business planning
- Multi-turn deep dives

#### 3. **Meta Llama 3.1 8B Instruct:free**
```
Model ID: meta-llama/llama-3.1-8b-instruct:free
Context: 128000 tokens (MASSIVE!)
Best for: Very long conversations, knowledge accumulation
Why: Largest context window = remembers more from session
```

**Use Case:**
- Extended brainstorming sessions
- Knowledge synthesis dari multiple topics
- Long-term pattern tracking dalam satu session

---

## Strategy for Building Central Knowledge

### Phase 1: Data Collection (Weeks 1-4)

**Goal:** Kumpulkan rich conversation data tentang:
- Decision-making patterns
- Strategic priorities
- Problem-solving approaches
- Values & principles
- Business philosophy

**Recommended Approach:**
```
1. Use Grill-Me mode untuk structured self-reflection
   - Discuss business challenges
   - Explore strategic dilemmas
   - Clarify values and priorities

2. Daily journaling via regular chat
   - Share thoughts on market trends
   - Reflect on decisions made
   - Document learnings

3. Weekly strategic reviews
   - Analyze what worked/didn't work
   - Identify emerging patterns
   - Refine mental models
```

**Model Selection:**
- Primary: `google/gemma-3-27b-it:free` (best reasoning)
- Fallback: Auto (system handles it)

### Phase 2: Pattern Extraction (Weeks 5-8)

**Goal:** Extract recurring patterns dari conversation history

**Techniques:**
```python
# Example: Ask AI to analyze your patterns
"Based on our last 20 conversations, what are my recurring 
decision-making patterns? What biases do I show?"

"Identify my core strategic principles from our discussions 
about business growth."

"What mental models do I consistently apply when solving problems?"
```

**Tools to Use:**
- Regular chat with long context (Llama 3.1 for 128k context)
- Export conversation history untuk analysis
- Use `/research` endpoint untuk deep pattern analysis

### Phase 3: Knowledge Synthesis (Weeks 9-12)

**Goal:** Build structured knowledge base dari extracted patterns

**Output Formats:**
```markdown
# My Strategic Framework

## Core Principles
1. [Principle 1] - derived from conversations on [date range]
2. [Principle 2] - reinforced in [specific discussion]

## Decision-Making Patterns
- When facing [situation A], I tend to [pattern X]
- Under pressure, I prioritize [value Y]

## Mental Models I Use
- [Model 1]: Applied in [context]
- [Model 2]: Preferred for [type of problem]

## Blind Spots Identified
- Tendency to [bias Z] - observed in [examples]
- Need to improve [skill W] - mentioned in [discussions]
```

---

## Technical Implementation

### 1. Enable Session Persistence

Pastikan conversation history tersimpan untuk pattern analysis:

```typescript
// Frontend already does this in ChatInterface.tsx
const saveCurrentSession = (messages: Message[]) => {
  localStorage.setItem(`chat_session_${sessionId}`, JSON.stringify(messages));
};
```

### 2. Export Conversation History

Create endpoint untuk export all conversations:

```python
# Add to backend/main.py
@app.get("/conversations/export")
def export_conversations():
    """Export all conversation history for pattern analysis."""
    # Query database for all sessions
    # Return as JSON or Markdown
    pass
```

### 3. Pattern Analysis Prompt Template

```python
PATTERN_ANALYSIS_PROMPT = """
Analyze the following conversation history and identify:

1. DECISION PATTERNS
   - How does user approach complex decisions?
   - What factors do they prioritize?
   - What's their risk tolerance?

2. STRATEGIC PRINCIPLES
   - What core beliefs guide their strategy?
   - What trade-offs do they consistently make?
   - What outcomes do they value most?

3. PROBLEM-SOLving STYLE
   - Analytical vs intuitive?
   - Big picture vs detail-oriented?
   - Quick action vs thorough analysis?

4. RECURRING THEMES
   - Topics that come up repeatedly
   - Concerns that persist across time
   - Goals that evolve but stay related

5. BLIND SPOTS & BIASES
   - Areas where judgment might be skewed
   - Assumptions that go unchallenged
   - Perspectives that are missing

Format output as structured markdown with specific examples from conversations.
"""
```

### 4. Automated Weekly Summary

Setup cron job untuk generate weekly insights:

```python
# Pseudo-code
def weekly_knowledge_summary():
    # Get all conversations from past week
    conversations = get_conversations(date_range="last_7_days")
    
    # Analyze patterns
    insights = ai_service.call_ai(
        prompt=PATTERN_ANALYSIS_PROMPT,
        context=conversations,
        model="google/gemma-3-27b-it:free"
    )
    
    # Save to knowledge base
    save_insights(insights, date=today())
    
    # Send summary to user
    notify_user(insights)
```

---

## Cost Optimization

### Free Tier Limits (OpenRouter)

OpenRouter free models have:
- ✅ **No monetary cost** (prompt_price = 0)
- ⚠️ **Rate limits** (varies by model, typically 10-50 req/min)
- ⚠️ **Queue times** during peak hours (may wait 5-30 seconds)

### Strategies to Maximize Free Usage

1. **Batch Conversations**
   - Group related thoughts into single long message
   - Reduces number of API calls
   - Better context for pattern recognition

2. **Use Efficient Models**
   - Gemma 27B for deep thinking (slower but better quality)
   - Qwen 7B for quick reflections (faster, good enough)
   - Llama 8B for long context needs

3. **Cache Insights**
   - Save pattern analysis results
   - Don't re-analyze same conversations
   - Build on previous insights

4. **Off-Peak Usage**
   - Use during non-peak hours (lower queue times)
   - Schedule batch analysis at night

---

## Integration with Mira Context

Nexus AI sudah punya **Mira Context** untuk centralized learning:

```python
# backend/logic/memory_manager.py
memory_manager.store_context(
    key="user_decision_patterns",
    value={...},
    tags=["strategic_thinking", "patterns"]
)
```

**Enhancement Idea:**
Store extracted patterns into Mira Context untuk:
- Cross-session learning
- Progressive refinement
- Context-aware responses

```python
# Example: Store weekly insights
memory_manager.store_context(
    key=f"weekly_insights_{week_number}",
    value=insights,
    tags=["patterns", "reflection", week_number]
)

# Later: Retrieve for context-aware responses
past_patterns = memory_manager.retrieve_relevant("decision_patterns")
```

---

## Monitoring & Analytics

### Track These Metrics

1. **Conversation Volume**
   - Messages per day/week
   - Average conversation length
   - Topics covered

2. **Pattern Quality**
   - Insightfulness of extracted patterns
   - Actionability of recommendations
   - Accuracy of predictions

3. **Model Performance**
   - Which free models work best for you
   - Response quality by model
   - Error rates / fallback frequency

### Simple Dashboard

Create simple analytics page:

```typescript
// frontend/src/app/analytics/page.tsx
export default function AnalyticsPage() {
  const [stats, setStats] = useState({
    totalConversations: 0,
    totalMessages: 0,
    topTopics: [],
    patternInsights: []
  });
  
  // Fetch and display stats
}
```

---

## Next Steps

### Immediate (This Week)
1. ✅ Start using Grill-Me mode untuk structured reflection
2. ✅ Experiment dengan different free models
3. ✅ Begin daily journaling via chat
4. ✅ Monitor which models work best for your style

### Short-term (Month 1)
1. 📋 Setup conversation export functionality
2. 📋 Create pattern analysis prompts
3. 📋 Build simple analytics dashboard
4. 📋 Integrate with Mira Context for storage

### Medium-term (Months 2-3)
1. 🚀 Implement automated weekly summaries
2. 🚀 Build knowledge base UI
3. 🚀 Add pattern visualization
4. 🚀 Enable cross-session learning

### Long-term (Months 4-6)
1. 🎯 Develop personal AI twin (trained on your patterns)
2. 🎯 Predictive decision support
3. 🎯 Bias detection & correction
4. 🎯 Strategic opportunity identification

---

## Troubleshooting

### Issue: Rate Limiting

**Symptom:** "Rate limit exceeded" errors

**Solution:**
```python
# System already handles this via fallback chain
# If one model hits rate limit, auto-switches to next

# Manual override: Change primary model in UI
Select: "google/gemma-3-27b-it:free" → "qwen/qwen-2.5-7b-instruct:free"
```

### Issue: Slow Response Times

**Symptom:** Waiting 30+ seconds for response

**Solution:**
1. Try different model (some are faster than others)
2. Use during off-peak hours
3. Shorten messages (less tokens = faster processing)
4. Check OpenRouter status page for outages

### Issue: Poor Response Quality

**Symptom:** AI doesn't understand nuance or gives generic answers

**Solution:**
1. Switch to larger model (Gemma 27B > Llama 8B > Mistral 7B)
2. Provide more context in your message
3. Use system prompt customization
4. Try rephrasing question

---

## Resources

### OpenRouter Free Models List
- URL: https://openrouter.ai/models?max_price=0
- Updated regularly with new free models

### Model Comparison
- LMSYS Chatbot Arena: https://chat.lmsys.org/
- Compare model quality side-by-side

### OpenRouter Documentation
- API Docs: https://openrouter.ai/docs
- Pricing: https://openrouter.ai/pricing

---

## Conclusion

Dengan setup ini, Anda bisa build **central knowledge base** tentang pola pikir Anda **tanpa biaya** menggunakan free models dari OpenRouter.

**Key Success Factors:**
1. ✅ Consistency - Regular conversations (daily/weekly)
2. ✅ Depth - Use Grill-Me mode untuk structured reflection
3. ✅ Analysis - Extract patterns periodically
4. ✅ Synthesis - Build structured knowledge base
5. ✅ Application - Use insights untuk better decisions

**Expected Timeline:**
- Month 1: Data collection foundation
- Month 2: Pattern emergence
- Month 3: Actionable insights
- Month 6+: Personal AI twin capabilities

Start today, and in 6 months you'll have a rich, structured understanding of your own thinking patterns! 🚀
