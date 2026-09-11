"""
Unit tests for MumtaAI Intent Detector (tests/test_intent_detector.py).
Tests standalone conversational intents, MumtaAI domain requests, priority rules,
normalization, and canned responses completely offline.
"""

import pytest
from intent_detector import (
    detect_intent,
    get_canned_response,
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
    INTENT_BABY_PROFILE,
    INTENT_OXIMETER,
    INTENT_CRY_ANALYSIS,
    INTENT_SUBSCRIPTIONS,
    INTENT_PRIVACY,
    INTENT_PASSWORD_RESET,
    INTENT_CAREGIVER,
    INTENT_GENERAL_PRODUCT,
    INTENT_UNKNOWN,
)


# =============================================================================
# 1. Non-LLM Conversational Intents (should_use_llm = False)
# =============================================================================

@pytest.mark.parametrize("query,expected_intent", [
    ("hi", INTENT_GREETING),
    ("hello", INTENT_GREETING),
    ("hey", INTENT_GREETING),
    ("hey there", INTENT_GREETING),
    ("hello there", INTENT_GREETING),
    ("good morning", INTENT_GREETING),
    ("good afternoon", INTENT_GREETING),
    ("good evening", INTENT_GREETING),
    ("thanks", INTENT_THANKS),
    ("thank you", INTENT_THANKS),
    ("thanks a lot", INTENT_THANKS),
    ("thank you so much", INTENT_THANKS),
    ("appreciate it", INTENT_THANKS),
    ("much appreciated", INTENT_THANKS),
    ("bye", INTENT_GOODBYE),
    ("goodbye", INTENT_GOODBYE),
    ("see you", INTENT_GOODBYE),
    ("see you later", INTENT_GOODBYE),
    ("talk to you later", INTENT_GOODBYE),
    ("good night", INTENT_GOODBYE),
    ("okay", INTENT_ACKNOWLEDGEMENT),
    ("ok", INTENT_ACKNOWLEDGEMENT),
    ("alright", INTENT_ACKNOWLEDGEMENT),
    ("got it", INTENT_ACKNOWLEDGEMENT),
    ("understood", INTENT_ACKNOWLEDGEMENT),
    ("makes sense", INTENT_ACKNOWLEDGEMENT),
    ("sure", INTENT_ACKNOWLEDGEMENT),
    ("yes", INTENT_CONFIRMATION),
    ("yeah", INTENT_CONFIRMATION),
    ("yep", INTENT_CONFIRMATION),
    ("correct", INTENT_CONFIRMATION),
    ("exactly", INTENT_CONFIRMATION),
    ("that's right", INTENT_CONFIRMATION),
    ("no", INTENT_SIMPLE_NEGATIVE),
    ("nope", INTENT_SIMPLE_NEGATIVE),
    ("not really", INTENT_SIMPLE_NEGATIVE),
    ("great", INTENT_SIMPLE_POSITIVE),
    ("awesome", INTENT_SIMPLE_POSITIVE),
    ("perfect", INTENT_SIMPLE_POSITIVE),
    ("nice", INTENT_SIMPLE_POSITIVE),
    ("excellent", INTENT_SIMPLE_POSITIVE),
    ("that's great", INTENT_SIMPLE_POSITIVE),
    ("cancel", INTENT_CANCELLATION),
    ("never mind", INTENT_CANCELLATION),
    ("forget it", INTENT_CANCELLATION),
    ("stop", INTENT_CANCELLATION),
    ("don't worry about it", INTENT_CANCELLATION),
    ("what?", INTENT_SIMPLE_CLARIFICATION),
    ("huh?", INTENT_SIMPLE_CLARIFICATION),
    ("i don't understand", INTENT_SIMPLE_CLARIFICATION),
    ("can you repeat that?", INTENT_SIMPLE_CLARIFICATION),
    ("say that again", INTENT_SIMPLE_CLARIFICATION),
    ("what can you do?", INTENT_CAPABILITY_HELP),
    ("how can you help?", INTENT_CAPABILITY_HELP),
    ("i need help", INTENT_CAPABILITY_HELP),
])
def test_standalone_conversational_intents(query, expected_intent):
    result = detect_intent(query)
    assert result.intent == expected_intent
    assert result.should_use_llm is False
    assert result.confidence >= 0.9


# =============================================================================
# 2. MumtaAI Domain Product Requests (should_use_llm = True)
# =============================================================================

