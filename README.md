# Inquest Document Analysis Pipeline

## Overview for Non-Technical Users

This project is designed to assist in analyzing documents from legal inquests, such as the Jean Charles de Menezes inquest, using Artificial Intelligence (AI). Specifically, it employs a technology called Retrieval-Augmented Generation (RAG) with a local Language Model (Llama 3 via Ollama) to process and interpret large volumes of text data from inquest records. 

For someone like a lawyer without a software engineering background, think of this tool as a digital assistant that can read through hundreds of pages of documents, summarize key points, identify issues with evidence (like missing CCTV footage or inconsistent statements), and even reflect on broader implications of using AI in legal contexts (such as speed of analysis or ethical concerns). The goal is to make complex legal document analysis faster and more accessible, potentially aiding in uncovering critical insights or inconsistencies that might be missed in manual reviews. This could be particularly valuable in ensuring transparency and fairness in legal proceedings.

While the system automates much of the analysis, human oversight is still crucial to validate findings and ensure they are used appropriately in a legal context. This repository contains scripts that download documents, convert them to readable text, and analyze them to answer specific questions about the inquest or the role of AI in such processes.

## Purpose for Technical Users

This project provides tools to analyze inquest documents using local Large Language Models (LLMs, specifically Llama 3 via Ollama) and Retrieval-Augmented Generation (RAG). It automates the process of extracting text from documents, building a searchable index, and querying that index to answer detailed questions about evidence and the implications of AI in legal analysis.

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

- If you are using the provided scripts to download documents, place any extracted `.txt` files or PDFs in the `downloads` folder. If you have your own inquest documents, you can place them there as well for processing.
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
This will process **all documents** in `plain_texts` with each scenario prompt and save results in `scenario_outputs`. This is useful for applying the same set of questions or scenarios to multiple documents.

---

### 4. Corpus-Level (Holistic) Analysis

Edit `llamaindex.py` to set your holistic/cross-document question(s).  
Run:
```bash
python llamaindex.py
```
This will build an index over all documents in `plain_texts` and answer your question(s) using the entire corpus. This method is ideal for questions that require synthesizing information across multiple documents, such as identifying overarching themes or inconsistencies in evidence.

**Note for Beginners**: If you encounter timeout errors with a specific question, the script has been modified to allow running individual analysis questions. Look for the `specific_analysis_question_index` variable in `llamaindex.py` and set it to the number of the question you want to run (e.g., 4 for the fourth question), then run the script again.

---

## Scenario & Ethical Analysis

- Use per-document outputs (from `llamascript.py` or `batch_llamascript.py`) to see what each document says in isolation.
- Use corpus-level outputs (from `llamaindex.py`) to see what emerges when all evidence is considered together.
- Reflect on the results and document your methodology and findings. Consider both the factual insights (e.g., issues with evidence) and ethical implications (e.g., how AI might affect fairness or transparency in legal processes).

---

## Troubleshooting

- **Ollama Not Running**: Ensure Ollama is installed and running on your system. Start it by opening a terminal and typing `ollama serve` if needed, before running any scripts.
- **Models Not Found**: Make sure you have pulled the required models with `ollama pull llama3` and `ollama pull nomic-embed-text`.
- **Python Dependencies**: If you get errors about missing packages, reinstall dependencies with the `pip install` command provided in the setup section.
- **File Not Found Errors**: Check that your documents are in the correct folder (`downloads` or `plain_texts`) and that file paths in scripts are correct.
- **Timeout Errors**: If a query times out, try running individual questions as described in the usage section for `llamaindex.py`.

---

## License

[Your license here]
