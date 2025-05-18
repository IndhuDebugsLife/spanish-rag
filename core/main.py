"""
Main script to run the Spanish RAG system
Using a hardcoded document path for simplicity
"""

import os
from rag_core import initialize_models, process_document, query_document

# Hardcoded document path
DOCUMENT_PATH = os.path.join("data", "filename.pdf")

def main():
    """Main function to process PDF and handle queries"""
    print("\n=== Spanish-English RAG System ===\n")
    
    # Check if document exists
    if not os.path.exists(DOCUMENT_PATH):
        print(f"Error: Document not found at path: {DOCUMENT_PATH}")
        print("Make sure to create a 'data' folder with your PDF file named 'filename.pdf'")
        return
    
    # Initialize models
    print("Initializing models...")
    initialize_models()
    
    # Process the document
    print(f"\nProcessing document: {DOCUMENT_PATH}")
    success = process_document(DOCUMENT_PATH)
    
    if not success:
        print("Failed to process document.")
        return
    
    # Interactive query loop
    print("\n=== Document processed successfully! ===")
    print("Enter your questions in Spanish or English (type 'exit' to quit):")
    
    while True:
        # Get user input
        user_input = input("\nQuestion: ")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'salir']:
            print("Exiting...")
            break
        
        # Skip empty input
        if not user_input.strip():
            continue
        
        # Determine language (simple check for Spanish characters)
        is_spanish = any(char in user_input for char in 'áéíóúüñ¿¡') or '¿' in user_input
        lang = 'es' if is_spanish else 'en'
        
        # Get answer with sources
        result = query_document(user_input, lang, return_sources=True)
        print(f"\nAnswer: {result['answer']}")
        
        # Display source chunks
        print("\nSource chunks:")
        for i, chunk in enumerate(result['sources']):
            print(f"\n--- SOURCE {i+1} (score: {chunk['score']:.4f}) ---")
            print(chunk['text'][:300] + "..." if len(chunk['text']) > 300 else chunk['text'])

if __name__ == "__main__":
    main()