@pytest.mark.parametrize("query,expected_intent", [
    ("How do I create a baby profile?", INTENT_BABY_PROFILE),
    ("Can I add another baby?", INTENT_BABY_PROFILE),
    ("How do I switch between babies?", INTENT_BABY_PROFILE),
    ("How do I pair my oximeter?", INTENT_OXIMETER),
    ("What are the oximeter alert thresholds?", INTENT_OXIMETER),
    ("What does cry analysis do?", INTENT_CRY_ANALYSIS),
    ("How does cry analysis work?", INTENT_CRY_ANALYSIS),
    ("Why is my baby crying?", INTENT_CRY_ANALYSIS),
    ("How do I cancel Plus?", INTENT_SUBSCRIPTIONS),
    ("What are the subscription plans?", INTENT_SUBSCRIPTIONS),
    ("How does MumtaAI protect my data?", INTENT_PRIVACY),
    ("Is my data safe and encrypted?", INTENT_PRIVACY),
    ("What is MumtaAI?", INTENT_GENERAL_PRODUCT),
    ("How do I invite a caregiver?", INTENT_CAREGIVER),
    ("How do I reset my password?", INTENT_PASSWORD_RESET),
    ("Forgot my password", INTENT_PASSWORD_RESET),
])
def test_mumtaai_domain_requests(query, expected_intent):
    result = detect_intent(query)
    assert result.intent == expected_intent
    assert result.should_use_llm is True
    assert result.confidence >= 0.9


# =============================================================================
# 3. Priority Rules (Domain Request ALWAYS beats Conversational Word)
# =============================================================================

@pytest.mark.parametrize("query,expected_intent", [
    ("Hi, how do I create a baby profile?", INTENT_BABY_PROFILE),
    ("Hello, can you tell me how to pair my oximeter?", INTENT_OXIMETER),
    ("Thanks, but how do I reset my password?", INTENT_PASSWORD_RESET),
    ("Okay, how do I invite a caregiver?", INTENT_CAREGIVER),
    ("Hey, what does cry analysis do?", INTENT_CRY_ANALYSIS),
    ("Can you help me pair my oximeter?", INTENT_OXIMETER),
    ("Help me understand my baby's cry analysis", INTENT_CRY_ANALYSIS),
    ("Thanks, how do I use cry analysis?", INTENT_CRY_ANALYSIS),
    ("Great, but how do I cancel my subscription?", INTENT_SUBSCRIPTIONS),
])
def test_domain_priority_over_conversational(query, expected_intent):
    result = detect_intent(query)
    assert result.intent == expected_intent
    assert result.should_use_llm is True


# =============================================================================
# 4. Text Normalization Robustness
# =============================================================================

@pytest.mark.parametrize("query,expected_intent", [
    ("HI", INTENT_GREETING),
    ("Hi!", INTENT_GREETING),
    ("hello...", INTENT_GREETING),
    ("heyyy", INTENT_GREETING),
    ("thanks!!!", INTENT_THANKS),
    ("Thank You", INTENT_THANKS),
    ("  hello  ", INTENT_GREETING),
    ("BYE!!!", INTENT_GOODBYE),
    ("GREAT!!", INTENT_SIMPLE_POSITIVE),
])
def test_text_normalization(query, expected_intent):
    result = detect_intent(query)
    assert result.intent == expected_intent
    assert result.should_use_llm is False


# =============================================================================
# 5. Conservative Fallback on Unknown / Complex Queries
# =============================================================================

def test_unknown_fallback():
    # An unfamiliar query should safely route to LLM
    result = detect_intent("What is the weather in New York today?")
    assert result.intent == INTENT_UNKNOWN
    assert result.should_use_llm is True

    # Empty string should route to LLM/fallback
    result_empty = detect_intent("   ")
    assert result_empty.intent == INTENT_UNKNOWN
    assert result_empty.should_use_llm is True


# =============================================================================
# 6. Canned Responses
# =============================================================================

def test_canned_responses():
    greeting_resp = get_canned_response(INTENT_GREETING)
    assert "MumtaAI" in greeting_resp
    assert len(greeting_resp) > 10

    thanks_resp = get_canned_response(INTENT_THANKS)
    assert "welcome" in thanks_resp.lower()

    help_resp = get_canned_response(INTENT_CAPABILITY_HELP)
    assert "baby profiles" in help_resp.lower()
    assert "oximeter" in help_resp.lower()
