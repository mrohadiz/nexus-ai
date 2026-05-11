# Nexus AI: Cognitive Auto Routing & Intent Detection System

## 1. Root Problem Analysis
Currently, Nexus AI suffers from a **"One-Size-Fits-All Cognitive Trap"**. It defaults to a heavy, consultant-style reasoning mode regardless of the input's complexity. 
* **Premature Solutioning:** It jumps to solutions for complex strategic issues without sufficient diagnosis.
* **Over-engineering Simple Queries:** It applies heavy frameworks (like TGM or deep bottlenecks) to straightforward factual questions.
* **Context Blindness:** It fails to distinguish between tactical execution (needs steps), strategic ambiguity (needs facilitation), and educational requests (needs simplification).
* **Forced Frameworks:** Grill-Me is treated as a blanket feature rather than a targeted diagnostic escalation.

## 2. Intent Detection Architecture
Instead of a simple NLP classifier, Nexus needs a **Multi-Dimensional Intent Analyzer**. When a user sends a prompt, the system evaluates it across 5 cognitive vectors:

1. **Domain:** Factual, Product, Strategic Marketing, Organizational Capability, Governance, Operations, System Architecture, Code.
2. **Abstraction Level:** High (Vision/Strategy) vs. Low (Tactical/Execution).
3. **Reasoning Complexity:** Single-step logic vs. Multi-variable systemic interaction.
4. **Ambiguity Level:** Clarity of the desired outcome and the current state (Score 0-10).
5. **Impact / Stakes:** High (Reorg, Business Model) vs. Low (Definition, Simple Task).

## 3. Cognitive Routing Design
The **Cognitive Router** acts as a switchboard. Based on the Intent Vectors, it routes the prompt to specific **Reasoning Modes**.

* **Direct Factual Mode:** (Low Ambiguity, Low Complexity, Factual Domain) -> Bypass deep reasoning, provide immediate, accurate answers.
* **Educational / Simplification Mode:** (User wants to understand a concept) -> Focus on analogies, clear language, no heavy consulting jargon.
* **Diagnosis-First Mode:** (High Ambiguity, Operational/Marketing Domain) -> Focus on identifying bottlenecks before suggesting solutions.
* **Strategic Facilitation Mode:** (High Abstraction, High Stakes) -> Focus on mapping options, trade-offs, and organizational alignment.
* **Systems Thinking Mode:** (Architecture, Operations) -> Focus on upstream/downstream impact, observability, and flow.

## 4. Reasoning Policy Engine
Once a mode is selected, the Policy Engine dictates *how* the AI should behave:
* **Restraint Level:** How hard the AI should try *not* to give a final answer.
* **Observability Focus:** What metrics or variables the AI must ask the user to clarify.
* **Output Structure:** Direct answer, step-by-step, diagnostic question, or framework mapping.

## 5. Auto Grill-Me Activation Logic
Grill-Me is repositioned as a **Diagnostic Escalation Protocol**. It activates *automatically* if:
`Ambiguity Score > 6` AND `Strategic/Operational Impact == High` AND `Diagnosis Confidence < Target Confidence`.

**Trigger Conditions:**
* The user states a symptom ("Leads high, closing low") without a clear root cause.
* The prompt contains contradictory goals ("Fast growth but zero budget increase").
* High reliance on "hidden assumptions" (e.g., assuming a specific channel works without data).
* **Bypass:** Automatically skipped for factual questions or explicitly detailed execution commands.

## 6. State Machine Proposal
Nexus will operate on a dynamic state machine per conversation thread:

1. **STATE_INGEST:** Receive user input.
2. **STATE_ANALYZE_INTENT:** Calculate the 5 cognitive vectors.
3. **STATE_ROUTE:** Assign Reasoning Mode.
4. **STATE_EVALUATE_AMBIGUITY:** 
   * If Ambiguity > Threshold -> **STATE_GRILL_ME** (Ask clarifying, diagnostic questions).
   * If Ambiguity < Threshold -> **STATE_FORMULATE_RESPONSE**.
5. **STATE_GRILL_ME:** Generate 1-2 sharp, targeted questions to reduce ambiguity. Wait for user response -> Return to Ingest.
6. **STATE_RESTRAINT_CHECK:** Before delivering a solution, verify: "Do I have enough context to solve this safely?"
7. **STATE_DELIVER:** Format and send the response based on the Communication Calibration.

## 7. Ambiguity Scoring Design
A background LLM call (or heuristic rule engine) scores Ambiguity (0.0 to 1.0) based on:
* **Missing Variables:** Are metrics mentioned without baselines?
* **Vague Terminology:** Use of words like "better," "faster," "optimize" without definitions.
* **Missing Constraints:** Lack of budget, timeline, or resource context.
* **Symptom vs. Cause:** Is the user describing a pain point or a verified system failure?

## 8. Diagnosis Confidence Design
Confidence (0% - 100%) measures how well Nexus understands the problem's root cause.
* **0-30%:** Symptom only. (Requires Grill-Me).
* **31-70%:** Bottleneck identified, but constraints/governance impact unclear. (Requires targeted clarification).
* **71-100%:** Clear causal chain (Symptom -> Bottleneck -> Root Cause -> Constraints). (Cleared for Solution Formulation).

