# Firebase Setup Guide for Multi-LLM Chat Application

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click **NEW PROJECT**
4. Enter a project name (e.g., "Multi-LLM-Chat")
5. Select your organization (or leave as default)
6. Click **CREATE**
7. Wait for the project to be created (this may take a minute)

## Step 2: Enable Firebase in Your Project

1. In the Google Cloud Console, make sure your new project is selected
2. Go to [Firebase Console](https://console.firebase.google.com/)
3. Click **Add project**
4. Select your Google Cloud Project from the dropdown
5. Click **Continue**
6. Enable Google Analytics (optional, click **Enable** or **Skip**)
7. Click **Create project**
8. Wait for Firebase to initialize your project

## Step 3: Set Up Firestore Database

1. In Firebase Console, click on **Firestore Database** in the left sidebar
2. Click **Create database**
3. Choose your database location (select the one closest to you)
4. Select **Start in test mode** (for development)
   - **Note:** Switch to production mode before deploying to production
5. Click **Create**
6. Firestore will initialize (wait for it to complete)

## Step 4: Set Up Firebase Authentication

1. In Firebase Console, click on **Authentication** in the left sidebar
2. Click on the **Sign-in method** tab
3. Click **Email/Password**
4. Enable both **Email/Password** and **Email link (passwordless sign-in)**
5. Click **Save**

## Step 5: Generate Firebase Admin SDK Key

1. In Firebase Console, click on **Project Settings** (gear icon) at the top
2. Go to the **Service Accounts** tab
3. Click **Generate New Private Key**
4. Save the downloaded JSON file securely in your project directory
   - Name it: `firebase-adminsdk.json` (or your preferred name)
   - **Keep this file secure and never commit it to public repositories**

## Step 6: Install Firebase SDKs

Add the following to your `requirements.txt` (if not already there):

```
firebase-admin>=6.0.0
google-cloud-firestore>=2.11.0
google-cloud-storage>=2.10.0
```

Install the packages:
```bash
pip install -r requirements.txt
```

## Step 7: Initialize Firebase in Your Python Application

Create a new file `firebase_config.py`:

```python
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
import os

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase-adminsdk.json')  # Path to your downloaded key
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# You can now use db to perform Firestore operations
# Example: db.collection('users').document('user_id').set({...})
```

## Step 8: Create Firestore Collections

1. In Firebase Console, go to **Firestore Database**
2. Click **Start collection**
3. Create the following collections:

### Collection 1: `users`
- Document structure:
  ```
  users/
  ├── user_id_1/
  │   ├── email: "user@example.com"
  │   ├── name: "User Name"
  │   ├── created_at: timestamp
  │   └── chat_history/ (subcollection)
  │       ├── timestamp_1/
  │       │   ├── user_query: "..."
  │       │   ├── openai_response: "..."
  │       │   ├── gemini_response: "..."
  │       │   └── timestamp: timestamp
  ```

### Collection 2: `testing` (for testing purposes)
- Already created, can be used for testing reads/writes

## Step 9: Connect Your Application to Firebase

Update your main application files to use Firebase:

### In `firebase_config.py`:
```python
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase
cred = credentials.Certificate('firebase-adminsdk.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_user_chat(user_id, user_query, openai_response, gemini_response):
    """Save chat interaction to Firestore"""
    from datetime import datetime
    
    chat_data = {
        'user_query': user_query,
        'openai_response': openai_response,
        'gemini_response': gemini_response,
        'timestamp': datetime.now()
    }
    
    # Save to user's chat history
    db.collection('users').document(user_id).collection('chat_history').document().set(chat_data)

def get_user_chat_history(user_id):
    """Retrieve user's chat history from Firestore"""
    docs = db.collection('users').document(user_id).collection('chat_history').stream()
    
    chat_history = []
    for doc in docs:
        chat_history.append(doc.to_dict())
    
    return chat_history

def create_user(user_id, email, name):
    """Create a new user document"""
    user_data = {
        'email': email,
        'name': name,
        'created_at': firestore.SERVER_TIMESTAMP
    }
    db.collection('users').document(user_id).set(user_data)
```

### Update `main_agent.py`:
```python
from firebase_config import save_user_chat, get_user_chat_history
from llm_functions import get_gemini_response, get_response_from_openai

# ... existing code ...

def main():
    user_id = "user_123"  # In a real app, get this from authentication
    
    # ... existing code ...
    
    # After getting responses, save them to Firestore:
    save_user_chat(
        user_id=user_id,
        user_query=user_query,
        openai_response=open_ai_response,
        gemini_response=gemini_ai_response
    )
```

## Step 10: Test Firebase Integration

Create a test script `test_firebase.py`:

```python
from firebase_config import db

def test_write():
    """Test writing data to Firestore"""
    db.collection('testing').document('test_doc').set({
        'message': 'Hello Firebase!',
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    print("✓ Write successful")

def test_read():
    """Test reading data from Firestore"""
    doc = db.collection('testing').document('test_doc').get()
    if doc.exists:
        print("✓ Read successful:", doc.to_dict())
    else:
        print("✗ Document not found")

if __name__ == "__main__":
    test_write()
    test_read()
```

Run the test:
```bash
python test_firebase.py
```

## Step 11: Security Considerations

1. **Keep Your Key Safe:**
   - Add `firebase-adminsdk.json` to `.gitignore`
   - Never commit this file to version control

2. **Firestore Security Rules (Update in Firebase Console):**
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{userId} {
         allow read, write: if request.auth.uid == userId;
         match /chat_history/{document=**} {
           allow read, write: if request.auth.uid == userId;
         }
       }
     }
   }
   ```

## Step 12: Next Steps

- [ ] Set up Firebase Authentication UI for sign-up/login
- [ ] Create a frontend (Streamlit/Flask) for user interface
- [ ] Implement user profile management
- [ ] Add chat history retrieval functionality
- [ ] Deploy to production

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'firebase_admin'` | Run `pip install firebase-admin` |
| `PermissionError: Project not found` | Check your Firebase API key and ensure it's valid |
| `Firestore: No document at path` | Make sure the document exists before trying to read it |
| `CORS errors` | Update Firebase security rules for your domain |

## Useful Links

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Python Client](https://firebase.google.com/docs/firestore/client/start-python)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Google Cloud Console](https://console.cloud.google.com/)
