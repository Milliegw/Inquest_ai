import openai

client = openai.OpenAI(api_key="")  # Replace with your actual key

def ask_gpt4(question, context):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert legal assistant."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content

# Example usage:
with open("downloads/dec_01.pdf.txt") as f:
    context = f.read()[:4000]  # Truncate to fit token limit

question = "Summarize the main findings of this document."
answer = ask_gpt4(question, context)
print(answer)