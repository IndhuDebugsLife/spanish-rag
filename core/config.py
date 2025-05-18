"""
Configuration file for the Spanish RAG system using OpenAI
"""
# OpenAI API Key (You'll need to set this as an environment variable or directly here)


# PDF processing configs
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Retrieval configs
TOP_K_CHUNKS = 7


# OpenAI Model for Embeddings
OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
OPENAI_EMBEDDING_DIMENSIONS = 1536  # Dimension of the Ada embedding

# OpenAI Model for Question Answering
OPENAI_QA_MODEL = "gpt-4o"

# LLM Prompt Templates (in llm_prompts.py)

# OpenAI Generation Parameters
OPENAI_TEMPERATURE = 0.2
OPENAI_MAX_TOKENS = 500


CHROMA_DB_PATH = 'C:\Indhu\AI\Spanish RAG\chroma_db'
CHROMA_COLLECTION_NAME = 'my_rag_collection'