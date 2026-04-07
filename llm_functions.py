"""Production-ready LLM helpers for Groq and OpenAI requests."""

from __future__ import annotations

import logging
import os
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from httpx import TimeoutException
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama3-8b-8192"
OPENAI_MODEL = "gpt-4o-mini"
REQUEST_TIMEOUT = 30
MAX_QUERY_LENGTH = 5000
MAX_HISTORY_MESSAGES = 10
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant."
SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT
T = TypeVar("T")


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Read secrets from Streamlit first, then environment variables."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)


@st.cache_resource(show_spinner=False)
def get_groq_client() -> Optional[Groq]:
    """Create and cache the Groq client."""
    api_key = get_secret("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY is not configured.")
        return None

    try:
        return Groq(api_key=api_key)
    except Exception as exc:
        logger.error("Failed to initialize Groq client: %s", exc)
        return None


@st.cache_resource(show_spinner=False)
def get_openai_client() -> Optional[OpenAI]:
    """Create and cache the OpenAI client."""
    api_key = get_secret("OPENAI_API_KEY") or get_secret("OPENAI_API_KEY2")
    if not api_key:
        logger.warning("OPENAI_API_KEY is not configured.")
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception as exc:
        logger.error("Failed to initialize OpenAI client: %s", exc)
        return None


def _trim_chat_history(chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Limit conversation context to the most recent messages."""
    return chat_history[-MAX_HISTORY_MESSAGES:]


def retry_api_call(func: Callable[..., str]) -> Callable[..., str]:
    """Retry transient API failures up to three times with a short delay."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        last_error: Optional[Exception] = None

        for attempt in range(1, 4):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                last_error = exc
                is_timeout = isinstance(exc, (TimeoutException, TimeoutError)) or "timeout" in str(exc).lower()
                log_message = "Request timed out" if is_timeout else "Request failed"
                logger.warning("%s in %s (attempt %s/3): %s", log_message, func.__name__, attempt, exc)

                if attempt < 3:
                    time.sleep(1)
                    continue

                logger.error("%s failed after retries: %s", func.__name__, exc)
                if is_timeout:
                    return "The request timed out after multiple attempts. Please try again."
                return "The AI service is temporarily unavailable right now. Please try again in a moment."

        logger.error("Unexpected retry exit for %s: %s", func.__name__, last_error)
        return "The AI service is temporarily unavailable right now. Please try again in a moment."

    return wrapper


def get_system_prompt_from_user() -> str:
    """Prompt the CLI user for an optional custom system prompt."""
    logger.info("\n=== System Prompt Configuration ===")
    logger.info("Enter a custom system prompt for the AI assistant.")
    logger.info("Press Enter to use the default helper prompt.\n")

    user_input = input("System Prompt: ").strip()
    if user_input:
        logger.info("Using custom system prompt.\n")
        return user_input

    logger.info("Using default system prompt.\n")
    return DEFAULT_SYSTEM_PROMPT


@retry_api_call
def get_response_from_groq(
    user_query: str,
    groq_chat_history: List[Dict[str, str]],
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> str:
    """Get a response from Groq with timeout protection and bounded context."""
    client = get_groq_client()
    if client is None:
        return "Error: Groq API is not configured. Please add GROQ_API_KEY."

    if not user_query or len(user_query) > MAX_QUERY_LENGTH:
        return f"Error: Query must be between 1 and {MAX_QUERY_LENGTH} characters."

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(_trim_chat_history(groq_chat_history))
    messages.append({"role": "user", "content": user_query})

    logger.info("Sending Groq request with %s context messages.", len(messages) - 1)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
        timeout=REQUEST_TIMEOUT,
    )

    content = completion.choices[0].message.content or "No response returned from Groq."
    return content.strip()


@retry_api_call
def get_openai_response2(
    user_query: str,
    chat_history: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
) -> str:
    """Get a response from OpenAI with timeout protection and bounded context."""
    client = get_openai_client()
    if client is None:
        return "Error: OpenAI API is not configured. Please add OPENAI_API_KEY."

    if not user_query or len(user_query) > MAX_QUERY_LENGTH:
        return f"Error: Query must be between 1 and {MAX_QUERY_LENGTH} characters."

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt or SYSTEM_PROMPT}]
    messages.extend(_trim_chat_history(chat_history))
    messages.append({"role": "user", "content": user_query})

    logger.info("Sending OpenAI request with %s context messages.", len(messages) - 1)
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
        timeout=REQUEST_TIMEOUT,
    )

    content = completion.choices[0].message.content or "No response returned from OpenAI."
    return content.strip()

