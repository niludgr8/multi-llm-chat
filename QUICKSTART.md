# Quick Start Guide - Multi-LLM Chat Application

Get your Multi-LLM Chat application running in 5 minutes!

## Prerequisites
- Python 3.8+
- OpenAI API key
- Google Gemini API key
- Firebase project with credentials

## 1. Setup Virtual Environment (1 minute)

```bash
# Navigate to project directory
cd "C:\Users\Dell\OneDrive\Documents\Visual Studio 2017\LLM Project"

# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\activate
```

## 2. Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

## 3. Configure Environment Variables (1 minute)

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
GOOGLE_APPLICATION_CREDENTIALS=./multi-llm-chat-4bf66-firebase-adminsdk-fbsvc-572c6a8d90.json
```

## 4. Run the Application (1 minute)

### Option A: Web Interface (Recommended)
```bash
streamlit run app.py
```
Then:
1. Click "Don't have an account? Sign Up"
2. Create new account with email and password
3. Start chatting!

### Option B: Console Chat
```bash
python main_agent.py
```
Then:
1. Select option 1 (OpenAI), 2 (Gemini), or 3 (Both)
2. Type your message
3. Get responses from selected LLM(s)

## Key Features

### 📱 Web Interface (Streamlit)
- **Login/Sign-up**: Firebase Authentication
- **Chat Interface**: Real-time LLM responses
- **Dual Models**: Compare OpenAI and Gemini
- **Chat History**: All messages saved to Firestore
- **Statistics**: View chat metrics

### 💻 Console Interface
- Direct command-line chat
- Fast LLM model switching
- Conversation history tracking

## File Structure

```
├── app.py                    # Main web app (Streamlit)
├── main_agent.py            # Console chat app
├── firebase_auth.py         # Authentication
├── firebase_config.py       # Database operations
├── llm_functions.py         # LLM integration
├── requirements.txt         # Dependencies
├── .env                     # API keys (create this)
└── multi-llm-chat-*-firebase-adminsdk-*.json  # Firebase credentials
```

## Common Commands

```bash
# Start web app
streamlit run app.py

# Test Firebase setup
python test_firebase.py

# Run console chat
python main_agent.py

# Create test data
python create_test_doc.py

# Test all modules
python firebase_config.py
python firebase_auth.py
```

## First Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API keys
- [ ] Firebase credentials file present
- [ ] Run `streamlit run app.py` or `python main_agent.py`
- [ ] Create test account and send first message
- [ ] Verify message saved in Firebase

## Troubleshooting

**Issue: `ModuleNotFoundError`**
```bash
# Make sure virtual environment is activated
.\.venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: Firebase connection failed**
- Check `.env` file has correct credentials path
- Verify Firebase credentials JSON file exists
- Check OPENAI_API_KEY and GEMINI_API_KEY are set

**Issue: OpenAI quota exceeded**
- Check billing at: https://platform.openai.com/account/billing/overview
- Consider using Gemini-only mode (option 2)

**Issue: Streamlit not running**
```bash
# Reinstall streamlit
pip install --upgrade streamlit

# Run with specific host/port
streamlit run app.py --server.port 8501
```

## Next Steps

1. ✅ Get the app running
2. 📚 Read [README.md](README.md) for full documentation
3. 🔐 Learn about Firebase setup in [firebase_setup.md](firebase_setup.md)
4. 🏗️ Understand integration in [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
5. 🚀 Deploy to production

## Support

- Check documentation files (README.md, firebase_setup.md, INTEGRATION_GUIDE.md)
- Review [planning.txt](planning.txt) for project overview
- Check test scripts to understand functionality

## Example: First Message

### Web Interface
1. Open http://localhost:8501
2. Click "Sign Up"
3. Enter email: `test@example.com`
4. Enter password: `TestPassword123`
5. Type name: `Test User`
6. Click "Create Account"
7. Login with credentials
8. Type message: `Hello, how are you?`
9. Select "Both" to compare LLMs
10. Click "Send"

### Console Interface
1. Run `python main_agent.py`
2. Select option `3` for both LLMs
3. Type message: `Hello, how are you?`
4. Receive responses from both OpenAI and Gemini
5. Type `exit` or `4` to quit

## API Keys Setup

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `.env` as `OPENAI_API_KEY=sk-...`

### Google Gemini API Key
1. Go to https://ai.google.dev
2. Create API key for your project
3. Copy to `.env` as `GEMINI_API_KEY=...`

### Firebase Credentials
- Download from Firebase Console → Project Settings → Service Accounts
- Save as `multi-llm-chat-4bf66-firebase-adminsdk-fbsvc-572c6a8d90.json`
- Keep in project root directory

---

**You're all set!** Start with `streamlit run app.py` and enjoy your Multi-LLM Chat application! 🚀
