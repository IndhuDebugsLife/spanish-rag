"""
Simple Streamlit interface for the Spanish-English RAG system
with hardcoded document path and chunking strategy selection
"""

import streamlit as st
import os
from rag_core import initialize_models, process_document, query_document
import nltk
import os

nltk_data_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'nltk_data')
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

print(f"NLTK data paths: {nltk.data.path}")

# Hardcoded document path
DOCUMENT_PATH = os.path.join("data", "SpanishRoadContract.txt")

# Set page title and layout
st.set_page_config(
    page_title="Spanish-English RAG System",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'document_processed' not in st.session_state:
    st.session_state.document_processed = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main title
st.title("Spanish-English RAG System")

# Sidebar with document information
with st.sidebar:
    st.header("Document Information")
    st.write(f"Document: {DOCUMENT_PATH}")

    # Chunking strategy selection
    chunking_strategy = st.selectbox(
        "Choose Chunking Strategy:",
        ["Basic", "Semantic"]
    )
    st.session_state.chunking_strategy = chunking_strategy

    # Process document button
    if st.button("Process Document"):
        # Check if document exists
        if not os.path.exists(DOCUMENT_PATH):
            st.error(f"Document not found at path: {DOCUMENT_PATH}")
            st.info("Make sure to create a 'data' folder with your text file.")
        else:
            # Initialize models if not already done
            if not st.session_state.initialized:
                with st.spinner("Loading models... This may take a while for the first time"):
                    initialize_models()
                    st.session_state.initialized = True

            # Process the document with the selected strategy
            with st.spinner(f"Processing document with {st.session_state.chunking_strategy} chunking..."):
                success = process_document(DOCUMENT_PATH, chunking_strategy=st.session_state.chunking_strategy.lower())
                if success:
                    st.session_state.document_processed = True
                    st.success(f"Document processed successfully with {st.session_state.chunking_strategy} chunking!")
                else:
                    st.error("Failed to process document. Check console for details.")

# Main content area - Chat interface
st.header("Ask Questions")

# Input for questions
question = st.text_input("Enter your question (Spanish or English):")
submit_button = st.button("Submit")

# Display when document needs to be processed first
if not st.session_state.document_processed:
    st.warning("Please process the document first by clicking the 'Process Document' button in the sidebar.")

# Handle question submission
if submit_button and question and st.session_state.document_processed:
    with st.spinner("Generating answer..."):
        # Simple language detection (very basic)
        is_spanish = any(char in question for char in 'áéíóúüñ¿¡') or '¿' in question
        lang = 'es' if is_spanish else 'en'

        # Get answer from RAG system with sources
        result = query_document(question, lang, return_sources=True)

        # Add to chat history with sources
        st.session_state.chat_history.append({
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"]
        })

# Display chat history
if st.session_state.chat_history:
    st.header("Chat History")
    for i, exchange in enumerate(st.session_state.chat_history):
        # Display question
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write(f"Question {i+1}:")
        with col2:
            st.write(exchange["question"])

        # Display answer
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write("Answer:")
        with col2:
            st.write(exchange["answer"])

        # Display source chunks with expander
        with st.expander(f"View Source Chunks (Question {i+1})", expanded=False):
            for j, chunk in enumerate(exchange["sources"]):
                st.markdown(f"**Source {j+1}** (similarity score: {chunk['score']:.4f})")
                st.text_area(f"Source text {j+1}", chunk["text"], height=150, key=f"query_{i}_source_{j}")
        st.divider()

# Instructions at the bottom
st.markdown("---")
st.write("**Instructions:**")
st.write("1. Choose the desired chunking strategy from the sidebar.")
st.write("2. Click 'Process Document' in the sidebar to load and process the text file.")
st.write("3. Enter your questions in Spanish or English.")
st.write("4. Click 'Submit' to get answers based on the document content.")