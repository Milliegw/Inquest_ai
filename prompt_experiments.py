# import os
# import ollama

# def ask_llama(question, context):
#     response = ollama.chat(
#         model='llama3',
#         messages=[
#             {'role': 'system', 'content': 'You are an expert legal assistant.'},
#             {'role': 'user', 'content': f"Context:\n{context}\n\nQuestion: {question}"}
#         ]
#     )
#     return response['message']['content']

# with open("downloads/dec_01.pdf.txt") as f:
#     context = f.read()[:4000]

# prompts = [
#     "Summarize the main findings of this document.",
#     "List the key evidence presented.",
#     "What are the main arguments from both sides?",
#     "Identify any potential biases in the document.",
#     # Add more prompts as you wish
# ]

# os.makedirs("prompt_outputs", exist_ok=True)

# for i, prompt in enumerate(prompts, 1):
#     print(f"Testing prompt {i}: {prompt}")
#     answer = ask_llama(prompt, context)
#     output_path = f"prompt_outputs/dec_01_prompt_{i}.txt"
#     with open(output_path, "w") as out:
#         out.write(f"PROMPT: {prompt}\n\nRESPONSE:\n{answer}")
#     print(f"Saved output to {output_path}")

import os
import ollama

def ask_llama(question, context):
    """
    Query the local Llama 3 model using Ollama with a given question and context.

    Args:
        question (str): The prompt or question to ask the model.
        context (str): The context or document text to provide to the model.

    Returns:
        str: The model's response.
    """
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': 'You are an expert legal assistant.'},
            {'role': 'user', 'content': f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response['message']['content']

input_folder = "downloads"  # or "plain_texts" if your files are there
os.makedirs("prompt_outputs", exist_ok=True)

prompts = [
    "Summarize the main findings of this document.",
    "List the key evidence presented.",
    "What are the main arguments from both sides?",
    "Identify any potential biases in the document.",
    # Add more prompts as you wish
]

for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(input_folder, filename)
        try:
            with open(filepath) as f:
                context = f.read()[:4000]
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            continue

        for i, prompt in enumerate(prompts, 1):
            print(f"Testing prompt {i} on {filename}: {prompt}")
            answer = ask_llama(prompt, context)
            output_path = f"prompt_outputs/{filename.replace('.txt','')}_prompt_{i}.txt"
            with open(output_path, "w") as out:
                out.write(f"PROMPT: {prompt}\n\nRESPONSE:\n{answer}")
            print(f"Saved output to {output_path}")