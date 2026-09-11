"""
Deterministic Rule-Based Intent Detector for MumtaAI Product Guide & Support.
Operates completely offline without LLMs or cloud APIs.
"""

import re
from typing import List, Tuple, Optional

from .normalizer import normalize_text, strip_punctuation
from .types import (
    IntentResult,
    # Conversational (should_use_llm = False)
    INTENT_GREETING,
    INTENT_WELLBEING,
    INTENT_BOT_IDENTITY,
    INTENT_COMPLIMENT,
    INTENT_PLEASANTRY,
    INTENT_APOLOGY,
    INTENT_PING,
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
            r"\bcry\s+(analysis|detection|model|classifier|feature|pattern(s)?)\b",
            r"\bcrying\s+(analysis|translation|pattern(s)?)\b",
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
        "hi", "hello", "hey", "hey there", "hello there", "heya", "hi there",
        "hiya", "yo", "good morning", "good afternoon", "good evening",
        "greetings", "howdy", "salam", "assalam o alaikum", "namaste",
    ],
    # 2. Wellbeing & Small Talk
    INTENT_WELLBEING: [
        "how are you", "how are you doing", "how are you today", "how are things",
        "how is it going", "hows it going", "how's it going", "hows everything",
        "how is everything", "how do you do", "whats up", "what's up", "what is up",
        "sup", "how have you been", "hows life", "how is life", "how is your day",
        "how was your day", "hows your day", "are you doing ok", "are you doing okay",
        "how r u", "how are u", "how you doing",
    ],
    # 3. Bot Persona / Identity
    INTENT_BOT_IDENTITY: [
        "who are you", "who are u", "what are you", "what are u", "what is your name",
        "whats your name", "what's your name", "who made you", "who created you",
        "are you a bot", "are you a robot", "are you an ai", "are you ai",
        "are you real", "are you human", "introduce yourself", "tell me about yourself",
    ],
    # 4. Compliments
    INTENT_COMPLIMENT: [
        "you are awesome", "you're awesome", "you are great", "you're great",
        "you are amazing", "you're amazing", "good bot", "good job", "nice work",
        "well done", "love you", "you are helpful", "you're so helpful",
        "you are the best", "you're the best", "i like you", "smart bot",
    ],
    # 5. Pleasantries
    INTENT_PLEASANTRY: [
        "nice to meet you", "pleased to meet you", "glad to meet you",
        "great to meet you", "good to see you",
    ],
    # 6. Apologies
    INTENT_APOLOGY: [
        "sorry", "i am sorry", "im sorry", "i'm sorry", "my bad",
        "excuse me", "pardon me", "apologies",
    ],
    # 7. Ping / Availability
    INTENT_PING: [
        "test", "testing", "ping", "check", "hello world", "are you there",
        "are you online", "can you hear me", "anyone there",
    ],
    # 8. Thanks
    INTENT_THANKS: [
        "thanks", "thank you", "thanks a lot", "thank you so much",
        "thanks so much", "appreciate it", "much appreciated", "thx", "ty",
        "many thanks", "thanks a ton", "thank u",
    ],
    # 9. Goodbye
    INTENT_GOODBYE: [
        "bye", "goodbye", "see you", "see you later", "see ya", "talk to you later",
        "talk soon", "good night", "cya", "bye bye", "have a good day",
        "have a great day", "have a good one", "take care",
    ],
    # 10. Acknowledgement
    INTENT_ACKNOWLEDGEMENT: [
        "okay", "ok", "alright", "all right", "got it", "understood", "makes sense",
        "sure", "k", "cool", "fine", "noted", "gotcha", "will do", "roger that", "sounds good",
    ],
    # 11. Confirmation
    INTENT_CONFIRMATION: [
        "yes", "yeah", "yep", "yup", "correct", "exactly", "that's right",
        "thats right", "right", "definitely", "absolutely",
    ],
    # 12. Simple Negative
    INTENT_SIMPLE_NEGATIVE: [
        "no", "nope", "not really", "nah", "negative", "no thanks", "no thank you",
    ],
    # 13. Positive Reaction
    INTENT_SIMPLE_POSITIVE: [
        "great", "awesome", "perfect", "nice", "excellent", "that's great",
        "thats great", "wonderful", "fantastic", "amazing",
    ],
    # 14. Cancellation
    INTENT_CANCELLATION: [
        "cancel", "never mind", "nevermind", "forget it", "stop",
        "don't worry about it", "dont worry", "leave it", "abort",
    ],
    # 15. Simple Clarification
    INTENT_SIMPLE_CLARIFICATION: [
        "what?", "what", "huh?", "huh", "i don't understand", "dont understand",
        "can you repeat that?", "can you repeat that", "say that again",
        "pardon?", "pardon", "come again",
    ],
    # 16. Capability / Generic Help
    INTENT_CAPABILITY_HELP: [
        "what can you do?", "what can you do", "what can u do", "what do you do?",
        "what do you do", "how can you help?", "how can you help", "how can you help me?",
        "how can you help me", "i need help", "help", "help me", "can you help me?",
        "can you help me", "what are your capabilities", "what are your features",
        "show me features", "guide me", "menu", "commands",
    ],
}

