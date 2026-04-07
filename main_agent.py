"""CLI entry point for the production-ready Multi-LLM chat application."""

from __future__ import annotations

import logging
from typing import Optional

from llm_functions import get_system_prompt_from_user
from multi_ai_chat import MultiAIChatSession

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def display_responses(groq_response: str, openai_response: str, user_choice: int) -> None:
    """Display the selected model responses in the terminal."""
    if user_choice in (1, 3):
        logger.info("\nGroq:\n%s\n", groq_response or "No response returned.")
    if user_choice in (2, 3):
        logger.info("\nGPT-4o-mini:\n%s\n", openai_response or "No response returned.")


def prompt_for_choice(current_choice: int) -> Optional[int]:
    """Ask the user which model output they want to see next."""
    if current_choice == 3:
        logger.info("Select which response you prefer:")
        logger.info("1. Groq")
        logger.info("2. GPT-4o-mini")
        logger.info("3. Both")
        logger.info("4. Exit")
        selection_input = input("Select: ").strip().lower()
        if selection_input in {"exit", "4"}:
            return 4
        if selection_input in {"1", "2", "3"}:
            return int(selection_input)
        logger.warning("Invalid choice. Continuing with the previous selection.")
        return current_choice

    user_selection = input("Press Enter to continue, or type 4 to exit: ").strip().lower()
    if user_selection in {"4", "exit"}:
        return 4
    return current_choice


def main() -> None:
    """Run the interactive terminal chat loop."""
    logger.info("\nWelcome to the Multi-LLM chat application\n")
    system_prompt = get_system_prompt_from_user()
    session = MultiAIChatSession(system_prompt=system_prompt)
    user_choice = 3

    while True:
        user_query = input("\nYou: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            logger.info("Goodbye.")
            break
        if not user_query:
            logger.warning("Please enter a message or type 'exit'.")
            continue

        logger.info("\nFetching responses from AI...\n")
        try:
            groq_response, openai_response = session.get_responses(user_query, user_choice)
            display_responses(groq_response, openai_response, user_choice)
        except Exception as exc:
            logger.error("CLI chat request failed: %s", exc)

        next_choice = prompt_for_choice(user_choice)
        if next_choice == 4:
            logger.info("Session ended.")
            break
        user_choice = next_choice or user_choice


if __name__ == "__main__":
    main()