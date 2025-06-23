"""
llamaindex.py

Builds a vector index over all .txt files in the plain_texts folder using LlamaIndex and Ollama.
Allows you to ask a question and get an answer synthesized from all documents.

Usage:
    python llamaindex.py

Requirements:
    - Ollama running with 'llama3' and 'nomic-embed-text' models pulled.
    - All .txt files to be indexed should be in the 'plain_texts' folder.
"""

import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.ollama import Ollama
from llama_index.core.settings import Settings
from llama_index.embeddings.ollama import OllamaEmbedding

# Set up Ollama LLM and embedding model for LlamaIndex
llm = Ollama(model="llama3")
Settings.llm = llm
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# Load all .txt files from the plain_texts folder
documents = SimpleDirectoryReader("plain_texts").load_data()

# Build a vector index from all documents
index = VectorStoreIndex.from_documents(documents)

# Create a query engine for the index
query_engine = index.as_query_engine()

# Explicit instructions to reduce hallucination and bias
instructions = (
    "Instructions: Only answer using information found in the provided documents. "
    "If the answer is not present, say 'Not found in the documents.' "
    "Do not speculate, invent facts, or use outside knowledge. "
    "Be concise and objective.\n\n"
)

# List of main and meta-questions
questions = [
    "List any evidence presented by the police during the inquest that was later shown to be misleading, incorrect, inaccurate, or contradicted by other information.",
    "How might using AI/NLP to summarize and interrogate inquest documents affect the speed and quality of legal analysis?",
    "Can AI help detect inconsistencies or possible evidence tampering in inquest documents? What are its limitations?",
    "How could the use of AI in inquests affect the balance of power between families, police, and legal teams?",
    "What are the transparency and accountability challenges when using AI to process legal evidence?",
    "In what other ways could AI be used in inquests beyond evidence review and summarization?",
    # Add more meta-questions as needed
]

os.makedirs("llamaindex_outputs", exist_ok=True)

for i, question in enumerate(questions, 1):
    full_prompt = instructions + question
    response = query_engine.query(full_prompt)
    print(f"\nQ{i}: {question}\nA: {response}\n")
    with open(f"llamaindex_outputs/question_{i}.txt", "w") as f:
        f.write(f"QUESTION: {question}\n\nRESPONSE:\n{response}")