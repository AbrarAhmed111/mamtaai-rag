"""
MumtaAI Canned Responses for Non-LLM Intents.
Kept strictly separate from detection logic.
"""

from typing import Dict
from .types import (
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
)

CANNED_RESPONSES: Dict[str, str] = {
    INTENT_GREETING: (
        "Hello! I am your MumtaAI Product Guide & Support Assistant. "
        "How can I help you with your account, baby profiles, cry analysis, or oximeter today?"
    ),
    INTENT_THANKS: (
        "You're very welcome! I'm always here if you have any more questions about MumtaAI."
    ),
    INTENT_GOODBYE: (
        "Goodbye! Take care, and feel free to reach out anytime you need support."
    ),
    INTENT_ACKNOWLEDGEMENT: (
        "Understood. Let me know whenever you're ready to explore another MumtaAI feature."
    ),
    INTENT_CONFIRMATION: (
        "Great! Let me know if there's anything else you'd like to check or configure in MumtaAI."
    ),
    INTENT_SIMPLE_NEGATIVE: (
        "No problem at all. Just ask whenever you need assistance with MumtaAI."
    ),
    INTENT_SIMPLE_POSITIVE: (
        "Wonderful! Let me know if you have any other questions."
    ),
    INTENT_CANCELLATION: (
        "Cancelled. Is there anything else about MumtaAI I can assist you with?"
    ),
    INTENT_SIMPLE_CLARIFICATION: (
        "Could you please specify which MumtaAI feature, step, or topic you'd like me to explain?"
    ),
    INTENT_CAPABILITY_HELP: (
        "I am the MumtaAI Product Guide & Support Assistant. I can guide you through:\n"
        "• Setting up baby profiles & multiple babies\n"
        "• Inviting caregivers & managing permissions\n"
        "• Cry analysis & recordings\n"
        "• Smart oximeter pairing, readings & alert thresholds\n"
        "• Subscription tiers (Free, Plus, Pro) & billing\n"
        "• Account settings & privacy\n\n"
        "What would you like assistance with?"
    ),
}


def get_canned_response(intent: str) -> str:
    """
    Retrieve canned response text for a non-LLM intent.
    Falls back to a polite generic prompt if intent is not recognized.
    """
    return CANNED_RESPONSES.get(
        intent,
        "How can I help you with MumtaAI today?"
    )
