"""Health check utility for validating external service connectivity."""

from __future__ import annotations

import sys
from typing import Callable, List, Tuple

from firebase_service import initialize_firebase
from llm_functions import GROQ_MODEL, OPENAI_MODEL, get_groq_client, get_openai_client


def check_groq() -> bool:
    """Verify the Groq API can complete a minimal request."""
    client = get_groq_client()
    if client is None:
        return False

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "Reply with OK"}],
            temperature=0,
            max_tokens=5,
            timeout=15,
        )
        return bool(response.choices[0].message.content)
    except Exception:
        return False


def check_openai() -> bool:
    """Verify the OpenAI API can complete a minimal request."""
    client = get_openai_client()
    if client is None:
        return False

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": "Reply with OK"}],
            temperature=0,
            max_tokens=5,
            timeout=15,
        )
        return bool(response.choices[0].message.content)
    except Exception:
        return False


def check_firebase() -> bool:
    """Verify Firebase can initialize and return a Firestore client."""
    client = initialize_firebase()
    return client is not None


def main() -> int:
    """Run all health checks and return a process exit code."""
    checks: List[Tuple[str, Callable[[], bool]]] = [
        ("Groq API", check_groq),
        ("OpenAI API", check_openai),
        ("Firebase", check_firebase),
    ]

    all_passed = True
    for label, check in checks:
        passed = check()
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
        all_passed = all_passed and passed

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
