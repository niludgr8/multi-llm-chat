"""Backward-compatible Firebase authentication exports for the app."""

from __future__ import annotations

import logging

from firebase_service import FirebaseAuth, initialize_firebase

logger = logging.getLogger(__name__)

try:
    initialize_firebase()
except Exception as exc:
    logger.error("Firebase authentication bootstrap failed: %s", exc)

__all__ = ["FirebaseAuth", "initialize_firebase"]

