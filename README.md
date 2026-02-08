# Inquest Document Analysis Pipeline

## Overview

This project assists in analyzing legal inquest documents (e.g., Jean Charles de Menezes inquest) using AI. It leverages Retrieval-Augmented Generation (RAG) with a local Language Model (Llama 3 via Ollama) to process, summarize, and interrogate large volumes of text data.

**For non-technical users:**  
Think of this as a digital assistant that reads, summarizes, and highlights key issues in legal documents—such as missing evidence or inconsistent statements—making complex analysis faster and more accessible.

**For technical users:**  
The pipeline automates scraping, conversion, indexing, and querying of inquest documents using LlamaIndex and Ollama, supporting both per-document and corpus-level analysis.

---

## Overview for Non-Technical Users

This project is designed to assist in analyzing documents from legal inquests, such as the Jean Charles de Menezes inquest, using Artificial Intelligence (AI). Specifically, it employs a technology called Retrieval-Augmented Generation (RAG) with a local Language Model (Llama 3 via Ollama) to process and interpret large volumes of text data from inquest records. 

For someone like a lawyer without a software engineering background, think of this tool as a digital assistant that can read through hundreds of pages of documents, summarize key points, identify issues with evidence (like missing CCTV footage or inconsistent statements), and even reflect on broader implications of using AI in legal contexts (such as speed of analysis or ethical concerns). The goal is to make complex legal document analysis faster and more accessible, potentially aiding in uncovering critical insights or inconsistencies that might be missed in manual reviews. This could be particularly valuable in ensuring transparency and fairness in legal proceedings.

A key feature of this project is the ability to automatically acquire documents from specific online sources related to the Jean Charles de Menezes inquest. It includes tools to scrape or download these documents directly from designated websites, convert them into a readable format, and then analyze them to answer specific questions about the inquest or the role of AI in such processes. While the system automates much of the analysis, human oversight is still crucial to validate findings and ensure they are used appropriately in a legal context.



## Purpose for Technical Users

This project provides tools to analyze inquest documents using local Large Language Models (LLMs, specifically Llama 3 via Ollama) and Retrieval-Augmented Generation (RAG). It automates the process of scraping documents from specific online sources (related to the Jean Charles de Menezes inquest), extracting text from these documents, building a searchable index, and querying that index to answer detailed questions about evidence and the implications of AI in legal analysis.

## Retrieval-Augmented Generation (RAG) Process

1. **Retrieval**: LlamaIndex is used to build a semantic index of documents and retrieve the most relevant chunks in response to a query.
2. **Augmentation**: The retrieved text is passed as context to a language model (Llama 3 via Ollama).
3. **Generation**: The LLM generates answers or summaries based on both the retrieved context and its own reasoning abilities. This allows for more accurate and contextually relevant responses, especially when dealing with large volumes of text where specific information needs to be extracted and synthesized.

## Setup Instructions

### Prerequisites

