# Inquest Document Analysis Pipeline

## Overview for Non-Technical Users

This project is designed to assist in analyzing documents from legal inquests, such as the Jean Charles de Menezes inquest, using Artificial Intelligence (AI). Specifically, it employs a technology called Retrieval-Augmented Generation (RAG) with a local Language Model (Llama 3 via Ollama) to process and interpret large volumes of text data from inquest records. 

For someone like a lawyer without a software engineering background, think of this tool as a digital assistant that can read through hundreds of pages of documents, summarize key points, identify issues with evidence (like missing CCTV footage or inconsistent statements), and even reflect on broader implications of using AI in legal contexts (such as speed of analysis or ethical concerns). The goal is to make complex legal document analysis faster and more accessible, potentially aiding in uncovering critical insights or inconsistencies that might be missed in manual reviews. This could be particularly valuable in ensuring transparency and fairness in legal proceedings.

A key feature of this project is the ability to automatically acquire documents from specific online sources related to the Jean Charles de Menezes inquest. It includes tools to scrape or download these documents directly from designated websites, convert them into a readable format, and then analyze them to answer specific questions about the inquest or the role of AI in such processes. While the system automates much of the analysis, human oversight is still crucial to validate findings and ensure they are used appropriately in a legal context.

## Purpose for Technical Users

This project provides tools to analyze inquest documents using local Large Language Models (LLMs, specifically Llama 3 via Ollama) and Retrieval-Augmented Generation (RAG). It automates the process of scraping documents from specific online sources (related to the Jean Charles de Menezes inquest), extracting text from these documents, building a searchable index, and querying that index to answer detailed questions about evidence and the implications of AI in legal analysis.

## Getting Started: For Beginners

This section is for users new to software development who want to use this repository. Follow these steps to clone, set up, and run the project on your computer.

### Prerequisites

- **Computer Skills**: Basic familiarity with using a command line or terminal (instructions provided below).
- **Hardware**: A computer with sufficient processing power and memory (at least 8GB RAM recommended) to run AI models locally.
- **Software**: You will need to install some free tools as described below.

### Step 1: Clone the Repository

1. **Install Git**: If not already on your computer, download and install Git from [https://git-scm.com/downloads](https://git-scm.com/downloads). Git is a tool to download and manage code repositories.

2. **Open Terminal or Command Prompt**:
   - On Windows, search for "Command Prompt" or "PowerShell" in the Start menu.
   - On macOS, search for "Terminal" in Spotlight or find it in Applications > Utilities.
   - On Linux, open your preferred terminal application.

3. **Clone the Repository**: In the terminal, type the following command and press Enter to download this project:
   ```
   git clone https://github.com/[your-username]/Inquest.git
   ```
   Replace `[your-username]` with the actual username or organization hosting this repository if it's hosted on GitHub. If you have the repository locally or on another platform, adjust the URL accordingly.


4. **Navigate to the Project Folder**: After cloning, move into the project directory by typing:
   ```
   cd Inquest
   ```

### Step 2: Set Up the Environment

1. **Install Python**: Ensure you have Python 3.10 or higher installed. Download it from [https://www.python.org/downloads/](https://www.python.org/downloads/) if needed. Verify the installation by typing in the terminal:
   ```
   python --version
   ```
   or
   ```
   python3 --version
   ```
   You should see a version number like `3.10.x` or higher.

2. **Install Ollama**: Ollama is a tool to run AI models locally. Download and install it from [https://ollama.com/](https://ollama.com/). After installation, open a new terminal window and run:
   ```
   ollama pull llama3
   ollama pull nomic-embed-text
   ```
   This downloads the AI models needed for analysis. It may take some time depending on your internet speed.

3. **Install Python Dependencies**: In the terminal, within the project directory, install the required Python packages by running:
   ```
   pip install ollama llama-index-core llama-index-llms-ollama llama-index-embeddings-ollama
   ```
   or if `pip` doesn't work, try:
   ```
   pip3 install ollama llama-index-core llama-index-llms-ollama llama-index-embeddings-ollama
   ```
   This installs the libraries needed to interact with the AI models and process documents.

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

## Usage

### 1. Organize Files

Run:
```bash
python organisefiles.py
```
This moves all `.txt` files from `downloads` to `plain_texts`, preparing them for analysis.

---

### 2. Single Document, Single Prompt

Edit `llamascript.py` to set your prompt and document, then run:
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
