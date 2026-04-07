# Firebase and Multi-LLM Integration Guide

## Overview
This guide explains how to connect your Multi-LLM Chat application with Firebase for authentication and data storage.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (Streamlit)                │
│                    (app.py)                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Firebase     │  │ Firebase     │  │ LLM          │
│ Auth         │  │ Config       │  │ Functions    │
│ (firebase_   │  │ (firebase_   │  │ (llm_       │
│ auth.py)     │  │ config.py)   │  │ functions.py)│
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────────┐        ┌──────────────────────┐
│  Firebase Services   │        │   External APIs      │
│  ┌────────────────┐  │        │ ┌────────────────┐   │
│  │ Authentication │  │        │ │ OpenAI API     │   │
│  │ Firestore DB   │  │        │ │ Google Gemini  │   │
│  │ Cloud Storage  │  │        │ └────────────────┘   │
│  └────────────────┘  │        └──────────────────────┘
└──────────────────────┘
```

## Step-by-Step Integration

### Step 1: Firebase Authentication Setup

#### Create User Accounts
```python
from firebase_auth import FirebaseAuth

# Sign up new user
result = FirebaseAuth.sign_up(
    email="user@example.com",
    password="SecurePassword123",
    display_name="John Doe"
)

if result['success']:
    user_id = result['user_id']
    print(f"User created: {user_id}")
else:
    print(f"Error: {result['message']}")
```

#### Retrieve User Information
```python
# Get user by email
user_info = FirebaseAuth.get_user_by_email("user@example.com")

# Get user by ID
user_info = FirebaseAuth.get_user_by_id("user_id_12345")
```

### Step 2: Create User in Firestore

After Firebase Authentication creates a user, create their Firestore document:

```python
from firebase_config import FirebaseDB

# Create user document in Firestore
FirebaseDB.create_user(
    user_id="user_id_12345",
    email="user@example.com",
    name="John Doe"
)
```

**Firestore Document Structure:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": timestamp,
  "last_login": timestamp,
  "status": "active"
}
```

### Step 3: Store Chat Messages

When users send messages, save them to their chat history:

```python
# Save chat interaction
FirebaseDB.save_chat_message(
    user_id="user_id_12345",
    user_query="What is artificial intelligence?",
    openai_response="AI is a field of computer science...",
    gemini_response="Artificial Intelligence refers to...",
    choice=3  # 1=OpenAI, 2=Gemini, 3=Both
)
```

**Saved Document Structure:**
```json
{
  "user_query": "What is artificial intelligence?",
  "openai_response": "AI is a field of computer science...",
  "gemini_response": "Artificial Intelligence refers to...",
  "user_choice": 3,
  "timestamp": "2026-02-22T19:40:47",
  "date": "2026-02-22",
  "time": "19:40:47"
}
```

### Step 4: Retrieve Chat History

Get a user's chat history from Firestore:

```python
# Get last 50 chat messages
chat_history = FirebaseDB.get_user_chat_history(
    user_id="user_id_12345",
    limit=50
)

# Get recent messages (for context)
recent_messages = FirebaseDB.get_recent_chat_messages(
    user_id="user_id_12345",
    num_messages=10
)
```

### Step 5: Get Chat Statistics

```python
stats = FirebaseDB.get_chat_statistics(user_id="user_id_12345")

print(f"Total messages: {stats['total_messages']}")
print(f"Last interaction: {stats['last_interaction']}")
```

## Data Flow Diagram

### Sign-Up Flow
```
User fills signup form
        │
        ▼
Validate inputs
        │
        ▼
FirebaseAuth.sign_up()
        │
        ├─ Create user in Firebase Auth
        │
        ▼
FirebaseDB.create_user()
        │
        ├─ Create user document in Firestore
        │
        ▼
User account created ✓
```

### Chat Flow
```
User sends message
        │
        ▼
Get LLM responses (OpenAI/Gemini)
        │
        ▼
FirebaseDB.save_chat_message()
        │
        ├─ Add chat document to chat_history subcollection
        │
        ▼
Show response to user
        │
        ▼
Load updated chat history
        │
        ▼
Display in UI ✓
```

## Complete Example: Full Chat Session

