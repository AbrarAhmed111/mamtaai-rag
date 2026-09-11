"""
Type definitions for MumtaAI Intent Detection.
"""

from typing import Optional
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Intent Constants
# -----------------------------------------------------------------------------

# Non-LLM Intents (should_use_llm = False)
INTENT_GREETING = "greeting"
INTENT_WELLBEING = "wellbeing"
INTENT_BOT_IDENTITY = "bot_identity"
INTENT_COMPLIMENT = "compliment"
INTENT_PLEASANTRY = "pleasantry"
INTENT_APOLOGY = "apology"
INTENT_PING = "ping"
INTENT_THANKS = "thanks"
INTENT_GOODBYE = "goodbye"
INTENT_ACKNOWLEDGEMENT = "acknowledgement"
INTENT_CONFIRMATION = "confirmation"
INTENT_SIMPLE_NEGATIVE = "simple_negative"
INTENT_SIMPLE_POSITIVE = "simple_positive_reaction"
INTENT_CANCELLATION = "cancellation"
INTENT_SIMPLE_CLARIFICATION = "simple_clarification"
INTENT_CAPABILITY_HELP = "capability_help"

# MumtaAI Domain Intents (should_use_llm = True)
INTENT_ACCOUNT = "account"
INTENT_AUTHENTICATION = "authentication"
INTENT_PASSWORD_RESET = "password_reset"
INTENT_EMAIL_VERIFICATION = "email_verification"
INTENT_BABY_PROFILE = "baby_profile"
INTENT_CAREGIVER = "caregiver"
INTENT_FAMILY = "family"
INTENT_ACTIVITY_TRACKING = "activity_tracking"
INTENT_RECORDINGS = "recordings"
INTENT_CRY_ANALYSIS = "cry_analysis"
INTENT_OXIMETER = "oximeter"
INTENT_INSIGHTS = "insights"
INTENT_NOTIFICATIONS = "notifications"
INTENT_COMMUNITY = "community"
INTENT_EXPERTS = "experts"
INTENT_SUBSCRIPTIONS = "subscriptions"
INTENT_BILLING = "billing"
INTENT_SETTINGS = "settings"
INTENT_PRIVACY = "privacy"
INTENT_TROUBLESHOOTING = "troubleshooting"
INTENT_GENERAL_PRODUCT = "general_product_question"
INTENT_UNKNOWN = "unknown"


class IntentResult(BaseModel):
    """
    Structured result returned by the Intent Detector.
    """
    intent: str = Field(..., description="Detected intent name")
    should_use_llm: bool = Field(..., description="Whether this message requires LLM/RAG processing")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Detection confidence score")
    matched_rule: Optional[str] = Field(default=None, description="Identifier of the rule that matched")
    reason: Optional[str] = Field(default=None, description="Explanation for routing decision")
