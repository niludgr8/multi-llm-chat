"""Reusable multi-model chat session orchestration for CLI and app usage."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from llm_functions import DEFAULT_SYSTEM_PROMPT, get_openai_response2, get_response_from_groq

logger = logging.getLogger(__name__)


@dataclass
class MultiAIChatSession:
    """Manage model-specific chat histories and fetch fresh responses."""

    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    groq_chat_history: List[Dict[str, str]] = field(default_factory=list)
    openai_chat_history: List[Dict[str, str]] = field(default_factory=list)

    def get_responses(self, user_query: str, user_choice: int = 3) -> Tuple[str, str]:
        """Fetch responses from the selected providers and update history."""
        groq_response = ""
        openai_response = ""

        if user_choice in (1, 3):
            groq_response = get_response_from_groq(user_query, self.groq_chat_history, self.system_prompt)
        if user_choice in (2, 3):
            openai_response = get_openai_response2(user_query, self.openai_chat_history, self.system_prompt)

        self._update_history(user_query, groq_response, openai_response, user_choice)
        logger.info("Updated multi-model session history for choice %s", user_choice)
        return groq_response, openai_response

    def _update_history(
        self,
        user_query: str,
        groq_response: str,
        openai_response: str,
        user_choice: int,
    ) -> None:
        """Persist the latest exchange into provider-specific chat histories."""
        if user_choice in (1, 3):
            self.groq_chat_history.append({"role": "user", "content": user_query})
            self.groq_chat_history.append({"role": "assistant", "content": groq_response})

        if user_choice in (2, 3):
            self.openai_chat_history.append({"role": "user", "content": user_query})
            self.openai_chat_history.append({"role": "assistant", "content": openai_response})
