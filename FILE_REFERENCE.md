# 📚 Project File Reference Guide

## Project Structure Reference

### Core Application Files

#### **app.py** - Streamlit Web Application
- **Purpose**: Main web interface for the Multi-LLM Chat application
- **Features**:
  - Login/Sign-up interface with Firebase Auth
  - Real-time chat interface
  - Dual LLM support (OpenAI & Gemini)
  - Chat history viewer
  - User statistics dashboard
  - Session management
- **How to run**: `streamlit run app.py`
- **Key Functions**:
  - `login_user()` - Handle user login
  - `signup_user()` - Handle user registration
  - `logout_user()` - Handle logout
  - `display_chat_interface()` - Show main chat UI
  - `display_auth_page()` - Show login/signup UI

---

#### **main_agent.py** - Console-Based Chat Application
- **Purpose**: Command-line interface for the Multi-LLM Chat application
- **Features**:
  - LLM selection (OpenAI, Gemini, or both)
  - Real-time message input and processing
  - Response comparison
  - Exit functionality with error handling
- **How to run**: `python main_agent.py`
- **Key Functions**:
  - `main()` - Main application loop
  - `display_responses()` - Show LLM responses
  - `update_history()` - Update chat history

---

### Authentication & Database Modules

#### **firebase_auth.py** - Firebase Authentication Module
- **Purpose**: Handle all user authentication operations with Firebase
- **Features**:
  - User sign-up with validation
  - User login verification
  - User profile retrieval and updates
  - User deletion
  - Password reset support
  - List all users (admin)
- **Key Functions**:
  - `sign_up(email, password, display_name)` - Create new account
  - `get_user_by_email(email)` - Find user by email
  - `get_user_by_id(user_id)` - Find user by ID
  - `update_user_profile(user_id, display_name, email)` - Update profile
  - `delete_user(user_id)` - Delete account
  - `reset_password(email)` - Send reset email
  - `list_all_users(max_users)` - Admin function

---

#### **firebase_config.py** - Firestore Database Module
- **Purpose**: Handle all database operations with Firestore
- **Features**:
  - User document creation and management
  - Chat message storage with timestamps
  - Chat history retrieval and management
  - Chat statistics and analytics
  - Subcollection support for chat_history
- **Key Functions**:
  - `create_user(user_id, email, name)` - Create user document
  - `get_user(user_id)` - Retrieve user data
  - `update_user(user_id, update_data)` - Update user info
  - `save_chat_message(...)` - Store chat interaction
  - `get_user_chat_history(user_id, limit)` - Get all messages
  - `get_recent_chat_messages(user_id, num_messages)` - Get recent messages
  - `delete_chat_message(user_id, message_id)` - Delete message
  - `clear_user_chat_history(user_id)` - Clear all messages
  - `get_chat_statistics(user_id)` - Get user stats

---

### LLM Integration

#### **llm_functions.py** - LLM Integration Module
- **Purpose**: Integration with OpenAI and Google Generative AI
- **Features**:
  - OpenAI GPT-4 integration
  - Google Gemini integration
  - Chat history management for each model
  - System prompts for sales AI
- **Key Functions**:
  - `get_response_from_openai(user_query, chat_history)` - Get OpenAI response
  - `get_gemini_response(user_query, chat_history)` - Get Gemini response

---

#### **ai_functions.py** - Additional AI Utilities
- **Purpose**: Additional AI-related helper functions
- **Status**: Available for extension

---

### Testing & Setup Files

#### **test_firebase.py** - Firebase Integration Tests
- **Purpose**: Comprehensive Firebase functionality testing
- **Tests Included**:
  1. Write Test - Document creation
  2. Read Test - Document retrieval
  3. Update Test - Document modification
  4. Read After Update - Verification
  5. List Documents - Collection browsing
- **How to run**: `python test_firebase.py`
- **Expected Output**: All 5/5 tests passed ✓

---

#### **create_test_doc.py** - Test Document Creator
- **Purpose**: Create sample documents for testing
- **Creates**: Sample test document in 'testing' collection
- **How to run**: `python create_test_doc.py`

---

#### **firebase_setup.md** - Firebase Setup Guide
- **Purpose**: Step-by-step Firebase configuration guide
- **Covers**:
  - Google Cloud project creation
  - Firebase initialization
  - Firestore database setup
  - Firebase Authentication setup
  - Admin SDK key generation
  - Python integration code
  - Collection structure setup
  - Security best practices

---

### Documentation Files

#### **README.md** - Main Project Documentation
- **Contents**:
  - Project overview and features
  - Installation instructions
  - Usage examples (web and console)
  - Module descriptions
  - Firestore data structure
  - Testing information
  - Security considerations
  - Troubleshooting guide
  - Future enhancements

---