- Python 3.10+
- Ollama (with `llama3` and `nomic-embed-text` models)
- At least 8GB RAM recommended for running Llama 3 locally, more for larger models or multiple queries.

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/[your-username]/Inquest.git
   cd Inquest
   ```

2. **Install dependencies:**
   ```bash
   pip install ollama llama-index-core llama-index-llms-ollama llama-index-embeddings-ollama
   ```

3. **Install and start Ollama:**
   - Download from [https://ollama.com/](https://ollama.com/)
   - Pull models:
     ```bash
     ollama pull llama3
     ollama pull nomic-embed-text
     ```
   - Start Ollama:
     ```bash
     ollama serve
     ```


### Step 3: Prepare Your Data

- **Using Provided Scripts to Download Documents**: You can use `scrape_stockwell.py` to automatically download documents related to the Jean Charles de Menezes inquest from a specified online source. Run the following command to scrape and save PDFs to the `downloads` folder:
  ```
  python scrape_stockwell.py
  ```
- If you already have documents or PDFs, place them in the `downloads` folder. If you have your own inquest documents, you can place them there as well for processing.
- Run the following command to organize files from `downloads` to `plain_texts` (converting PDFs to text if necessary):
  ```
  python organisefiles.py
  ```

---

## Workflow

### 1. Acquire and Prepare Documents

- **Scrape documents:**  
  ```bash
  python scrape_stockwell.py
  ```
- **Convert PDFs to text:**  
  ```bash
  python convertdocstoplaintext.py
  ```
- **Organize files:**  
  ```bash
  python organisefiles.py
  ```
  This moves `.txt` files to `plain_texts`.

---

### 2. Single Document, Single Prompt

Edit `llamascript.py` to set your prompt and document, then run:
```bash
python llamascript.py
```
```bash
python llamascript.py
```
This will process one document and print/save the result. Use a text editor or an Integrated Development Environment (IDE) like VSCode to edit the file and specify your prompt (the question or instruction for the AI) and the path to the document.

---

### 3. Batch Scenario Analysis (Per Document)

Edit `batch_llamascript.py` to set your scenario prompts.  
Run:
```bash
python batch_llamascript.py
```
This will process **all documents** in `plain_texts` with each scenario prompt and save results in `scenario_outputs`. This script applies specific perspective-based prompts (e.g., family, coroner, police viewpoints) to each document individually, analyzing how different stakeholders might interpret the evidence in isolation. This is useful for detailed, per-document analysis from multiple angles.

---

### 4. Corpus-Level (Holistic) Analysis

Edit `llamaindex.py` to set your holistic/cross-document question(s).  
Run:
```bash
python llamaindex.py
```
This will build an index over all documents in `plain_texts` and answer your question(s) using the entire corpus. Unlike `batch_llamascript.py`, this script uses prompts designed for synthesizing information across all documents, focusing on specific evidence issues (e.g., missing CCTV footage, reliability of police statements) and broader implications of AI in legal analysis (e.g., speed, transparency). The outputs are saved as question-and-answer pairs in the `llamaindex_outputs` directory, with files named `question_1.txt`, `question_2.txt`, etc., for evidence-specific queries, and `analysis_question_1.txt`, `analysis_question_2.txt`, etc., for broader analysis topics. This method is ideal for identifying overarching themes or inconsistencies that emerge when considering the full set of documents together.

**Note for Beginners**: If you encounter timeout errors with a specific question, the script has been modified to allow running individual analysis questions. Look for the `specific_analysis_question_index` variable in `llamaindex.py` and set it to the number of the question you want to run (e.g., 4 for the fourth question), then run the script again.

---

## Scenario & Ethical Analysis

- Use per-document outputs (from `llamascript.py` or `batch_llamascript.py`) to see what each document says in isolation.
- Use corpus-level outputs (from `llamaindex.py`) to see what emerges when all evidence is considered together.
- Reflect on the results and document your methodology and findings. Consider both the factual insights (e.g., issues with evidence) and ethical implications (e.g., how AI might affect fairness or transparency in legal processes).

---
# Inquest Document Analysis Pipeline

This project provides tools to analyze inquest documents using local LLMs (Llama 3 via Ollama) and retrieval-augmented generation (RAG).

## Setup

1. **Install dependencies**  
   - Python 3.10+  
   - [Ollama](https://ollama.com/) (install and pull `llama3` and `nomic-embed-text` models)
   - Python packages:
     ```
     pip install ollama llama-index-core llama-index-llms-ollama llama-index-embeddings-ollama
     ```

2. **Prepare your data**  
   - Place all extracted `.txt` files in the `downloads` folder.

## Usage

### 1. Organize Files

Run:
```bash
python organisefiles.py
```
This moves all `.txt` files from `downloads` to `plain_texts`.

---

### 2. Single Document, Single Prompt

Edit `llamascript.py` to set your prompt and document, then run:
```bash
python llamascript.py
```
This will process one document and print/save the result.

---

### 3. Batch Scenario Analysis (Per Document)

Edit `batch_llamascript.py` to set your scenario prompts.  
Run:
```bash
python batch_llamascript.py
```
This will process **all documents** in `plain_texts` with each scenario prompt and save results in `scenario_outputs`.

---

### 4. Corpus-Level (Holistic) Analysis

Edit `llamaindex.py` to set your holistic/cross-document question(s).  
Run:
```bash
python llamaindex.py
```
This will build an index over all documents and answer your question(s) using the entire corpus.

---


## Adapting to Other Projects

This repository is tailored for analyzing documents from the Jean Charles de Menezes inquest, with scripts like `scrape_stockwell.py` designed to acquire data from specific online sources related to this case. However, it can be adapted for other legal document analysis projects or inquests with some modifications:

- **Reusing Existing Scripts**: The core functionality of text extraction (`convertdocstoplaintext.py`), indexing, and querying (`llamaindex.py`, `llamascript.py`, `batch_llamascript.py`) can be reused for other sets of documents. You would need to modify the data source in `scrape_stockwell.py` to target a different website or data repository, adjusting the scraping logic to match the structure of the new source. Basic programming skills are required to adapt the script to new URLs, HTML structures, or file formats.
- **Custom Solutions**: If the target data source is significantly different (e.g., not web-based or in a unique format), you might need to develop a custom solution for data acquisition. The analysis pipeline (conversion, indexing, querying) can still be used once documents are in a compatible format (PDFs or text files placed in the `downloads` or `plain_texts` folder).
- **Potential Use Cases**: This framework could be adapted for other inquests, legal reviews, or even non-legal document analysis tasks where large volumes of text need to be summarized or queried for specific insights. The prompts in `llamaindex.py` can be customized to focus on different themes or questions relevant to the new context.

Adapting this repository offers a head start compared to building a solution from scratch, especially for users familiar with Python. For those without programming expertise, collaboration with a developer might be necessary to modify the scraping or processing logic for a new project.

## Troubleshooting

- **Ollama Not Running**: Ensure Ollama is installed and running on your system. Start it by opening a terminal and typing `ollama serve` if needed, before running any scripts.
- **Models Not Found**: Make sure you have pulled the required models with `ollama pull llama3` and `ollama pull nomic-embed-text`.
- **Python Dependencies**: If you get errors about missing packages, reinstall dependencies with the `pip install` command provided in the setup section.
- **File Not Found Errors**: Check that your documents are in the correct folder (`downloads` or `plain_texts`) and that file paths in scripts are correct.
- **Timeout Errors**: If a query times out, try running individual questions as described in the usage section for `llamaindex.py`.

---

## Understanding Retrieval Augmented Generation (RAG)

### What is Retrieval Augmented Generation?

Retrieval Augmented Generation (RAG) is a technique in Artificial Intelligence (AI) that combines the power of information retrieval with text generation to provide more accurate and contextually relevant responses. Imagine you have a vast library of documents, and you ask a librarian a question. Instead of guessing the answer, the librarian first searches the library for the most relevant books or articles, reads the pertinent sections, and then crafts a detailed response based on that information. RAG works similarly: it retrieves relevant data from a collection of documents and uses that data to augment the knowledge of a language model, ensuring the generated answers are grounded in specific, factual content rather than relying solely on the model's pre-trained knowledge, which might be outdated or incomplete.

### How is RAG Implemented in This Project?

In this project, RAG is used to analyze inquest documents by integrating two key components:
- **Document Indexing and Retrieval**: The project employs a tool called LlamaIndex to create a searchable index of all the text documents stored in the `plain_texts` folder. This index acts like a digital catalog, breaking down the documents into smaller, searchable pieces (or "vectors") based on their content. When a question is asked, LlamaIndex retrieves the most relevant sections of the documents that match the query.
- **Text Generation with Local AI Model**: Once the relevant document sections are retrieved, they are passed to a local Large Language Model (LLM), specifically Llama 3, running via Ollama on your computer. This model uses the retrieved information to generate comprehensive answers to questions about the inquest evidence or the implications of using AI in legal analysis. For example, scripts like `llamaindex.py` build this index and query it with predefined questions, ensuring the responses are based on the specific content of the inquest documents rather than generic or potentially inaccurate information.

This RAG approach enhances the accuracy and relevance of the analysis by grounding the AI's responses in the actual text of the documents, making it a powerful tool for legal research and review. It allows the system to answer detailed questions about evidence issues (e.g., missing CCTV footage) or broader ethical concerns (e.g., transparency in AI use) by directly referencing the content of the analyzed records.

---

## License

This project is licensed under the MIT License - see the full license text below for details.

### MIT License
s
Copyright (c) [2025] [Camilla Graham Wood]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
