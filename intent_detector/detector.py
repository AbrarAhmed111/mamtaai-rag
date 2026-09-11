"""
Deterministic Rule-Based Intent Detector for MumtaAI Product Guide & Support.
Operates completely offline without LLMs or cloud APIs.
"""

import re
from typing import List, Tuple, Optional

from intent_detector.normalizer import normalize_text, strip_punctuation
from intent_detector.types import (
    IntentResult,
    # Conversational (should_use_llm = False)
    INTENT_GREETING,
    INTENT_THANKS,
    INTENT_GOODBYE,
    INTENT_ACKNOWLEDGEMENT,
    INTENT_CONFIRMATION,
    INTENT_SIMPLE_NEGATIVE,
    INTENT_SIMPLE_POSITIVE,
    INTENT_CANCELLATION,
    INTENT_SIMPLE_CLARIFICATION,
    INTENT_CAPABILITY_HELP,
    # Domain (should_use_llm = True)
    INTENT_ACCOUNT,
    INTENT_AUTHENTICATION,
    INTENT_PASSWORD_RESET,
    INTENT_EMAIL_VERIFICATION,
    INTENT_BABY_PROFILE,
    INTENT_CAREGIVER,
    INTENT_FAMILY,
    INTENT_ACTIVITY_TRACKING,
    INTENT_RECORDINGS,
    INTENT_CRY_ANALYSIS,
    INTENT_OXIMETER,
    INTENT_INSIGHTS,
    INTENT_NOTIFICATIONS,
    INTENT_COMMUNITY,
    INTENT_EXPERTS,
    INTENT_SUBSCRIPTIONS,
    INTENT_BILLING,
    INTENT_SETTINGS,
    INTENT_PRIVACY,
    INTENT_TROUBLESHOOTING,
    INTENT_GENERAL_PRODUCT,
    INTENT_UNKNOWN,
)


# =============================================================================
# 1. MumtaAI Product Feature Rules (Priority 1: Always Route to LLM / RAG)
# =============================================================================