#### **QUICKSTART.md** - Quick Start Guide
- **Purpose**: Get running in 5 minutes
- **Contents**:
  - Prerequisites
  - Step-by-step setup
  - Common commands
  - First-time checklist
  - Troubleshooting tips
  - API key setup instructions

---

#### **INTEGRATION_GUIDE.md** - Firebase Integration Tutorial
- **Purpose**: Complete integration guide with examples
- **Contents**:
  - Architecture diagrams
  - Step-by-step integration
  - Data flow diagrams
  - Complete code examples
  - Database schema details
  - Error handling patterns
  - Best practices
  - Security rules

---

#### **SETUP_SUMMARY.md** - Setup Completion Summary
- **Purpose**: Overview of completed tasks
- **Contents**:
  - Completed tasks checklist
  - Files created/updated
  - Architecture overview
  - Usage instructions
  - Test results
  - Feature summary
  - Next steps

---

### Configuration Files

#### **.env** - Environment Variables
- **Purpose**: Store API keys and sensitive information
- **Variables Required**:
  ```env
  OPENAI_API_KEY=sk-...
  GEMINI_API_KEY=gsk-...
  GOOGLE_APPLICATION_CREDENTIALS=./firebase-key.json
  ```
- **Security**: Never commit to version control

---

#### **requirements.txt** - Python Dependencies
- **Contains**: All required Python packages
- **Key Packages**:
  - firebase-admin>=6.0.0
  - google-cloud-firestore>=2.11.0
  - google-generativeai
  - openai
  - python-dotenv
  - streamlit>=1.28.0

---

#### **multi-llm-chat-4bf66-firebase-adminsdk-fbsvc-572c6a8d90.json**
- **Purpose**: Firebase Admin SDK credentials
- **Usage**: Authenticates with Firebase backend
- **Security**: Never commit to version control, keep in root only

---

#### **client_secret_*.json**
- **Purpose**: Google OAuth credentials
- **Usage**: Google authentication integration
- **Security**: Never share or commit to version control

---

### Project Planning & Documentation

#### **planning.txt** - Project Planning Document
- **Purpose**: Overall project requirements and goals
- **Tracks**: Firebase setup, authentication, database structure

---

#### **word_counter.py** - Utility Script
- **Purpose**: Word counting utility
- **Status**: Optional utility

---

## File Dependencies Map

```
app.py (Streamlit Web App)
├── firebase_auth.py
│   └── firebase_admin
│
├── firebase_config.py
│   └── firebase_admin
│
└── llm_functions.py
    ├── openai
    └── google.generativeai

main_agent.py (Console App)
├── firebase_config.py (optional)
│
└── llm_functions.py
    ├── openai
    └── google.generativeai

firebase_auth.py
└── firebase_admin

firebase_config.py
└── firebase_admin

llm_functions.py
├── openai
└── google.generativeai

test_firebase.py
├── firebase_config.py
└── firebase_admin

create_test_doc.py
├── firebase_config.py
└── firebase_admin
```

## Module Usage Examples

### Authentication Flow
```python
# In app.py
from firebase_auth import FirebaseAuth
from firebase_config import FirebaseDB

# Sign up
result = FirebaseAuth.sign_up(email, password, name)
if result['success']:
    FirebaseDB.create_user(result['user_id'], email, name)
```

### Chat Message Flow
```python
# In app.py
from firebase_config import FirebaseDB
from llm_functions import get_gemini_response, get_response_from_openai

# Get responses
openai_resp = get_response_from_openai(query, [])
gemini_resp = get_gemini_response(query, [])

# Save to database
FirebaseDB.save_chat_message(user_id, query, openai_resp, gemini_resp, choice)

# Retrieve history
history = FirebaseDB.get_user_chat_history(user_id)
```

## Directory Organization

```
LLM Project/
│
├── Application Files
│   ├── app.py                    [Streamlit Web App]
│   └── main_agent.py             [Console App]
│
├── Core Modules
│   ├── firebase_auth.py          [Authentication]
│   ├── firebase_config.py        [Database]
│   └── llm_functions.py          [LLM Integration]
│
├── Testing
│   ├── test_firebase.py
│   └── create_test_doc.py
│
├── Configuration
│   ├── .env                      [API Keys & Secrets]
│   ├── requirements.txt
│   └── *.json                    [Firebase & OAuth]
│
└── Documentation
    ├── README.md
    ├── firebase_setup.md
    ├── QUICKSTART.md
    ├── INTEGRATION_GUIDE.md
    └── SETUP_SUMMARY.md
```

## Quick Reference

### Run Web Application
```bash
streamlit run app.py
```

### Run Console Application
```bash
python main_agent.py
```

### Test Database
```bash
python test_firebase.py
```

### View Documentation
- Main docs: `README.md`
- Quick start: `QUICKSTART.md`
- Integration: `INTEGRATION_GUIDE.md`
- Setup info: `SETUP_SUMMARY.md`
- Firebase: `firebase_setup.md`

---

For more information, start with [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md).
