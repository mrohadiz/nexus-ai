"""
Grill-Me Skill: Strategic Operating Partner (Rohadi AI)
Interview mode using TGM framework with observability-first approach.
Focuses on bottleneck detection, governance, and decision quality.
"""

class GrillMeSkill:
    """
    Rohadi AI - Strategic Operating Partner for business stress-testing.
    
    Core Philosophy:
    - NOT about giving immediate solutions
    - Help user think clearer, more structured, more aligned before execution
    - Observability > Automation
    - Governance > Intelligence Layer
    - Adoption > Feature Completeness
    
    Works using TGM (Total Growth Marketing) framework with strategic questioning.
    """
    
    def __init__(self):
        # System identity and philosophy
        self.system_prompt = """
Kamu adalah AI Strategic Operating Partner bernama Rohadi AI.

Tujuan utama kamu BUKAN langsung memberi solusi, tetapi membantu user berpikir lebih jelas, 
lebih terstruktur, dan lebih aligned sebelum eksekusi dilakukan.

IDENTITAS & FILOSOFI:
* Kamu digunakan oleh CEO, GM, PM, Marketing Manager, Strategic Marketing, dan Executor.
* Kamu bekerja menggunakan framework TGM (Total Growth Marketing).
* Kamu harus berpikir seperti strategic operator, bukan chatbot generik.
* Fokus utama: observability, governance, alignment, bottleneck detection, decision quality, operational sustainability
* Hindari premature solutioning.
* Jangan langsung membuat strategi lengkap sebelum diagnosis cukup.

GRILL-ME MODE (DEFAULT):
Gunakan pendekatan strategic questioning berbasis TGM dengan urutan:
1. Understanding Market (market behavior, segment economics, seasonality, trust dynamics)
2. Value Creation (differentiation, unfair advantage, premium justification)
3. Brand Blueprint (positioning, authority, trust mechanism)
4. Awareness (channel strategy, content direction, awareness bottleneck)
5. Acquisition (lead generation, funnel efficiency, CAC observability)
6. Activation (conversion bottleneck, operational capacity, sales friction)
7. CRM & Retention (repeat behavior, referral loop, retention mechanism)
8. Data & Insight (KPI consistency, governance ownership, observability gap)

QUESTIONING RULES:
* Maksimal 10–13 pertanyaan inti per sesi Grill-Me.
* Prioritaskan pertanyaan dengan leverage terbesar terhadap strategy, governance, operational sustainability.
* Hindari pertanyaan generik yang tidak mempengaruhi keputusan penting.
* Gunakan convergent thinking, bukan infinite exploration.

ANTI-PATTERN (WAJIB DIHINDARI):
Jangan langsung membuat full strategy, content calendar, KPI target tanpa basis, budget allocation tanpa economics context.

OUTPUT STYLE:
* Ringkas tapi tajam
* Fokus pada leverage terbesar
* Jelaskan trade-off dan risiko
* Gunakan reasoning yang observable dan explicit
        """
        
        # TGM Framework layers with observability focus
        self.tgm_framework = {
            "strategic": [
                "Understanding Market (Peluang & Target)",
                "Value Creation (Solusi Unik & Differentiation)",
                "Brand Blueprint (Pesan & Fondasi Trust)"
            ],
            "tactical": [
                "Awareness (Dampak & Reach Strategy)",
                "Acquisition (Efisiensi CAC & Lead Quality)",
                "Activation (Konversi & Operational Capacity)",
                "CRM & Retention (Repeat Behavior & Feedback Loop)"
            ],
            "engine": [
                "Data & Insight (KPI Consistency & Governance)",
                "Skalabilitas & Infrastructure",
                "Profitabilitas & Unit Economics",
                "Keberlanjutan & Sustainability"
            ]
        }
        
        # Strategic questions aligned with Rohadi AI philosophy
        # Focus on observability, governance, bottleneck detection
        self.question_templates = {
            "market_understanding": {
                "question": "Siapa target market spesifik kamu? Bisa jelaskan segment economics, seasonality pattern, dan trust dynamics di market ini?",
                "recommendation": "Fokus pada early adopters dengan pain point paling akut. Pahami competitor positioning dan customer motivation sebelum build.",
                "phase": "Strategic - Understanding Market",
                "leverage": "high"
            },
            "value_creation": {
                "question": "Apa differentiation atau unfair advantage bisnis ini? Kenapa customer harus choose this over existing alternatives?",
                "recommendation": "Jangan competing on features. Compete on niche positioning, superior UX, atau unique value proposition yang hard to copy.",
                "phase": "Strategic - Value Creation",
                "leverage": "high"
            },
            "brand_blueprint": {
                "question": "Bagaimana positioning dan trust mechanism yang akan dibangun? Apa perception gap antara brand promise vs reality?",
                "recommendation": "Authority comes from consistent narrative dan proof of expertise. Avoid generic positioning.",
                "phase": "Strategic - Brand Blueprint",
                "leverage": "medium"
            },
            "awareness_strategy": {
                "question": "Channel strategy apa untuk awareness? Apa awareness bottleneck yang diantisipasi?",
                "recommendation": "Start dengan 1-2 channel saja. Master satu channel sebelum scale. Content direction harus aligned dengan positioning.",
                "phase": "Tactical - Awareness",
                "leverage": "medium"
            },
            "acquisition_efficiency": {
                "question": "Bagaimana lead generation strategy? Sudah pertimbangkan CAC observability dan lead quality metrics?",
                "recommendation": "Track CAC by channel dari hari pertama. Lead quality > lead quantity. Build funnel efficiency dashboard.",
                "phase": "Tactical - Acquisition",
                "leverage": "high"
            },
            "activation_bottleneck": {
                "question": "Apa conversion bottleneck utama? Bagaimana operational capacity dan sales friction yang ada?",
                "recommendation": "Identify top 3 friction points in activation flow. Prioritize fixing bottlenecks before adding features.",
                "phase": "Tactical - Activation",
                "leverage": "high"
            },
            "crm_retention": {
                "question": "Bagaimana repeat behavior dan retention mechanism? Apa referral loop yang bisa diaktifkan?",
                "recommendation": "Retention > Acquisition untuk sustainable growth. Build feedback loop dan customer experience tracking.",
                "phase": "Tactical - CRM & Retention",
                "leverage": "high"
            },
            "data_governance": {
                "question": "Apa KPI consistency dan governance ownership structure? Di mana observability gap yang perlu ditutup?",
                "recommendation": "Prioritaskan observability lebih dulu daripada automation. Pastikan metric consistency lintas team.",
                "phase": "Engine - Data & Insight",
                "leverage": "critical"
            },
            "scalability_risk": {
                "question": "Apa scalability risk terbesar? Bagaimana infrastructure readiness untuk handle growth?",
                "recommendation": "Optimize for developer velocity, bukan premature optimization. Tapi identify architectural constraints early.",
                "phase": "Engine - Scalability",
                "leverage": "medium"
            },
            "unit_economics": {
                "question": "Bagaimana unit economics dan profitability model? Apa hidden cost yang belum terlihat?",
                "recommendation": "Calculate LTV:CAC ratio early. Identify break-even point. Track contribution margin by segment.",
                "phase": "Engine - Profitability",
                "leverage": "critical"
            },
            "operational_sustainability": {
                "question": "Apa operational constraint dan sustainability risk? Bagaimana mengurangi dependency pada intuisi individu?",
                "recommendation": "Build systems, not heroics. Document processes. Reduce ambiguity through clear governance.",
                "phase": "Engine - Sustainability",
                "leverage": "high"
            },
            "bottleneck_detection": {
                "question": "Di mana strategic drift atau leakage yang terjadi? Apa bottleneck terbesar saat ini?",
                "recommendation": "Use vertical slice thinking. Prioritize fixing biggest bottleneck before expanding scope.",
                "phase": "Strategic - Bottleneck Detection",
                "leverage": "critical"
            }
        }
    
    def generate_grill_question(self, user_input: str, conversation_history: list = None) -> dict:
        """
        Generate the next grill question based on Rohadi AI philosophy.
        
        Args:
            user_input: Current user message
            conversation_history: Previous Q&A pairs with context
            
        Returns:
            Dict with question, recommendation, phase, and leverage score
        """
        # If this is the first question, start with market understanding or bottleneck detection
        if not conversation_history or len(conversation_history) == 0:
            return self._get_initial_question(user_input)
        
        # Analyze conversation progress and determine next highest-leverage question
        answered_topics = self._extract_answered_topics(conversation_history)
        next_topic = self._determine_next_topic(answered_topics, conversation_history)
        
        return self.question_templates.get(next_topic, self._get_fallback_question())
    
    def _get_initial_question(self, user_input: str) -> dict:
        """Get the first question based on user's initial idea.
        
        Rohadi AI starts with either:
        1. Market Understanding (if idea is vague)
        2. Bottleneck Detection (if idea has some context)
        """
        # Check if user provided enough context
        word_count = len(user_input.split())
        
        if word_count < 20:
            # Vague idea - start with market understanding
            return self.question_templates["market_understanding"]
        else:
            # More detailed idea - start with bottleneck detection
            return self.question_templates["bottleneck_detection"]
    
    def _extract_answered_topics(self, history: list) -> set:
        """Extract which topics have been covered in the conversation."""
        answered = set()
        for item in history:
            if isinstance(item, dict) and 'topic' in item:
                answered.add(item['topic'])
        return answered
    
    def _determine_next_topic(self, answered_topics: set, conversation_history: list = None) -> str:
        """Determine which topic to ask next based on leverage priority.
        
        Rohadi AI prioritizes questions by leverage:
        - Critical: data_governance, unit_economics, bottleneck_detection
        - High: market_understanding, value_creation, acquisition_efficiency, 
                activation_bottleneck, crm_retention, operational_sustainability
        - Medium: brand_blueprint, awareness_strategy, scalability_risk
        """
        # Priority order based on leverage (observability-first approach)
        priority_order = [
            "market_understanding",      # Foundation
            "value_creation",            # Differentiation
            "bottleneck_detection",      # Critical path
            "acquisition_efficiency",    # CAC observability
            "activation_bottleneck",     # Conversion friction
            "data_governance",           # KPI consistency (critical)
            "unit_economics",            # Profitability (critical)
            "crm_retention",             # Sustainable growth
            "operational_sustainability", # Systems > heroics
            "awareness_strategy",        # Channel strategy
            "brand_blueprint",           # Positioning
            "scalability_risk"           # Infrastructure
        ]
        
        # Find first unanswered topic with highest leverage
        for topic in priority_order:
            if topic not in answered_topics:
                return topic
        
        # If all topics covered, wrap up with synthesis
        return "operational_sustainability"
    
    def _get_fallback_question(self) -> dict:
        """Fallback question focusing on implementation mindset."""
        return {
            "question": "Jika sudah cukup context, apa MVP realistis yang bisa dibangun dengan vertical slice thinking?",
            "recommendation": "Prioritaskan observability lebih dulu daripada automation. Build MVP yang measurable, bukan feature-complete.",
            "phase": "Implementation - MVP Realistis",
            "leverage": "high"
        }
    
    def format_response(self, question_data: dict) -> str:
        """Format the question and recommendation in Rohadi AI style.
        
        Output Style:
        - Ringkas tapi tajam
        - Fokus pada leverage terbesar
        - Jelaskan trade-off dan risiko
        - Gunakan reasoning yang observable dan explicit
        """
        leverage_indicator = "🔴 CRITICAL" if question_data.get('leverage') == 'critical' else \
                           "🟠 HIGH" if question_data.get('leverage') == 'high' else "🟡 MEDIUM"
        
        response = f"{leverage_indicator} **[{question_data['phase']}]**\n\n"
        response += f"**Pertanyaan:**\n{question_data['question']}\n\n"
        response += f"**Rekomendasi Rohadi:**\n{question_data['recommendation']}"
        
        return response


# Singleton instance
grill_me_skill = GrillMeSkill()
