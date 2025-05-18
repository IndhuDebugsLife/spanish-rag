# Install necessary libraries if you haven't already
# pip install chromadb

import chromadb

# 1. Define some dummy documents
documents = [
    "The sky is blue and the grass is green.",
    "Paris is the capital of France.",
    "Elephants are large mammals with trunks.",
    "RAG combines retrieval and generation."
]
ids = [f"doc{i+1}" for i in range(len(documents))]
metadatas = [
    {"source": "observation"},
    {"source": "fact"},
    {"source": "fact"},
    {"source": "concept"}
]

# 2. Initialize ChromaDB in-memory (for simplicity)
client = chromadb.Client()
collection = client.get_or_create_collection("my_rag_collection")

# 3. Add the documents to the collection
collection.add(
    documents=documents,
    ids=ids,
    metadatas=metadatas
)

# 4. Define a query
query_texts = ["What is the capital of France?"]

# 5. Perform a similarity search
results = collection.query(
    query_texts=query_texts,
    n_results=2  # Retrieve the top 2 most relevant documents
)

# 6. Display the retrieved context
print("Retrieved Context:")
if results and results["documents"] and len(results["documents"][0]) > 0:
    for i, doc in enumerate(results["documents"][0]):
        doc_id = results["ids"][0][i]
        print(f"- \"{doc}\" (ID: {doc_id})")
else:
    print("- No relevant documents found.")

# 7. Basic "generation" (simply using the retrieved context)
if results and results["documents"] and len(results["documents"][0]) > 0:
    context = " ".join(results["documents"][0])
    answer = f"Based on the retrieved information: {context}"
    print("\nGenerated Answer:")
    print(answer)
else:
    print("\nGenerated Answer: No relevant information found to answer the query.")

# Optional: Clean up the collection (if you want to start fresh next time)
# client.delete_collection("my_rag_collection")