import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate('multi-llm-chat-4bf66-firebase-adminsdk-fbsvc-572c6a8d90.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Create a test document
test_doc = {
    'name': 'Test Document',
    'description': 'This is a test document to verify Firestore write operations',
    'created_date': datetime.now().strftime('%Y-%m-%d'),
    'created_time': datetime.now().strftime('%H:%M:%S'),
    'created_at': datetime.now().isoformat(),
    'test_status': 'active',
    'data_type': 'test'
}

# Write to Firebase
doc_ref = db.collection('testing').document('test_doc_001')
doc_ref.set(test_doc)

print("✓ Test document created successfully!")
print(f"Collection: testing")
print(f"Document ID: test_doc_001")
print(f"Data: {test_doc}")
