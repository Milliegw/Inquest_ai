import os
import ollama

def ask_llama(question, context):
    """
    Query the local Llama 3 model using Ollama with a given question and context.

    Args:
        question (str): The prompt or question to ask the model.
        context (str): The context or document text to provide to the model.

    Returns:
        str: The model's response or an error message.
    """
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

input_folder = "plain_texts"
os.makedirs("scenario_outputs", exist_ok=True)
os.makedirs("scenario_outputs_new", exist_ok=True)

prompts = [
    # (role, scenario prompt)
    ("family", "If you were representing the family, what evidence would you focus on to challenge the police narrative? Provide a detailed analysis of each piece of evidence, identifying potential inconsistencies or contradictions with specific references to the document content. Structure your response with clear headings for each evidence point, include hypothetical examples if direct quotes are unavailable, and conclude with actionable next steps for legal representatives."),
    ("coroner", "Summarize the main findings relevant to the coroner's decision-making. Include detailed explanations of key evidence, direct references or quotes from the document to support each finding, and organize the response with structured sections for clarity. Highlight any ambiguities or gaps in evidence that could impact the decision-making process and suggest areas for further investigation."),
    ("police", "What evidence supports the police's version of events? Provide an in-depth analysis of each supporting piece of evidence, referencing specific document content or quotes where possible. Format the response with clear headings and sub-points for each evidence item, address potential counterarguments or inconsistencies, and conclude with recommendations for strengthening the police narrative or addressing weaknesses."),
    # Add more scenarios as needed
]


# Explicit instructions to reduce hallucination and bias
instructions = (
    "Instructions: Only answer using information found in the provided documents. "
    "If the answer is not present, say 'Not found in the documents.' "
    "Do not speculate, invent facts, or use outside knowledge. "
    "Be concise and objective.\n\n"
)

for filename in os.listdir(input_folder):
    """
    Loop through all .txt files in the input folder, run each scenario prompt,
    and save the results to the scenario_outputs directory.
    """
    if filename.endswith(".txt"):
        filepath = os.path.join(input_folder, filename)
        try:
            with open(filepath) as f:
                context = f.read()[:4000]
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            continue

        if context:
            for role, prompt in prompts:
                print(f"Querying {filename} for scenario: {role}")
                full_prompt = instructions + prompt
                answer = ask_llama(full_prompt, context)
                output_path = f"scenario_outputs_new/{filename.replace('.txt','')}_{role}_scenario.txt"
                with open(output_path, "w") as out:
                    out.write(f"PROMPT: {prompt}\n\nRESPONSE:\n{answer}")
                print(f"Saved output to {output_path}")
        else:
            print(f"No context to query in {filename}.")
