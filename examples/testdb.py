"""
ChromaDB Basic Functionality Test

This script provides a minimal example to test if ChromaDB is working properly.
It creates an in-memory client, adds a document, and performs a query.
"""

import chromadb
import time
import sys

def test_chromadb_basic():
    """Test basic ChromaDB functionality with in-memory client."""
    print("Testing ChromaDB basic functionality...")
    print(f"ChromaDB version: {chromadb.__version__}")
    
    try:
        # Initialize client
        print("Creating in-memory ChromaDB client...")
        client = chromadb.Client()
        
        # List collections and print them
        print("Listing existing collections...")
        collections = client.list_collections()
        print(f"Found {len(collections)} existing collections")
        for collection in collections:
            print(f"  - {collection.name}")
        
        # Create a test collection
        collection_name = f"test_collection_{int(time.time())}"
        print(f"Creating new collection: {collection_name}")
        collection = client.create_collection(name=collection_name)
        
        # Add a document
        print("Adding test document to collection...")
        collection.add(
            documents=["This is a test document for ChromaDB"],
            metadatas=[{"source": "test_script", "type": "example"}],
            ids=["doc1"]
        )
        
        # Check if document was added
        count = collection.count()
        print(f"Collection now has {count} document(s)")
        
        # Perform a query with query_texts
        print("Performing query with query_texts...")
        results = collection.query(
            query_texts=["test document"],
            n_results=1
        )
        print(f"Query results: {results}")
        
        # Create a simple embedding
        test_embedding = [0.1] * 384  # Adjust dimension based on your embedding model
        
        # Add a document with an embedding
        print("Adding document with embedding...")
        collection.add(
            documents=["Another test document with embedding"],
            embeddings=[test_embedding],
            metadatas=[{"source": "test_script", "type": "embedding_example"}],
            ids=["doc2"]
        )
        
        # Perform a query with embeddings
        print("Performing query with embeddings...")
        results = collection.query(
            query_embeddings=[test_embedding],
            n_results=2
        )
        print(f"Embedding query results: {results}")
        
        # Clean up - delete the collection
        print(f"Deleting test collection: {collection_name}")
        client.delete_collection(name=collection_name)
        
        print("ChromaDB test completed successfully!")
        return True
    
    except Exception as e:
        print(f"ChromaDB test failed: {e}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chromadb_basic()
    if success:
        print("All ChromaDB operations completed successfully!")
        sys.exit(0)
    else:
        print("ChromaDB test failed. See errors above.")
        sys.exit(1)