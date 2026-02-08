import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.ollama import Ollama
from llama_index.core.settings import Settings
from llama_index.embeddings.ollama import OllamaEmbedding

# Set up Ollama LLM and embedding model for LlamaIndex
llm = Ollama(model="llama3")
Settings.llm = llm
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

input_folder = "plain_texts"
output_folder = "scenario_outputs_vector"
os.makedirs(output_folder, exist_ok=True)

# Define your prompts (same as batch_llamascript.py for fair comparison)
prompts = [
    ("Scenario 1", "Your first scenario prompt here."),
    ("Scenario 2", "Your second scenario prompt here."),
    # Add more scenarios as needed
]

instructions = (
    "Instructions: Only answer using information found in the provided document. "
    "If the answer is not present, say 'Not found in the document.' "
    "Do not speculate, invent facts, or use outside knowledge. "
    "Be concise and objective.\n\n"
)

for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(input_folder, filename)
        documents = SimpleDirectoryReader(filepath).load_data()
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine(similarity_top_k=5)  # Adjust top_k as needed

        for role, prompt in prompts:
            print(f"Querying {filename} for scenario: {role} (vector search)")
            full_prompt = instructions + prompt
            try:
                answer = query_engine.query(full_prompt)
            except Exception as e:
                answer = f"Error: {e}"
            output_path = f"{output_folder}/{filename.replace('.txt','')}_{role}_vector.txt"
            with open(output_path, "w") as out:
                out.write(f"PROMPT: {prompt}\n\nRESPONSE:\n{answer}")
            print(f"Saved vector output to {output_path}")