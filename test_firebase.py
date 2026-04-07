import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# Initialize Firebase Admin SDK with your key
try:
    cred = credentials.Certificate('multi-llm-chat-4bf66-firebase-adminsdk-fbsvc-572c6a8d90.json')
    firebase_admin.initialize_app(cred)
    print("✓ Firebase initialized successfully!\n")
except FileNotFoundError:
    print("✗ Error: Firebase key file not found!")
    print("  Make sure 'multi-llm-chat-4bf66-firebase-adminsdk-fbsvc-572c6a8d90.json' is in the project directory.")
    exit()
except Exception as e:
    print(f"✗ Error initializing Firebase: {e}")
    exit()

# Get Firestore client
db = firestore.client()

def test_write():
    """Test writing data to Firestore"""
    print("=" * 50)
    print("TEST 1: Writing to Firestore")
    print("=" * 50)
    
    try:
        # Create test data
        test_data = {
            'message': 'Hello Firebase!',
            'test_type': 'read_write_test',
            'timestamp': datetime.now(),
            'status': 'success'
        }
        
        # Write to 'testing' collection
        doc_ref = db.collection('testing').document('test_document_001')
        doc_ref.set(test_data)
        
        print("✓ Data written successfully!")
        print(f"  Collection: testing")
        print(f"  Document ID: test_document_001")
        print(f"  Data: {test_data}\n")
        
        return True
    
    except Exception as e:
        print(f"✗ Error writing to Firestore: {e}\n")
        return False

def test_read():
    """Test reading data from Firestore"""
    print("=" * 50)
    print("TEST 2: Reading from Firestore")
    print("=" * 50)
    
    try:
        # Read from 'testing' collection
        doc = db.collection('testing').document('test_document_001').get()
        
        if doc.exists:
            print("✓ Data read successfully!")
            print(f"  Document ID: {doc.id}")
            print(f"  Data retrieved:")
            data = doc.to_dict()
            for key, value in data.items():
                print(f"    - {key}: {value}")
            print()
            return True
        else:
            print("✗ Document not found in Firestore\n")
            return False
    
    except Exception as e:
        print(f"✗ Error reading from Firestore: {e}\n")
        return False

def test_update():
    """Test updating data in Firestore"""
    print("=" * 50)
    print("TEST 3: Updating data in Firestore")
    print("=" * 50)
    
    try:
        # Update the document
        update_data = {
            'status': 'updated',
            'last_updated': datetime.now(),
            'update_message': 'Document was successfully updated'
        }
        
        db.collection('testing').document('test_document_001').update(update_data)
        
        print("✓ Data updated successfully!")
        print(f"  Updated fields: {update_data}\n")
        
        return True
    
    except Exception as e:
        print(f"✗ Error updating Firestore: {e}\n")
        return False

def test_read_after_update():
    """Test reading updated data from Firestore"""
    print("=" * 50)
    print("TEST 4: Reading updated data")
    print("=" * 50)
    
    try:
        doc = db.collection('testing').document('test_document_001').get()
        
        if doc.exists:
            print("✓ Updated data read successfully!")
            print(f"  Document ID: {doc.id}")
            print(f"  Updated data:")
            data = doc.to_dict()
            for key, value in data.items():
                print(f"    - {key}: {value}")
            print()
            return True
        else:
            print("✗ Document not found after update\n")
            return False
    
    except Exception as e:
        print(f"✗ Error reading updated data: {e}\n")
        return False

def test_list_all_documents():
    """List all documents in the 'testing' collection"""
    print("=" * 50)
    print("TEST 5: List all documents in 'testing' collection")
    print("=" * 50)
    
    try:
        docs = db.collection('testing').stream()
        
        doc_count = 0
        print("✓ Documents in 'testing' collection:")
        for doc in docs:
            doc_count += 1
            print(f"\n  Document {doc_count}:")
            print(f"    ID: {doc.id}")
            print(f"    Data: {doc.to_dict()}")
        
        if doc_count == 0:
            print("  (No documents found)")
        
        print()
        return True
    
    except Exception as e:
        print(f"✗ Error listing documents: {e}\n")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("█" * 50)
    print("Firebase Integration Test Suite")
    print("█" * 50)
    print()
    
    # Run all tests
    write_result = test_write()
    read_result = test_read()
    update_result = test_update()
    read_update_result = test_read_after_update()
    list_result = test_list_all_documents()
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    tests = {
        'Write Test': write_result,
        'Read Test': read_result,
        'Update Test': update_result,
        'Read After Update': read_update_result,
        'List Documents': list_result
    }
    
    passed = sum(1 for result in tests.values() if result)
    total = len(tests)
    
    for test_name, result in tests.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<30} {status}")
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All tests passed! Firebase integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    print()

if __name__ == "__main__":
    main()
