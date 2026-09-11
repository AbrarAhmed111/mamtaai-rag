"""
LLM Gateway Layer
Provides automatic fallback across multiple providers and multiple API keys.
Handles:
- Deployments configuration (Gemini x4, Groq, OpenAI, Mistral, Cerebras)
- Error classification (retryable 429/quota/5xx vs non-retryable 400/401)
- Cooldown tracking (avoids hammering a provider that recently rate-limited)
- User-facing provider status events ("fallback", "switched")
"""

import os
import time
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage

load_dotenv()
logger = logging.getLogger("LLMGateway")


# -----------------------------------------------------------------------------
# 1. Provider Deployment Configuration
# -----------------------------------------------------------------------------
@dataclass
class ProviderDeployment:
    """Represents a specific provider deployment with its own key, base URL, and model."""
    name: str              # User-friendly name, e.g. "Gemini #1", "Groq"
    provider: str          # Provider category: "gemini", "groq", "openai", "mistral", "cerebras"
    api_key: str           # Secret API key (never exposed in output or logs)
    base_url: Optional[str]# Custom API base URL if OpenAI-compatible
    default_model: str     # Provider-specific model name
    cooldown_seconds: int = 60
    cooldown_until: float = 0.0
    is_permanently_disabled: bool = False

    @property
    def is_available(self) -> bool:
        """Returns True if the deployment is not disabled and not currently in cooldown."""
        if self.is_permanently_disabled:
            return False
        return time.time() >= self.cooldown_until

    def mark_cooldown(self, seconds: Optional[int] = None) -> None:
        """Put this deployment on temporary cooldown after a rate limit or transient failure."""
        duration = seconds or self.cooldown_seconds
        self.cooldown_until = time.time() + duration

    def mark_disabled(self) -> None:
        """Mark deployment as permanently disabled (e.g. invalid API key)."""
        self.is_permanently_disabled = True


# -----------------------------------------------------------------------------
# 2. Error Classification
# -----------------------------------------------------------------------------
class ErrorClassifier:
    """
    Classifies errors into:
    - Retryable: 429 rate limit, quota exhaustion, 5xx server errors, network timeouts.
    - Non-Retryable: 400 bad request, 401 unauthorized (bad key), 403 forbidden, policy violations.
    """

    RETRYABLE_KEYWORDS = [
        "rate limit",
        "ratelimit",
        "quota",
        "429",
        "resource exhausted",
        "overloaded",
        "server error",
        "500",
        "502",
        "503",
        "504",
        "bad gateway",
        "gateway timeout",
        "timeout",
        "timed out",
        "connection error",
        "temporarily unavailable",
    ]

    NON_RETRYABLE_KEYWORDS = [
        "invalid_api_key",
        "invalid api key",
        "authentication",
        "unauthorized",
        "401",
        "forbidden",
        "403",
        "bad request",
        "400",
        "invalid_request_error",
        "context_length_exceeded",
    ]

    @classmethod
    def is_retryable(cls, error: Exception) -> Tuple[bool, str]:
        """
        Returns (is_retryable: bool, reason: str).
        """
        err_msg = str(error).lower()
        err_type = type(error).__name__

        # Check for non-retryable first
        if any(keyword in err_msg for keyword in cls.NON_RETRYABLE_KEYWORDS):
            if "401" in err_msg or "invalid" in err_msg and "key" in err_msg:
                return False, "invalid_api_key"
            return False, "client_or_auth_error"

        # Model not found or deprecated endpoint on a specific provider (404)
        if "404" in err_msg or "not_found" in err_msg or "not found" in err_msg or "NotFoundError" in err_type:
            return True, "model_or_endpoint_not_found"

        # Check for retryable rate-limits and quotas
        if "429" in err_msg or "rate limit" in err_msg or "quota" in err_msg or "resource exhausted" in err_msg:
            return True, "rate_limit_or_quota"

        # Check for server or connection errors
        if any(keyword in err_msg for keyword in cls.RETRYABLE_KEYWORDS):
            return True, "server_or_network_error"

        # Check by exception type
        if "RateLimitError" in err_type:
            return True, "rate_limit_or_quota"
        if "Timeout" in err_type or "ConnectionError" in err_type or "APIConnectionError" in err_type:
            return True, "server_or_network_error"
        if "InternalServerError" in err_type:
            return True, "server_or_network_error"

        # Unknown errors default to non-retryable to prevent masking application bugs
        return False, "unknown_error"


