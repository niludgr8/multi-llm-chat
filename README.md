# Multi-LLM Chat Application with Firebase Integration

A full-stack Python application that integrates multiple Large Language Models (OpenAI's GPT-4 and Google's Gemini) with Firebase for authentication and data storage.

## Features

### 1. **Multi-LLM Support**
   - Compare responses from OpenAI GPT-4 and Google Gemini
   - Use individual LLMs or compare both responses side-by-side
   - Seamless switching between models

### 2. **Firebase Authentication**
   - User sign-up and login functionality
   - Secure password handling
   - User profile management
   - Session management

### 3. **Firestore Database**
   - User data storage
   - Chat history management with timestamps
   - Subcollection-based organization
   - Chat statistics and analytics

### 4. **Web Interface (Streamlit)**
   - Modern, responsive UI
   - Real-time chat interaction
   - Chat history viewer
   - User profile management
   - Chat statistics dashboard

## Project Structure

```
LLM Project/
├── app.py                          # Main Streamlit web application
├── firebase_auth.py                # Firebase Authentication module
├── firebase_config.py              # Firebase Firestore database operations
├── llm_functions.py                # LLM integration (OpenAI & Gemini)
├── ai_functions.py                 # Additional AI utilities
├── main_agent.py                   # Console-based chat application
├── requirements.txt                # Python dependencies
├── firebase_setup.md               # Firebase setup guide
├── multi-llm-chat-*-firebase-adminsdk-*.json  # Firebase credentials
├── client_secret_*.json            # Google OAuth credentials
└── planning.txt                    # Project planning document
```

## Installation

### 1. Clone/Setup Project
```bash
cd "C:\Users\Dell\OneDrive\Documents\Visual Studio 2017\LLM Project"
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=./multi-llm-chat-4bf66-firebase-adminsdk-fbsvc-572c6a8d90.json
```

### 5. Firebase Setup
- Firebase credentials file: `multi-llm-chat-4bf66-firebase-adminsdk-fbsvc-572c6a8d90.json`
- Ensure Firestore is initialized with the following collections:
  - `testing` (for testing)
  - `users` (for user data and chat history)

## Usage

### Option 1: Web Interface (Recommended)
```bash
streamlit run app.py
```

This will open a web browser with:
- Sign-up/Login interface
- Multi-LLM chat interface
- Chat history viewer
- User statistics

### Option 2: Console-Based Chat
```bash
python main_agent.py
```

Choose between:
1. OpenAI only
2. Gemini only
3. Both (compare responses)

## Module Descriptions

### `firebase_auth.py`
Handles Firebase Authentication operations:
- `sign_up()`: Create new user accounts
- `get_user_by_email()`: Retrieve user by email
- `get_user_by_id()`: Retrieve user by user ID
- `update_user_profile()`: Update user information
- `delete_user()`: Remove user account
- `list_all_users()`: Admin function to list all users

### `firebase_config.py`
Manages Firestore database operations:
- `create_user()`: Create user document
- `get_user()`: Retrieve user data
- `save_chat_message()`: Store chat interaction
- `get_user_chat_history()`: Retrieve user's chat history
- `get_chat_statistics()`: Get user chat analytics
- `clear_user_chat_history()`: Delete user's chat history

### `app.py`
Streamlit web application with:
- Authentication system (login/signup)
- Chat interface
- LLM selection (OpenAI, Gemini, or both)
- Chat history display
- Statistics dashboard
- Logout functionality

### `llm_functions.py`
LLM integration:
- `get_response_from_openai()`: Get responses from GPT-4
- `get_gemini_response()`: Get responses from Gemini

## Firestore Data Structure

### Users Collection
```
users/
├── user_id_1/
│   ├── email: "user@example.com"
│   ├── name: "User Name"
│   ├── created_at: timestamp
│   ├── last_login: timestamp
│   ├── status: "active"
│   └── chat_history/  (subcollection)
│       ├── auto_generated_id_1/
│       │   ├── user_query: "What is AI?"
│       │   ├── openai_response: "..."
│       │   ├── gemini_response: "..."
│       │   ├── user_choice: 3
│       │   ├── timestamp: 2026-02-22T19:40:47
│       │   └── date: "2026-02-22"
│       └── auto_generated_id_2/
│           └── ...
```

## Testing

### Test Firebase Integration
```bash
python test_firebase.py
```

### Test Firebase Configuration
```bash
python firebase_config.py
```

### Create Test Document
```bash
python create_test_doc.py
```

## Security Considerations

1. **API Keys**: Store sensitive keys in `.env` file (add to `.gitignore`)
2. **Firebase Credentials**: Keep `firebase-adminsdk-*.json` secure
3. **Database Rules**: Configure Firestore security rules

### Recommended Firestore Security Rules
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
      
      // Chat history subcollection
      match /chat_history/{document=**} {
        allow read, write: if request.auth.uid == userId;
      }
    }
    
    // Testing collection (for development only)
    match /testing/{document=**} {
      allow read, write: if true;
    }
  }
}
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'firebase_admin'`
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Firebase credentials not found
**Solution**: Ensure the Firebase JSON key file is in the project root directory

### Issue: OpenAI API quota exceeded
**Solution**: Check your OpenAI account billing details at https://platform.openai.com/account/billing/overview

### Issue: Cannot connect to Firestore
**Solution**: 
1. Verify Firebase project ID is correct
2. Check network connectivity
3. Ensure Firestore is enabled in Firebase Console

## Future Enhancements

- [ ] Real-time chat using WebSockets
- [ ] Advanced chat history search
- [ ] User preferences and settings
- [ ] Chat categories/folders
- [ ] Export chat history to PDF
- [ ] User roles and admin panel
- [ ] API endpoints for external integration
- [ ] Mobile app version

## Dependencies

- **firebase-admin**: Firebase Admin SDK
- **google-cloud-firestore**: Firestore database client
- **openai**: OpenAI API client
- **google-generativeai**: Google Gemini API client
- **streamlit**: Web application framework
- **python-dotenv**: Environment variable management

## License

This project is for educational and personal use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Firebase documentation
3. Check OpenAI and Google Generative AI documentation

## Author

Created as a Multi-LLM Chat Application with Firebase Integration
