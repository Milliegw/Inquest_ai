import os
import ollama

def ask_llama(question, context):
    try:
        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': 'You are an expert legal assistant.'},
                {'role': 'user', 'content': f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

try:
    with open("downloads/dec_01.pdf.txt") as f:
        context = f.read()[:4000]
except FileNotFoundError:
    print("File not found: downloads/dec_01.pdf.txt")
    context = ""

question = "Summarize the main findings of this document."

instructions = (
    "Instructions: Only answer using information found in the provided document. "
    "If the answer is not present, say 'Not found in the document.' "
    "Do not speculate, invent facts, or use outside knowledge. "
    "Be concise and objective.\n\n"
)

# Create the summaries folder if it doesn't exist
os.makedirs("summaries", exist_ok=True)

if context:
    print("Querying Llama 3, please wait...")
    full_prompt = instructions + question
    answer = ask_llama(full_prompt, context)
    # answer = ask_llama(question, context)
    # Save the summary to the summaries folder
    summary_path = "summaries/dec_01_summary.txt"
    with open(summary_path, "w") as out:
        out.write(answer)
    print(f"Summary saved to {summary_path}")
else:
    print("No context to query.")