## 9. Communication Calibration System
Nexus adapts its tone and depth based on the detected user persona and context:
* **CEO/GM:** High-level trade-offs, governance impact, resource allocation. Bottom-line up front.
* **PM/Marketing Manager:** Process flow, bottleneck analysis, metric tracking.
* **Executor:** Step-by-step tactical guidance.
* **Confusion Detection:** If user replies with "I don't understand" or "Too complex", Nexus triggers **Simplification Mode** -> drops frameworks, uses analogies, reduces vocabulary complexity.

## 10. Suggested Module/Class Structure (Python)

```python
core/
├── intent/
│   ├── intent_detector.py      # Outputs IntentProfile (Domain, Ambiguity, etc.)
│   ├── ambiguity_scorer.py     # Calculates 0-1 score
│   └── persona_detector.py     # Calibrates communication style
├── routing/
│   ├── cognitive_router.py     # Maps IntentProfile to ReasoningMode
│   └── modes/                  # Base class for different reasoning strategies
│       ├── factual_mode.py
│       ├── diagnosis_mode.py
│       ├── strategic_mode.py
│       └── execution_mode.py
├── policies/
│   ├── restraint_engine.py     # Enforces solution restraint based on Confidence
│   └── grill_me_trigger.py     # Logic for escalating to diagnostic questions
└── orchestration/
    ├── state_machine.py        # Manages conversation state transitions
    └── response_formatter.py   # Applies Communication Calibration
```

## 11. Incremental Implementation Roadmap
* **Phase 1: Observability & Intent (Weeks 1-2):** Implement the `IntentDetector`. Log intents in the background without changing responses. Validate if Nexus correctly identifies Factual vs Strategic.
* **Phase 2: The Switchboard (Weeks 3-4):** Implement `CognitiveRouter` and basic `ReasoningModes` (Factual vs. Consultant). Bypass heavy prompts for simple questions.
* **Phase 3: Auto Grill-Me & Restraint (Weeks 5-6):** Implement `AmbiguityScorer` and `GrillMeTrigger`. Nexus begins asking questions autonomously when ambiguity is high.
* **Phase 4: Communication Calibration (Weeks 7-8):** Implement persona-based formatting and confusion fallback loops.

## 12. Example Conversations (Before vs After)

**Case 1: "Kenapa telinga anak saya batuk saat dibersihkan?"**
* **Before:** *Enters consultant mode.* "Mari kita analisis bottleneck dari telinga anak Anda. Pertama, kita perlu melihat governance dari pembersihan telinga..."
* **After (Factual Mode):** "Ini terjadi karena refleks Arnold (Arnold's nerve reflex). Saraf vagus di telinga terstimulasi saat dibersihkan, yang mengirimkan sinyal ke tenggorokan dan memicu batuk. Ini normal dan tidak berbahaya. Tidak perlu terapi khusus, cukup bersihkan pelan-pelan." *(No Grill-Me)*

**Case 2: "Leads banyak tapi closing rendah"**
* **Before:** "Berikut adalah 10 strategi untuk meningkatkan closing rate Anda: 1. Retargeting, 2. Script sales..." *(Premature Solutioning)*
* **After (Diagnosis Mode + Auto Grill-Me):** "Ini adalah klasik *activation bottleneck*. Sebelum saya memberi solusi, saya perlu memastikan letak kebocorannya. 
1. Berapa % leads yang *valid* (bisa dihubungi) vs *invalid*? 
2. Apakah leads drop di tahap follow-up pertama, atau setelah tahu harga?
Mari kita isolasi masalahnya dulu."

**Case 3: "Saya ingin mengubah tacit knowledge CEO menjadi explicit"**
* **Before:** "Mari kita gunakan framework Total Growth Marketing untuk knowledge..." *(Wrong domain)*
* **After (Organizational Capability Mode):** "Ini adalah tantangan *Organizational Governance*. Mentransfer knowledge CEO bukan soal dokumentasi, tapi soal memindahkan *decision-making intuition*. Pendekatan yang tepat adalah membangun *Observability* atas keputusan CEO. Apakah Anda ingin mulai dari area Operasional, atau Strategi Produk?"

## 13. Risks & Trade-offs
* **Latency:** Adding Intent Detection and Ambiguity Scoring via LLM calls will add latency. *Mitigation: Use faster, smaller models (e.g., Claude 3 Haiku / GPT-4o-mini) strictly for the routing and scoring layers.*
* **Over-Questioning (Infinite Grill-Me):** The AI might get stuck asking questions if the user cannot provide clear answers. *Mitigation: Cap Auto Grill-Me to maximum 2 consecutive turns. If ambiguity remains high, force a "Best Guess Scenarios" response.*
* **Prompt Complexity:** Managing multiple system prompts for different Reasoning Modes can become unruly. *Mitigation: Strict modularization of prompts, loaded dynamically based on the router's output.*
