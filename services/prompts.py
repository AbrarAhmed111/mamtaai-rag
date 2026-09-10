"""
Centralized Prompt Templates and System Instructions
Keep your prompts organized in one place rather than scattered across route handlers.
"""

DEFAULT_SYSTEM_PROMPT = """You are a helpful, accurate, and concise AI assistant. 
Answer questions clearly and follow all user instructions carefully."""

STRUCTURED_EXTRACTION_SYSTEM_PROMPT = """You are an expert data extraction system.
Analyze the input text carefully and extract the requested information accurately into valid JSON matching the exact schema requested.
Do not include commentary or markdown formatting outside the JSON object."""

SUMMARY_SYSTEM_PROMPT = """You are an expert summarizer. 
Provide a clear, objective, and dense summary of the provided text, preserving essential facts and key takeaways."""


def build_chat_messages(
    messages: list,
    system_prompt: str | None = None,
) -> list:
    """
    Ensure the message list has a system prompt if provided.
    If the first message is not a system message and a system_prompt is given, prepends it.
    """
    formatted = []
    
    # Check if system prompt is needed
    has_system = any(m.get("role") == "system" for m in messages)
    if not has_system and system_prompt:
        formatted.append({"role": "system", "content": system_prompt})
        
    formatted.extend(messages)
    return formatted