MUMTAAI_DOMAIN_RULES: List[Tuple[str, List[str], str]] = [
    # (Intent, [regex patterns], rule_name)
    (
        INTENT_PASSWORD_RESET,
        [
            r"\b(reset|forgot|change)\s+(my\s+)?password\b",
            r"\bpassword\s+reset\b",
            r"\bcannot\s+(remember|login)\s+password\b",
        ],
        "domain_password_reset",
    ),
    (
        INTENT_EMAIL_VERIFICATION,
        [
            r"\b(verify|confirm|resend)\s+(my\s+)?email\b",
            r"\bemail\s+verification\b",
            r"\bverification\s+(code|email|link)\b",
        ],
        "domain_email_verification",
    ),
    (
        INTENT_AUTHENTICATION,
        [
            r"\b(log\s*in|sign\s*in|log\s*out|sign\s*out)\b",
            r"\bhow\s+do\s+i\s+(login|logout|signin|signout)\b",
            r"\bcannot\s+(log\s*in|sign\s*in)\b",
        ],
        "domain_authentication",
    ),
    (
        INTENT_CRY_ANALYSIS,
        [
            r"\bcry\s+(analysis|detection|model|classifier|feature|pattern)\b",
            r"\bcrying\s+(analysis|translation|patterns)\b",
            r"\bwhat\s+does\s+cry\s+analysis\b",
            r"\bhow\s+does\s+cry\s+analysis\b",
            r"\bbaby('s)?\s+cry\b",
            r"\bwhy\s+is\s+my\s+baby\s+crying\b",
        ],
        "domain_cry_analysis",
    ),
    (
        INTENT_OXIMETER,
        [
            r"\boximeter\b",
            r"\b(pair|connect|sync)\s+(my\s+)?oximeter\b",
            r"\b(pulse|spo2|oxygen\s+saturation)\b",
            r"\boximeter\s+(pairing|reading|readings|alert|alerts|threshold)\b",
            r"\bfoot\s+sensor\b",
        ],
        "domain_oximeter",
    ),
    (
        INTENT_BABY_PROFILE,
        [
            r"\b(create|add|setup|set\s+up|register|edit|delete)\s+(a\s+|my\s+|another\s+)?baby(\s+profile)?\b",
            r"\bbaby\s+profile(s)?\b",
            r"\bmultiple\s+babies\b",
            r"\badd\s+(a\s+|another\s+)?(child|infant|baby)\b",
            r"\bswitch\s+between\s+babies\b",
        ],
        "domain_baby_profile",
    ),
    (
        INTENT_CAREGIVER,
        [
            r"\b(invite|add|remove|manage)\s+(a\s+|my\s+)?caregiver(s)?\b",
            r"\bcaregiver\s+(invitation|invite|access|role|permissions)\b",
            r"\bnanny\b",
            r"\bbabysitter\b",
        ],
        "domain_caregiver",
    ),
    (
        INTENT_FAMILY,
        [
            r"\bfamily\s+(member|members|sharing|access)\b",
            r"\b(co-parent|partner|grandparent)\s+access\b",
        ],
        "domain_family",
    ),
    (
        INTENT_ACTIVITY_TRACKING,
        [
            r"\b(track|log)\s+(feeding|diaper|sleep|nursing|nap|bottle)\b",
            r"\bactivity\s+tracking\b",
            r"\bfeeding\s+schedule\b",
            r"\bsleep\s+log(s)?\b",
        ],
        "domain_activity_tracking",
    ),
    (
        INTENT_RECORDINGS,
        [
            r"\b(audio\s+)?recording(s)?\b",
            r"\brecord\s+(my\s+)?baby('s)?\s+cry\b",
            r"\bplay\s+(back\s+)?recording\b",
        ],
        "domain_recordings",
    ),
    (
        INTENT_SUBSCRIPTIONS,
        [
            r"\b(subscription|subscriptions|pricing|tier|tiers)\b",
            r"\b(upgrade|downgrade|cancel)\s+(to\s+|my\s+)?(subscription|plus|pro|plan)\b",
            r"\b(free|plus|pro)\s+plan\b",
            r"\bhow\s+much\s+does\s+mumtaai\s+cost\b",
        ],
        "domain_subscriptions",
    ),
    (
        INTENT_BILLING,
        [
            r"\b(billing|invoice|receipt|charge|refund|stripe)\b",
            r"\b(credit\s+card|payment\s+method)\b",
            r"\bupdate\s+payment\b",
        ],
        "domain_billing",
    ),
    (
        INTENT_PRIVACY,
        [
            r"\b(privacy|data\s+protection|hipaa|gdpr|encryption)\b",
            r"\bhow\s+does\s+mumtaai\s+(protect|use|store)\s+(my\s+)?data\b",
            r"\bis\s+my\s+data\s+safe\b",
            r"\bdelete\s+my\s+data\b",
        ],
        "domain_privacy",
    ),
    (
        INTENT_INSIGHTS,
        [
            r"\b(baby\s+)?insight(s)?\b",
            r"\b(daily|weekly)\s+(report|trends|analytics)\b",
            r"\bdevelopmental\s+milestone(s)?\b",
        ],
        "domain_insights",
    ),
    (
        INTENT_NOTIFICATIONS,
        [
            r"\b(notification|notifications|push\s+notifications|alert\s+settings)\b",
            r"\bnot\s+getting\s+alerts\b",
        ],
        "domain_notifications",
    ),
    (
        INTENT_COMMUNITY,
        [
            r"\b(community|parent\s+community|forum|discussion\s+board)\b",
        ],
        "domain_community",
    ),
    (
        INTENT_EXPERTS,
        [
            r"\b(expert|pediatrician|specialist|consult\s+expert|doctor\s+advice)\b",
        ],
        "domain_experts",
    ),
    (
        INTENT_SETTINGS,
        [
            r"\b(app\s+settings|account\s+settings|preferences|dark\s+mode|change\s+language)\b",
        ],
        "domain_settings",
    ),
    (
        INTENT_TROUBLESHOOTING,
        [
            r"\b(not\s+working|doesn't\s+work|won't\s+work|crashing|bug|glitch|error\s+code)\b",
            r"\b(troubleshoot|cannot\s+connect|failed\s+to\s+pair|app\s+keeps\s+freezing)\b",
        ],
        "domain_troubleshooting",
    ),
    (
        INTENT_ACCOUNT,
        [
            r"\b(create|setup|register|open|delete)\s+(an\s+|my\s+)?account\b",
            r"\baccount\s+(creation|registration|management)\b",
        ],
        "domain_account",
    ),
    (
        INTENT_GENERAL_PRODUCT,
        [
            r"\bwhat\s+is\s+mumtaai\b",
            r"\bhow\s+does\s+mumtaai\s+work\b",
            r"\babout\s+mumtaai\b",
            r"\bmumtaai\s+(features|overview|guide)\b",
        ],
        "domain_general_product",
    ),
]


# =============================================================================
# 2. Standalone Conversational Rules (Priority 2: Zero-LLM Canned Answers)
# =============================================================================