# Regex patterns for conversational intents when phrasing varies slightly
CONVERSATIONAL_REGEX_PATTERNS: List[Tuple[str, List[str]]] = [
    (
        INTENT_WELLBEING,
        [
            r"^(how|how's|hows)\s+(are\s+(you|u)|is\s+it\s+going|are\s+things|everything|have\s+you\s+been|r\s+u|do\s+you\s+do|your\s+day)(\s+.*)?\??$",
            r"^(what's\s+up|whats\s+up|what\s+is\s+up|sup)(\s+.*)?\??$",
            r"^are\s+you\s+doing\s+(ok|okay|well|fine|good)(\s+.*)?\??$",
        ],
    ),
    (
        INTENT_BOT_IDENTITY,
        [
            r"^(who|what)\s+(are\s+(you|u)|is\s+your\s+name|made\s+(you|u)|created\s+(you|u))(\s+.*)?\??$",
            r"^are\s+you\s+(a\s+bot|a\s+robot|an\s+ai|ai|human|real)(\s+.*)?\??$",
            r"^(introduce\s+yourself|tell\s+me\s+about\s+yourself)(\s+.*)?\??$",
        ],
    ),
    (
        INTENT_COMPLIMENT,
        [
            r"^(you're|you\s+are)\s+(so\s+|really\s+|very\s+)?(awesome|great|amazing|the\s+best|cool|smart|helpful|wonderful)(\s+.*)?!?\.?$",
            r"^(good\s+job|nice\s+work|well\s+done)(\s+.*)?!?\.?$",
        ],
    ),
    (
        INTENT_PLEASANTRY,
        [
            r"^(nice|pleased|glad|great|good)\s+to\s+(meet|see)\s+you(\s+.*)?!?\.?$",
        ],
    ),
    (
        INTENT_APOLOGY,
        [
            r"^(i'm\s+sorry|im\s+sorry|i\s+am\s+sorry|my\s+bad|sorry|apologies)(\s+.*)?!?\.?$",
        ],
    ),
    (
        INTENT_PING,
        [
            r"^(are\s+you\s+(there|online)|can\s+you\s+hear\s+me|anyone\s+there)(\s+.*)?\??$",
            r"^(test|testing|ping)$",
        ],
    ),
    (
        INTENT_CAPABILITY_HELP,
        [
            r"^(what\s+can\s+(you|u)\s+do|how\s+can\s+(you|u)\s+help|what\s+do\s+you\s+do)(\s+.*)?\??$",
            r"^(can\s+you\s+help\s+me|help\s+me\s+please|what\s+are\s+your\s+(features|capabilities))(\s+.*)?\??$",
        ],
    ),
    (
        INTENT_GREETING,
        [
            r"^(hi|hello|hey|heya|hiya|howdy|yo|greetings)(\s+(there|friend|bot|assistant|mumtaai|mumta))?!?\.?\??$",
        ],
    ),
    (
        INTENT_THANKS,
        [
            r"^(thank\s+(you|u)|thanks|thx|ty)(\s+.*)?!?\.?$",
        ],
    ),
    (
        INTENT_GOODBYE,
        [
            r"^(bye|goodbye|bye\s+bye|see\s+ya|see\s+you|good\s+night|take\s+care|cya)(\s+.*)?!?\.?$",
        ],
    ),
]


# =============================================================================
# 3. Core Intent Detection Function
# =============================================================================

def detect_intent(text: str) -> IntentResult:
    """
    Classifies the user input into a structured IntentResult.
    
    Priority Algorithm:
    1. Check for MumtaAI product & support features (oximeter, cry analysis, baby profile, billing, etc.).
       -> If found: MUST return that domain intent with should_use_llm = True.
    2. Check for conversational intents (wellbeing, greetings, bot identity, thanks, goodbye, ok, etc.).
       -> Only triggered if NO domain keywords exist.
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
    # A. Exact match against stripped text (e.g. "how are you", "thanks", "who are you")
    for intent, phrases in EXACT_CONVERSATIONAL_RULES.items():
        if stripped in phrases:
            return IntentResult(
                intent=intent,
                should_use_llm=False,
                confidence=1.0,
                matched_rule=f"exact_{intent}",
                reason=f"Matched standalone conversational phrase for '{intent}'",
            )

    # B. Regex patterns for flexible conversational phrasing (e.g. "how are you doing today?")
    for intent, patterns in CONVERSATIONAL_REGEX_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, norm_text, re.IGNORECASE) or re.search(pattern, stripped, re.IGNORECASE):
                return IntentResult(
                    intent=intent,
                    should_use_llm=False,
                    confidence=0.95,
                    matched_rule=f"regex_{intent}",
                    reason=f"Matched conversational pattern for '{intent}'",
                )

    # C. For very short messages (<= 4 words), check fullmatch against phrase dictionary
    if word_count <= 4:
        for intent, phrases in EXACT_CONVERSATIONAL_RULES.items():
            for phrase in phrases:
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