```python
from firebase_auth import FirebaseAuth
from firebase_config import FirebaseDB
from llm_functions import get_response_from_openai, get_gemini_response

# 1. User Sign-Up
signup_result = FirebaseAuth.sign_up(
    email="alice@example.com",
    password="SecurePass123",
    display_name="Alice"
)

if not signup_result['success']:
    print(f"Sign-up failed: {signup_result['message']}")
    exit()

user_id = signup_result['user_id']

# 2. Create user in Firestore
FirebaseDB.create_user(
    user_id=user_id,
    email="alice@example.com",
    name="Alice"
)

# 3. Get responses from LLMs
user_query = "Tell me about machine learning"

openai_response = get_response_from_openai(user_query, [])
gemini_response = get_gemini_response(user_query, [])

# 4. Save chat message to Firestore
FirebaseDB.save_chat_message(
    user_id=user_id,
    user_query=user_query,
    openai_response=openai_response,
    gemini_response=gemini_response,
    choice=3
)

# 5. Display responses to user
print(f"OpenAI: {openai_response}")
print(f"Gemini: {gemini_response}")

# 6. Retrieve and display chat history
chat_history = FirebaseDB.get_user_chat_history(user_id)

print("\n--- Chat History ---")
for msg in chat_history:
    print(f"You: {msg['user_query']}")
    print(f"OpenAI: {msg['openai_response']}")
    print(f"Gemini: {msg['gemini_response']}")
    print("---")

# 7. Get statistics
stats = FirebaseDB.get_chat_statistics(user_id)
print(f"\nTotal messages: {stats['total_messages']}")
```

## Database Schema

### Collections

#### `users` Collection
| Field | Type | Description |
|-------|------|-------------|
| email | String | User's email address |
| name | String | User's display name |
| created_at | Timestamp | Account creation time |
| last_login | Timestamp | Last login timestamp |
| status | String | User status (active/inactive) |

#### `chat_history` Subcollection (under each user)
| Field | Type | Description |
|-------|------|-------------|
| user_query | String | User's input text |
| openai_response | String | Response from OpenAI |
| gemini_response | String | Response from Gemini |
| user_choice | Integer | LLM choice (1/2/3) |
| timestamp | Timestamp | Message creation time |
| date | String | Message date (YYYY-MM-DD) |
| time | String | Message time (HH:MM:SS) |

## Error Handling

```python
try:
    # Create user
    result = FirebaseAuth.sign_up("user@example.com", "pass", "name")
    
    if not result['success']:
        print(f"Error: {result['message']}")
        # Handle specific errors
        if "already exists" in result['message']:
            # User already registered
            pass
        elif "weak password" in result['message']:
            # Password too weak
            pass
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Always validate user input** before saving to Firebase
2. **Use try-except blocks** for all Firebase operations
3. **Check return values** before proceeding with operations
4. **Implement rate limiting** for chat messages
5. **Regularly backup** user data
6. **Use security rules** to protect user data
7. **Never store sensitive information** in plain text

## Security Rules for Firestore

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own documents
    match /users/{userId} {
      allow read, create, update, delete: if request.auth.uid == userId;
      
      // Users can access their own chat history
      match /chat_history/{document=**} {
        allow read, create, delete: if request.auth.uid == userId;
      }
    }
  }
}
```

## Testing Your Integration

```bash
# Test Firebase configuration
python firebase_config.py

# Test Firebase authentication
python firebase_auth.py

# Test full integration
python test_firebase.py

# Run web application
streamlit run app.py
```

## Troubleshooting Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| User not found | Email doesn't exist in Firebase | Check email spelling, sign up if new user |
| Chat not saving | User ID mismatch | Ensure user is created in Firestore after auth signup |
| Permission denied | Security rules too restrictive | Update Firestore security rules |
| API quota exceeded | Too many requests | Implement rate limiting, upgrade plan |
| Document not found | Chat history empty | Check that save_chat_message was called |

## Next Steps

1. Deploy application to production
2. Set up automated backups
3. Implement monitoring and logging
4. Add user preferences and settings
5. Create admin dashboard
6. Implement real-time chat
7. Add email notifications

## Support Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Python SDK](https://firebase.google.com/docs/firestore/client/start-python)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [OpenAI API](https://platform.openai.com/docs)
- [Google Generative AI](https://ai.google.dev)