# -----------------------------------------------------------------------------
# 3. Status Event Model
# -----------------------------------------------------------------------------
@dataclass
class ProviderStatusEvent:
    """User-facing event describing provider failover status."""
    type: str = "provider_status"
    status: str = "fallback"  # "fallback" or "switched"
    message: str = ""
    provider: str = ""


# -----------------------------------------------------------------------------
# 4. LLM Gateway Class
# -----------------------------------------------------------------------------
class LLMGateway:
    """
    Manages provider deployments, ordered fallback, and status events.
    """

    def __init__(self, max_attempts: int = 10, cooldown_seconds: int = 60):
        self.max_attempts = max_attempts
        self.cooldown_seconds = cooldown_seconds
        self.deployments: List[ProviderDeployment] = []
        self._initialize_deployments()

    def _initialize_deployments(self) -> None:
        """
        Load configured provider deployments using exact requested environment variables:
        - Gemini: GOOGLE_API_KEY1, GOOGLE_API_KEY2, GOOGLE_API_KEY3, GOOGLE_API_KEY4
        - Groq: GROQ_API_KEY
        - OpenAI: OPENAI_API_KEY
        - Mistral: MISTRAL_API_KEY
        - Cerebras: CEREBRAS_API_KEY
        """
        gemini_base = "https://generativelanguage.googleapis.com/v1beta/openai/"
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        gemini_fallback = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.6-flash")

        # 1. Gemini Deployments (4 Keys with Primary Lightweight Model)
        for i in range(1, 5):
            key = os.getenv(f"GOOGLE_API_KEY{i}")
            if key and key.strip():
                self.deployments.append(
                    ProviderDeployment(
                        name=f"Gemini #{i}",
                        provider="gemini",
                        api_key=key.strip(),
                        base_url=gemini_base,
                        default_model=gemini_model,
                        cooldown_seconds=self.cooldown_seconds,
                    )
                )

        # Gemini Higher-Quality Fallback (uses Primary Key if available)
        primary_google_key = os.getenv("GOOGLE_API_KEY1")
        if primary_google_key and primary_google_key.strip() and gemini_fallback:
            self.deployments.append(
                ProviderDeployment(
                    name="Gemini (Quality Fallback)",
                    provider="gemini",
                    api_key=primary_google_key.strip(),
                    base_url=gemini_base,
                    default_model=gemini_fallback,
                    cooldown_seconds=self.cooldown_seconds,
                )
            )

        # 2. Groq Deployments (Lightweight gpt-oss-20b + Quality Fallback gpt-oss-120b)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and groq_key.strip():
            groq_primary = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
            groq_fallback = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-120b")

            self.deployments.append(
                ProviderDeployment(
                    name="Groq",
                    provider="groq",
                    api_key=groq_key.strip(),
                    base_url="https://api.groq.com/openai/v1",
                    default_model=groq_primary,
                    cooldown_seconds=self.cooldown_seconds,
                )
            )
            if groq_fallback:
                self.deployments.append(
                    ProviderDeployment(
                        name="Groq (Quality Fallback)",
                        provider="groq",
                        api_key=groq_key.strip(),
                        base_url="https://api.groq.com/openai/v1",
                        default_model=groq_fallback,
                        cooldown_seconds=self.cooldown_seconds,
                    )
                )

        # 3. OpenAI Deployment
        openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        if openai_key and openai_key.strip():
            self.deployments.append(
                ProviderDeployment(
                    name="OpenAI",
                    provider="openai",
                    api_key=openai_key.strip(),
                    base_url=None,  # Standard OpenAI default
                    default_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    cooldown_seconds=self.cooldown_seconds,
                )
            )

        # 4. Mistral Deployment
        mistral_key = os.getenv("MISTRAL_API_KEY")
        if mistral_key and mistral_key.strip():
            self.deployments.append(
                ProviderDeployment(
                    name="Mistral",
                    provider="mistral",
                    api_key=mistral_key.strip(),
                    base_url="https://api.mistral.ai/v1",
                    default_model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
                    cooldown_seconds=self.cooldown_seconds,
                )
            )

        # 5. Cerebras Deployment
        cerebras_key = os.getenv("CEREBRAS_API_KEY")
        if cerebras_key and cerebras_key.strip():
            self.deployments.append(
                ProviderDeployment(
                    name="Cerebras",
                    provider="cerebras",
                    api_key=cerebras_key.strip(),
                    base_url="https://api.cerebras.ai/v1",
                    default_model=os.getenv("CEREBRAS_MODEL", "qwen-3.8-27b"),
                    cooldown_seconds=self.cooldown_seconds,
                )
            )

    def get_available_deployments(self) -> List[ProviderDeployment]:
        """Returns deployments that are configured and not in cooldown."""
        return [d for d in self.deployments if d.is_available]

    async def generate(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, str, str, Dict[str, int], List[ProviderStatusEvent]]:
        """
        Executes chat completion with automatic fallback across providers.
        Returns:
            (reply, provider_name, model_name, usage_dict, status_events)
        """
        available = self.get_available_deployments()

        # If all active deployments are cooling down, attempt the one cooling down the soonest
        if not available:
            active = [d for d in self.deployments if not d.is_permanently_disabled]
            if not active:
                raise RuntimeError("No LLM provider deployments configured or available.")
            active.sort(key=lambda d: d.cooldown_until)
            available = [active[0]]

        status_events: List[ProviderStatusEvent] = []
        attempts = 0
        last_error = None

        for deployment in available:
            if attempts >= self.max_attempts:
                break

            attempts += 1

            try:
                # Initialize LangChain ChatOpenAI for this deployment
                logger.info(
                    f"🌐 Connecting to Cloud LLM Provider: {deployment.name} ({deployment.default_model}) "
                    f"[Attempt {attempts}/{self.max_attempts}]..."
                )
                llm = ChatOpenAI(
                    api_key=deployment.api_key,
                    base_url=deployment.base_url,
                    model=deployment.default_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=30.0,
                )

                # Invoke the model asynchronously
                ai_response = await llm.ainvoke(messages)

                # If we had previous fallbacks, emit a "switched" event
                if len(status_events) > 0:
                    status_events.append(
                        ProviderStatusEvent(
                            type="provider_status",
                            status="switched",
                            message=f"Switched to {deployment.name} successfully.",
                            provider=deployment.name,
                        )
                    )

                # Extract token usage metadata safely
                usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                if hasattr(ai_response, "usage_metadata") and ai_response.usage_metadata:
                    m = ai_response.usage_metadata
                    usage["prompt_tokens"] = m.get("input_tokens", 0)
                    usage["completion_tokens"] = m.get("output_tokens", 0)
                    usage["total_tokens"] = m.get("total_tokens", 0)
                elif hasattr(ai_response, "response_metadata"):
                    tu = ai_response.response_metadata.get("token_usage", {})
                    usage["prompt_tokens"] = tu.get("prompt_tokens", 0)
                    usage["completion_tokens"] = tu.get("completion_tokens", 0)
                    usage["total_tokens"] = tu.get("total_tokens", 0)

                content = (
                    ai_response.content
                    if isinstance(ai_response.content, str)
                    else str(ai_response.content)
                )

                return content, deployment.name, deployment.default_model, usage, status_events

            except Exception as e:
                last_error = e
                is_retryable, reason = ErrorClassifier.is_retryable(e)

                if is_retryable:
                    if reason == "model_or_endpoint_not_found":
                        deployment.mark_disabled()
                        msg = f"{deployment.name} model '{deployment.default_model}' is unavailable. Switching to another provider..."
                        status_events.append(
                            ProviderStatusEvent(
                                type="provider_status",
                                status="fallback",
                                message=msg,
                                provider=deployment.name,
                            )
                        )
                        logger.warning(
                            f"⚠️ Fallback triggered for {deployment.name}: model '{deployment.default_model}' not found (404). "
                            f"Disabling and switching to next provider..."
                        )
                        continue
                    else:
                        # Put failed deployment on cooldown
                        deployment.mark_cooldown(self.cooldown_seconds)
                        msg = f"{deployment.name} has reached its current API limit or is unavailable. Switching to another provider..."
                        status_events.append(
                            ProviderStatusEvent(
                                type="provider_status",
                                status="fallback",
                                message=msg,
                                provider=deployment.name,
                            )
                        )
                        logger.warning(f"⚠️ Fallback triggered for {deployment.name}: {reason} ({str(e)})")
                        continue
                else:
                    # Non-retryable error on this specific provider (e.g. invalid key)
                    if reason == "invalid_api_key":
                        deployment.mark_disabled()
                        logger.error(f"⚠️ Permanently disabling {deployment.name} due to invalid API key. Falling back to next provider...")
                        status_events.append(
                            ProviderStatusEvent(
                                type="provider_status",
                                status="fallback",
                                message=f"{deployment.name} authentication failed. Switching to another provider...",
                                provider=deployment.name,
                            )
                        )
                        continue
                    raise e

        # If all attempts exhausted
        raise RuntimeError(
            f"All available LLM providers failed after {attempts} attempts. Last error: {str(last_error)}"
        )
