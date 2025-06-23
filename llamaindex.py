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
# ...imports and setup...

# Explicit instructions to reduce hallucination and bias
instructions = (
    "Instructions: Only answer using information found in the provided documents. "
    "If the answer is not present, say 'Not found in the documents.' "
    "Do not speculate, invent facts, or use outside knowledge. "
    "Be concise and objective. "
    "When listing allegations or reliability issues, include direct quotes or references from the documents where possible.\n\n"
)

analysis_instructions = (
    "You are an expert in law, technology, and ethics. "
    "Reflect on the implications of using AI/NLP in the context of inquests like those described in the documents. "
    "You may use your general knowledge as well as any relevant context from the documents. "
    "Be critical, balanced, and cite examples where possible.\n\n"
)

questions = [
    (
        "List all issues or concerns in the provided documents related to the following categories. For each, provide the relevant quote or passage and specify the type of evidence or record involved:\n"
        "1. CCTV or video footage (missing, unavailable, technical faults, not preserved)\n"
        "2. Audio/video recording of briefings, control room activity, or communications (missing, not made, not preserved)\n"
        "3. Telephone or radio records (missing, destroyed, unavailable)\n"
        "4. Handling, alteration, or overwriting of notes, statements, or logs (including collaboration on statements, overwritten notes, or logs not continued)\n"
        "5. Prioritization or failure to use available evidence (e.g., photographs, intelligence, or imagery not accessed or used)\n"
        "For each instance, provide the relevant quote or passage from the documents, and specify the type of evidence or record involved."
    ),
    (
        "Extract and list, in as much detail as possible, every instance in the provided documents where police evidence, statements, or procedures are described as dishonest, unreliable, inaccurate, incomplete, misleading, or otherwise questioned. "
        "For each instance, provide the relevant quote or passage from the documents, and specify the context (e.g., conferring on accounts, alteration of logs, communications failures, evidence handling, expert witness reliability, etc.). "
        "Organize your answer by theme (e.g., Conferring on Accounts, Surveillance Logs, Communications, Evidence Handling, Expert Witnesses, etc.), and use bullet points for clarity. "
        "Include both explicit allegations and any concerns, criticisms, or recommendations related to the reliability or accuracy of police evidence or procedures."
    ),
    (
        "For each theme above, expand with all subpoints, criticisms, and recommendations, and include any relevant paragraph or page references if available."
    )
]

analysis_questions = [
    "How might using AI/NLP to summarize and interrogate inquest documents affect the speed and quality of legal analysis?",
    "Can AI help detect inconsistencies or possible evidence tampering in inquest documents? What are its limitations?",
    "How could the use of AI in inquests affect the balance of power between families, police, and legal teams?",
    "What are the transparency and accountability challenges when using AI to process legal evidence?",
    "In what other ways could AI be used in inquests beyond evidence review and summarization?",
]

os.makedirs("llamaindex_outputs", exist_ok=True)

for i, question in enumerate(questions, 1):
    full_prompt = instructions + question
    try:
        response = query_engine.query(full_prompt)
    except Exception as e:
        response = f"Error: {e}"
    print(f"\nQ{i}: {question}\nA: {response}\n")
    with open(f"llamaindex_outputs/question_{i}.txt", "w") as f:
        f.write(f"QUESTION: {question}\n\nRESPONSE:\n{response}")

for i, question in enumerate(analysis_questions, 1):
    full_prompt = analysis_instructions + question
    try:
        response = query_engine.query(full_prompt)
    except Exception as e:
        response = f"Error: {e}"
    print(f"\nAnalysis Q{i}: {question}\nA: {response}\n")
    with open(f"llamaindex_outputs/analysis_question_{i}.txt", "w") as f:
        f.write(f"QUESTION: {question}\n\nRESPONSE:\n{response}")