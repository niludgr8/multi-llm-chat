"""Production-ready Firebase auth and Firestore service layer."""

from __future__ import annotations

import base64
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import firebase_admin
import requests
import streamlit as st
from dotenv import load_dotenv
from firebase_admin import auth, credentials, firestore

load_dotenv()

logger = logging.getLogger(__name__)
DEFAULT_FIREBASE_FILE = os.getenv("FIREBASE_CREDENTIALS_PATH", "local-file.json")


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Read environment variables first, then fall back to Streamlit secrets."""
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    try:
        return st.secrets[key]
    except Exception:
        return default


def _load_firebase_credential() -> Optional[credentials.Certificate]:
    """Load Firebase Admin credentials from JSON text or a local file."""
    creds_json = get_secret("FIREBASE_CREDENTIALS")
    if creds_json:
        cleaned = creds_json.strip().lstrip("\ufeff")
        if not cleaned:
            logger.error("FIREBASE_CREDENTIALS is set but empty.")
            return None

        candidates = [cleaned]
        if cleaned.startswith(('"', "'")) and cleaned.endswith(('"', "'")):
            candidates.append(cleaned[1:-1])

        last_error: Optional[Exception] = None
        for candidate in candidates:
            try:
                creds_dict = json.loads(candidate)
                private_key = creds_dict.get("private_key")
                if isinstance(private_key, str):
                    creds_dict["private_key"] = private_key.replace("\\n", "\n")
                return credentials.Certificate(creds_dict)
            except json.JSONDecodeError as exc:
                last_error = exc
            except Exception as exc:
                logger.error("Failed to parse FIREBASE_CREDENTIALS: %s", exc)
                return None

        try:
            decoded = base64.b64decode(cleaned).decode("utf-8")
            creds_dict = json.loads(decoded)
            private_key = creds_dict.get("private_key")
            if isinstance(private_key, str):
                creds_dict["private_key"] = private_key.replace("\\n", "\n")
            return credentials.Certificate(creds_dict)
        except Exception:
            logger.error("FIREBASE_CREDENTIALS is not valid JSON: %s", last_error)
            return None

    local_file = get_secret("FIREBASE_CREDENTIALS_PATH", DEFAULT_FIREBASE_FILE)
    if not local_file or not os.path.exists(local_file):
        logger.warning("Firebase credentials file not found: %s", local_file)
        return None

    try:
        return credentials.Certificate(local_file)
    except Exception as exc:
        logger.error("Failed to load Firebase credentials from file %s: %s", local_file, exc)
        return None


def ensure_firebase_initialized() -> bool:
    """Ensure the Firebase Admin SDK is initialized before auth/database operations."""
    if firebase_admin._apps:
        return True

    client = initialize_firebase()
    return bool(firebase_admin._apps or client is not None)


@st.cache_resource(show_spinner=False)
def initialize_firebase() -> Optional[firestore.Client]:
    """Initialize Firebase once and return a Firestore client when available."""
    try:
        if firebase_admin._apps:
            return firestore.client()

        cred = _load_firebase_credential()
        if cred is None:
            logger.error("Firebase initialization skipped because no valid Admin credentials were found.")
            return None

        firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully")
        return firestore.client()
    except Exception as exc:
        logger.error("Firebase init failed: %s", exc)
        return None


db: Optional[firestore.Client] = None


class FirebaseAuth:
    """Firebase Authentication operations used by the Streamlit app."""

    @staticmethod
    def sign_up(email: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Firebase Authentication user."""
        api_key = get_secret("FIREBASE_WEB_API_KEY")
        if not api_key:
            message = "FIREBASE_WEB_API_KEY is not configured."
            logger.error(message)
            return {"success": False, "user_id": None, "message": message}

        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            user_id = data.get("localId")

            if ensure_firebase_initialized() and user_id:
                try:
                    auth.update_user(user_id, display_name=display_name or email.split("@")[0])
                except Exception as exc:
                    logger.warning("Unable to update Firebase display name for %s: %s", user_id, exc)

            logger.info("Firebase user created successfully: %s", user_id)
            return {
                "success": True,
                "user_id": user_id,
                "message": "Account created successfully.",
                "email": data.get("email", email),
                "display_name": display_name or email.split("@")[0],
            }
        except requests.HTTPError:
            error_payload = response.json() if response.content else {}
            firebase_message = (
                error_payload.get("error", {}).get("message", "") if isinstance(error_payload, dict) else ""
            )
            normalized = firebase_message.upper()
            if normalized == "EMAIL_EXISTS":
                message = "Email already exists. Please use a different email."
            elif normalized == "INVALID_EMAIL":
                message = "Invalid email format."
            elif normalized in {"WEAK_PASSWORD : PASSWORD SHOULD BE AT LEAST 6 CHARACTERS", "WEAK_PASSWORD"}:
                message = "Password is too weak. Please use at least 6 characters."
            elif normalized == "PASSWORD_LOGIN_DISABLED":
                message = "Email/password sign-in is disabled in Firebase Console. Enable it under Authentication > Sign-in method."
            else:
                message = f"Error creating account: {firebase_message or response.text}"
            logger.error("Firebase sign-up failed: %s", response.text)
            return {"success": False, "user_id": None, "message": message}
        except requests.RequestException as exc:
            logger.error("Firebase sign-up request failed: %s", exc)
            return {
                "success": False,
                "user_id": None,
                "message": "Authentication service is temporarily unavailable.",
            }

    @staticmethod
    def verify_email(email: str, password: str) -> Dict[str, Any]:
        """Verify user credentials against Firebase Identity Toolkit."""
        api_key = get_secret("FIREBASE_WEB_API_KEY")
        if not api_key:
            logger.error("FIREBASE_WEB_API_KEY is not configured.")
            return {
                "success": False,
                "user_id": None,
                "message": "Authentication service is not configured.",
            }

        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}

        try:
            response = requests.post(endpoint, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            logger.info("Firebase login successful for %s", email)
            return {
                "success": True,
                "user_id": data.get("localId"),
                "message": "Login successful.",
                "email": data.get("email", email),
            }
        except requests.HTTPError:
            error_payload = response.json() if response.content else {}
            firebase_message = (
                error_payload.get("error", {}).get("message", "") if isinstance(error_payload, dict) else ""
            )
            logger.error("Firebase login rejected for %s: %s", email, response.text)
            if firebase_message == "PASSWORD_LOGIN_DISABLED":
                return {
                    "success": False,
                    "user_id": None,
                    "message": "Email/password sign-in is disabled in Firebase Console. Enable it under Authentication > Sign-in method.",
                }
            return {"success": False, "user_id": None, "message": "Invalid email or password."}
        except requests.RequestException as exc:
            logger.error("Firebase login request failed: %s", exc)
            return {
                "success": False,
                "user_id": None,
                "message": "Authentication service is temporarily unavailable.",
            }

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Firebase user by email address."""
        try:
            if not ensure_firebase_initialized():
                logger.error("Firebase is not initialized; cannot get user by email.")
                return None

            user = auth.get_user_by_email(email)
            return {
                "user_id": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "created_at": user.user_metadata.creation_timestamp,
                "last_sign_in": user.user_metadata.last_sign_in_timestamp,
            }
        except Exception as exc:
            logger.error("Error retrieving Firebase user by email: %s", exc)
            return None

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Firebase user by UID."""
        try:
            if not ensure_firebase_initialized():
                logger.error("Firebase is not initialized; cannot get user by id.")
                return None

            user = auth.get_user(user_id)
            return {
                "user_id": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "created_at": user.user_metadata.creation_timestamp,
                "last_sign_in": user.user_metadata.last_sign_in_timestamp,
            }
        except Exception as exc:
            logger.error("Error retrieving Firebase user by id: %s", exc)
            return None

    @staticmethod
    def update_user_profile(user_id: str, display_name: Optional[str] = None, email: Optional[str] = None) -> bool:
        """Update the display name and/or email for a Firebase user."""
        try:
            update_data: Dict[str, str] = {}
            if display_name:
                update_data["display_name"] = display_name
            if email:
                update_data["email"] = email
            if not update_data:
                return False
            auth.update_user(user_id, **update_data)
            logger.info("Firebase user updated successfully: %s", user_id)
            return True
        except Exception as exc:
            logger.error("Error updating Firebase user %s: %s", user_id, exc)
            return False

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete a Firebase Authentication user."""
        try:
            auth.delete_user(user_id)
            logger.info("Firebase user deleted successfully: %s", user_id)
            return True
        except Exception as exc:
            logger.error("Error deleting Firebase user %s: %s", user_id, exc)
            return False


class FirebaseDB:
    """Firestore CRUD operations for user profiles and chat history."""

    @staticmethod
    def _client() -> Optional[firestore.Client]:
        """Return a live Firestore client, if available."""
        global db
        db = initialize_firebase()
        return db

    @staticmethod
    def create_user(user_id: str, email: str, name: str) -> bool:
        """Create or update the user profile document in Firestore."""
        client = FirebaseDB._client()
        if client is None:
            logger.warning("Skipping user creation because Firebase is unavailable.")
            return False

        try:
            now = datetime.now(timezone.utc)
            user_data = {
                "email": email,
                "name": name,
                "created_at": now,
                "last_login": now,
                "status": "active",
            }
            client.collection("users").document(user_id).set(user_data, merge=True)
            logger.info("Firestore user profile saved for %s", user_id)
            return True
        except Exception as exc:
            logger.error("Error creating user profile for %s: %s", user_id, exc)
            return False

    @staticmethod
    def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a Firestore user profile by UID."""
        client = FirebaseDB._client()
        if client is None:
            return None

        try:
            doc = client.collection("users").document(user_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as exc:
            logger.error("Error retrieving Firestore user %s: %s", user_id, exc)
            return None

    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing Firestore user profile."""
        client = FirebaseDB._client()
        if client is None:
            return False

        try:
            update_data["last_updated"] = datetime.now(timezone.utc)
            client.collection("users").document(user_id).set(update_data, merge=True)
            logger.info("Firestore user updated successfully: %s", user_id)
            return True
        except Exception as exc:
            logger.error("Error updating Firestore user %s: %s", user_id, exc)
            return False

    @staticmethod
    def save_chat_message(
        user_id: str,
        user_query: str,
        groq_response: str,
        openai_response: str,
        choice: int,
        openai_rating: Optional[int] = None,
        gemini_rating: Optional[int] = None,
    ) -> bool:
        """Persist a chat interaction to Firestore."""
        client = FirebaseDB._client()
        if client is None:
            logger.warning("Skipping chat save because Firebase is unavailable.")
            return False

        try:
            now = datetime.now(timezone.utc)
            chat_data = {
                "user_query": user_query,
                "groq_response": groq_response,
                "openai_response": openai_response,
                "gemini_response": openai_response,
                "user_choice": choice,
                "timestamp": now,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "openai_rating": openai_rating,
                "gemini_rating": gemini_rating,
            }
            chat_data = {key: value for key, value in chat_data.items() if value is not None}
            client.collection("users").document(user_id).collection("chat_history").add(chat_data)
            logger.info("Chat message saved for user %s", user_id)
            return True
        except Exception as exc:
            logger.error("Error saving chat message for %s: %s", user_id, exc)
            return False

    @staticmethod
    def get_user_chat_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the user's chat history sorted in chronological order."""
        client = FirebaseDB._client()
        if client is None:
            return []

        try:
            docs = (
                client.collection("users")
                .document(user_id)
                .collection("chat_history")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )

            chat_history: List[Dict[str, Any]] = []
            for doc in docs:
                chat_data = doc.to_dict()
                chat_data["id"] = doc.id
                chat_history.append(chat_data)

            chat_history.reverse()
            return chat_history
        except Exception as exc:
            logger.error("Error retrieving chat history for %s: %s", user_id, exc)
            return []

    @staticmethod
    def clear_user_chat_history(user_id: str) -> bool:
        """Delete all chat messages for a given user."""
        client = FirebaseDB._client()
        if client is None:
            return False

        try:
            docs = client.collection("users").document(user_id).collection("chat_history").stream()
            for doc in docs:
                doc.reference.delete()
            logger.info("Chat history cleared for user %s", user_id)
            return True
        except Exception as exc:
            logger.error("Error clearing chat history for %s: %s", user_id, exc)
            return False

    @staticmethod
    def get_chat_statistics(user_id: str) -> Dict[str, Any]:
        """Get aggregate chat statistics for a user."""
        client = FirebaseDB._client()
        if client is None:
            return {"total_messages": 0, "last_interaction": None}

        try:
            collection = client.collection("users").document(user_id).collection("chat_history")
            total_messages = len(list(collection.stream()))
            last_doc = list(
                collection.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).stream()
            )
            return {
                "total_messages": total_messages,
                "last_interaction": last_doc[0].to_dict().get("timestamp") if last_doc else None,
            }
        except Exception as exc:
            logger.error("Error getting chat statistics for %s: %s", user_id, exc)
            return {"total_messages": 0, "last_interaction": None}
