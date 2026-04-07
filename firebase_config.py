"""Backward-compatible Firestore exports for the Streamlit app."""

from __future__ import annotations

import logging

from firebase_service import FirebaseDB, db, initialize_firebase

logger = logging.getLogger(__name__)

try:
    initialize_firebase()
except Exception as exc:
    logger.error("Firebase database bootstrap failed: %s", exc)

__all__ = ["FirebaseDB", "db", "initialize_firebase"]
