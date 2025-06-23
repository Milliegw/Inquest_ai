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
# if context:
#     print("Querying Llama 3, please wait...")
#     answer = ask_llama(question, context)
#     print(answer)
# else:
#     print("No context to query.")
if context:
    print("Querying Llama 3, please wait...")
    answer = ask_llama(question, context)
    # Save the summary to a file
    summary_path = "downloads/dec_01_summary.txt"
    with open(summary_path, "w") as out:
        out.write(answer)
    print(f"Summary saved to {summary_path}")
else:
    print("No context to query.")