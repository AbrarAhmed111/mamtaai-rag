"""
MumtaAI Canned Responses for Non-LLM Intents.
Kept strictly separate from detection logic.
"""

from typing import Dict
from .types import (
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
)

CANNED_RESPONSES: Dict[str, str] = {
    INTENT_GREETING: (
        "Hello! I am your MumtaAI Product Guide & Support Assistant. "
        "I can help explain MumtaAI features, baby profile management, cry analysis, smart oximeter pairing, and subscription plans. "
        "How can I assist you with the platform today?"
    ),
    INTENT_WELLBEING: (
        "I'm doing great, thank you for asking! I'm here and ready to help you learn about MumtaAI — "
        "including setting up baby profiles, pairing your smart oximeter, and how cry analysis works. What can I answer for you?"
    ),
    INTENT_BOT_IDENTITY: (
        "I am the MumtaAI Product Guide & Support Assistant! I'm an AI assistant designed to help parents "
        "and caregivers navigate MumtaAI's product features, smart monitoring tools, cry insights, and subscription plans."
    ),
    INTENT_COMPLIMENT: (
        "Thank you so much! I'm glad I could help. Let me know if you have any other questions about MumtaAI features or guides."
    ),
    INTENT_PLEASANTRY: (
        "Nice to connect with you! I'm ready to guide you through any MumtaAI product features whenever you need."
    ),
    INTENT_APOLOGY: (
        "No worries at all! How can I assist you with MumtaAI product guides today?"
    ),
    INTENT_PING: (
        "I'm online and ready! What would you like to know about MumtaAI features or hardware?"
    ),
    INTENT_THANKS: (
        "You're very welcome! Feel free to ask anytime if you need help understanding MumtaAI features."
    ),
    INTENT_GOODBYE: (
        "Goodbye! Take care, and feel free to ask anytime you need guidance with MumtaAI."
    ),
    INTENT_ACKNOWLEDGEMENT: (
        "Understood. Let me know whenever you'd like to explore another MumtaAI feature or guide."
    ),
    INTENT_CONFIRMATION: (
        "Great! Let me know if there's anything else about MumtaAI you would like explained."
    ),
    INTENT_SIMPLE_NEGATIVE: (
        "No problem at all. Just ask whenever you have a question about MumtaAI features or setup."
    ),
    INTENT_SIMPLE_POSITIVE: (
        "Wonderful! Let me know if you have any questions about MumtaAI."
    ),
    INTENT_CANCELLATION: (
        "Cancelled. Is there anything else about MumtaAI features I can assist you with?"
    ),
    INTENT_SIMPLE_CLARIFICATION: (
        "Could you please specify which MumtaAI feature, device setup step, or topic you'd like me to explain?"
    ),
    INTENT_CAPABILITY_HELP: (
        "I am the MumtaAI Product Guide & Support Assistant. I provide information regarding:\n"
        "• What is MumtaAI & platform features\n"
        "• Setting up baby profiles & multi-baby limits\n"
        "• Inviting caregivers & permission levels\n"
        "• How acoustic cry analysis works & cry categories\n"
        "• Smart oximeter pairing, live SpO2/pulse readings & alert thresholds\n"
        "• Subscription plans (Free, Plus, Pro) & feature comparison\n"
        "• Data privacy and non-diagnostic medical disclaimers\n\n"
        "*(Note: I am a product documentation assistant and cannot access or modify private individual accounts. For private settings or vitals, please check your Dashboard.)*\n\n"
        "What product topic can I help you with today?"
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