EXACT_CONVERSATIONAL_RULES = {
    # 1. Greetings
    INTENT_GREETING: [
        "hi", "hello", "hey", "hey there", "hello there", "heya",
        "good morning", "good afternoon", "good evening", "greetings", "howdy",
    ],
    # 2. Thanks
    INTENT_THANKS: [
        "thanks", "thank you", "thanks a lot", "thank you so much",
        "appreciate it", "much appreciated", "thx", "ty", "many thanks",
    ],
    # 3. Goodbye
    INTENT_GOODBYE: [
        "bye", "goodbye", "see you", "see you later", "talk to you later",
        "good night", "cya", "bye bye", "have a good day",
    ],
    # 4. Acknowledgement
    INTENT_ACKNOWLEDGEMENT: [
        "okay", "ok", "alright", "got it", "understood", "makes sense",
        "sure", "k", "cool", "fine",
    ],
    # 5. Confirmation
    INTENT_CONFIRMATION: [
        "yes", "yeah", "yep", "correct", "exactly", "that's right",
        "right", "definitely", "absolutely",
    ],
    # 6. Simple Negative
    INTENT_SIMPLE_NEGATIVE: [
        "no", "nope", "not really", "nah", "negative",
    ],
    # 7. Positive Reaction
    INTENT_SIMPLE_POSITIVE: [
        "great", "awesome", "perfect", "nice", "excellent", "that's great",
        "wonderful", "fantastic", "amazing",
    ],
    # 8. Cancellation
    INTENT_CANCELLATION: [
        "cancel", "never mind", "nevermind", "forget it", "stop",
        "don't worry about it", "dont worry", "leave it",
    ],
    # 9. Simple Clarification
    INTENT_SIMPLE_CLARIFICATION: [
        "what?", "what", "huh?", "huh", "i don't understand", "dont understand",
        "can you repeat that?", "can you repeat that", "say that again",
        "pardon?", "pardon",
    ],
    # 10. Capability / Generic Help
    INTENT_CAPABILITY_HELP: [
        "what can you do?", "what can you do", "how can you help?", "how can you help",
        "i need help", "help", "help me", "can you help me?", "can you help me",
        "what are your capabilities", "what do you do?", "what do you do",
    ],
}


# =============================================================================
# 3. Core Intent Detection Function
# =============================================================================

def detect_intent(text: str) -> IntentResult:
    """
    Classifies the user input into a structured IntentResult.
    
    Priority Algorithm:
    1. Check for MumtaAI product & support features (oximeter, cry analysis, baby profile, billing, etc.).
       -> If found: MUST return that domain intent with should_use_llm = True.
    2. Check for standalone conversational intents (greeting, thanks, goodbye, ok, etc.).
       -> Only triggered if NO domain keywords exist and message is a simple conversational phrase.
       -> Returns conversational intent with should_use_llm = False.
    3. Fallback:
       -> Ambiguous, compound, or unclassified queries default to 'unknown' with should_use_llm = True.
    """
    if not text or not text.strip():
        return IntentResult(
            intent=INTENT_UNKNOWN,
            should_use_llm=True,
            confidence=0.0,
            matched_rule="empty_input",
            reason="Input message is empty",
        )

    norm_text = normalize_text(text)
    stripped = strip_punctuation(norm_text)
    words = norm_text.split()
    word_count = len(words)

    # -------------------------------------------------------------------------
    # STEP 1: Check MumtaAI Domain Topics (Top Priority)
    # -------------------------------------------------------------------------
    for intent, patterns, rule_name in MUMTAAI_DOMAIN_RULES:
        for pattern in patterns:
            if re.search(pattern, norm_text, re.IGNORECASE):
                return IntentResult(
                    intent=intent,
                    should_use_llm=True,
                    confidence=0.95,
                    matched_rule=rule_name,
                    reason=f"Matched MumtaAI product feature rule '{rule_name}'",
                )

    # -------------------------------------------------------------------------
    # STEP 2: Check Standalone Conversational Intents (Zero-LLM)
    # -------------------------------------------------------------------------
    # Conversational shortcuts are only safe for concise standalone messages
    # (typically <= 6 words). Long messages with question words should not be
    # swallowed by conversational rules.
    has_question_indicators = bool(
        re.search(r"\b(how|what|where|when|why|who|can\s+i|is\s+there|could\s+you)\b", norm_text)
    )

    for intent, phrases in EXACT_CONVERSATIONAL_RULES.items():
        # A. Exact match against stripped text (e.g., "thanks", "hello", "what can you do")
        if stripped in phrases:
            return IntentResult(
                intent=intent,
                should_use_llm=False,
                confidence=1.0,
                matched_rule=f"exact_{intent}",
                reason=f"Matched standalone conversational phrase for '{intent}'",
            )

        # B. For short messages (<= 4 words) without substantive question indicators,
        # check if it's a simple greeting or farewell
        if word_count <= 4 and not has_question_indicators:
            for phrase in phrases:
                # Word-boundary match for the phrase alone
                if re.fullmatch(re.escape(phrase), stripped):
                    return IntentResult(
                        intent=intent,
                        should_use_llm=False,
                        confidence=0.9,
                        matched_rule=f"short_{intent}",
                        reason=f"Matched concise conversational phrase for '{intent}'",
                    )

    # -------------------------------------------------------------------------
    # STEP 3: Fallback (Conservative: When uncertain -> Route to LLM / RAG)
    # -------------------------------------------------------------------------
    return IntentResult(
        intent=INTENT_UNKNOWN,
        should_use_llm=True,
        confidence=0.0,
        matched_rule="fallback_unknown",
        reason="No deterministic conversational shortcut or product rule matched. Routing to LLM/RAG.",
    )
