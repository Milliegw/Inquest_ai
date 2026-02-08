# Inquest Document Analysis Pipeline

## Overview for Non-Technical Users

This project is designed to assist in analyzing documents from legal inquests, such as the Jean Charles de Menezes inquest, using Artificial Intelligence (AI). It employs a modern Retrieval-Augmented Generation (RAG) architecture with:

- **Groq API** (Llama 3.3 70B) for high-quality text generation
- **Milvus Lite** for persistent vector storage
- **Cross-encoder reranking** for improved retrieval precision
- **Citation verification** for legal accuracy

The system processes and interprets large volumes of text data from inquest records while requiring all responses to cite specific page and line numbers—critical for legal work. 

For someone like a lawyer without a software engineering background, think of this tool as a digital assistant that can read through hundreds of pages of documents, summarize key points, identify issues with evidence (like missing CCTV footage or inconsistent statements), and even reflect on broader implications of using AI in legal contexts (such as speed of analysis or ethical concerns). The goal is to make complex legal document analysis faster and more accessible, potentially aiding in uncovering critical insights or inconsistencies that might be missed in manual reviews. This could be particularly valuable in ensuring transparency and fairness in legal proceedings.

A key feature of this project is the ability to automatically acquire documents from specific online sources related to the Jean Charles de Menezes inquest. It includes tools to scrape or download these documents directly from designated websites, convert them into a readable format, and then analyze them to answer specific questions about the inquest or the role of AI in such processes. While the system automates much of the analysis, human oversight is still crucial to validate findings and ensure they are used appropriately in a legal context.

## Purpose for Technical Users

This project provides tools to analyze inquest documents using a modern RAG architecture:

| Component | Technology | Purpose |
|-----------|------------|----------|
| **Vector Store** | Milvus Lite | Persistent, embedded vector database (no Docker required) |
| **LLM** | Groq API (Llama 3.3 70B) | High-quality generation with fast inference |
| **Embeddings** | Ollama (nomic-embed-text) | Local embeddings (no data sent externally) |
| **Reranking** | Cross-encoder | Improved retrieval precision |
| **Chunking** | Custom transcript parser | Extracts page/line metadata for citations |

The pipeline automates scraping documents from online sources, extracting text, building a searchable index with metadata, and querying with citation verification.

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
   git clone https://github.com/[your-username]/Inquest_ai.git
   ```
   Replace `[your-username]` with the actual username or organization hosting this repository if it's hosted on GitHub. If you have the repository locally or on another platform, adjust the URL accordingly.


4. **Navigate to the Project Folder**: After cloning, move into the project directory by typing:
   ```
   cd Inquest_ai
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
   ollama pull gpt-oss:20b
   ollama pull nomic-embed-text
   ```
   This downloads the AI models needed for analysis. It may take some time depending on your internet speed.

3. **Create and Activate a Virtual Environment**: A virtual environment keeps this project's packages separate from your system Python. In the terminal, within the project directory, run:
   ```
   python3 -m venv .venv
   ```
   Then activate it:
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   You should see `(.venv)` at the start of your terminal prompt, indicating the environment is active.

4. **Install Python Dependencies**: With the virtual environment activated, install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
   This installs all required libraries including LlamaIndex, Milvus, Groq, and sentence-transformers.
   
   **Important**: Always activate the virtual environment before running any scripts in this project. If you open a new terminal, run `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows) first.

5. **Set Up Groq API Key**:
   - Get a free API key from [https://console.groq.com/keys](https://console.groq.com/keys)
   - Copy the example environment file:
     ```
     cp .env.example .env
     ```
   - Edit `.env` and add your Groq API key:
     ```
     GROQ_API_KEY=your_actual_api_key_here
     ```
   
   **Note**: Embeddings are computed locally via Ollama, so your document content is never sent to external APIs. Only your queries go through Groq.

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

Process a single document with automatic citation verification:
```bash
# Process all documents with Groq (default)
python inquestscript.py

# Process a specific file
python inquestscript.py -f plain_texts/dec_01.pdf.md

# Use custom prompt
python inquestscript.py -p "What evidence issues are mentioned?"

# Use local Ollama instead of Groq (slower but free)
python inquestscript.py --use-ollama
```

Outputs include citation verification showing which page/line references were found in the source documents.

---

### 3. Batch Scenario Analysis (Per Document)

Process all documents with multiple perspective-based prompts:
```bash
# Process all documents with all scenarios (family, coroner, police)
python batch_inquestscript.py

# Process specific scenario only
python batch_inquestscript.py --scenario family

# Process single file
python batch_inquestscript.py -f plain_texts/dec_01.pdf.md

# Use local Ollama instead of Groq
python batch_inquestscript.py --use-ollama

# Quiet output
python batch_inquestscript.py --quiet
```

This applies perspective-based prompts (family, coroner, police viewpoints) to each document with citation requirements. Results are saved in `scenario_outputs_new/` with citation verification summaries.

---

### 4. Corpus-Level (Holistic) Analysis

Build a vector index and query across all documents with the modern RAG pipeline:
```bash
# First run: builds index and runs all questions
python inquestindex.py

# Subsequent runs: reuses existing index (faster)
python inquestindex.py

# Force rebuild the index
python inquestindex.py --rebuild-index

# Run specific question only
python inquestindex.py --question 1

# Run only analysis questions (AI/ethics)
python inquestindex.py --analysis-only

# Skip analysis, run evidence questions only
python inquestindex.py --skip-analysis

# Use local Ollama LLM instead of Groq API
python inquestindex.py --use-ollama

# Verbose output
python inquestindex.py -v
```

**Features**:
- **Milvus Lite**: Persistent vector storage (index survives restarts)
- **Groq Llama 3.3 70B**: High-quality generation
- **Cross-encoder reranking**: Retrieves top-15, reranks to top-5 for precision
- **Citation verification**: Warns if cited page/lines aren't found in source chunks
- **Transcript metadata**: Custom parser extracts page/line numbers from inquest transcripts

Outputs are saved in `inquestindex_outputs/` with citation verification summaries.

---

## Scenario & Ethical Analysis

- Use per-document outputs (from `inquestscript.py` or `batch_inquestscript.py`) to see what each document says in isolation.
- Use corpus-level outputs (from `inquestindex.py`) to see what emerges when all evidence is considered together.
- Reflect on the results and document your methodology and findings. Consider both the factual insights (e.g., issues with evidence) and ethical implications (e.g., how AI might affect fairness or transparency in legal processes).

---

## Adapting to Other Projects

This repository is tailored for analyzing documents from the Jean Charles de Menezes inquest, with scripts like `scrape_stockwell.py` designed to acquire data from specific online sources related to this case. However, it can be adapted for other legal document analysis projects or inquests with some modifications:

- **Reusing Existing Scripts**: The core functionality of text extraction (`convertdocstoplaintext.py`), indexing, and querying (`inquestindex.py`, `inquestscript.py`, `batch_inquestscript.py`) can be reused for other sets of documents. You would need to modify the data source in `scrape_stockwell.py` to target a different website or data repository, adjusting the scraping logic to match the structure of the new source. Basic programming skills are required to adapt the script to new URLs, HTML structures, or file formats.
- **Custom Solutions**: If the target data source is significantly different (e.g., not web-based or in a unique format), you might need to develop a custom solution for data acquisition. The analysis pipeline (conversion, indexing, querying) can still be used once documents are in a compatible format (PDFs or text files placed in the `downloads` or `plain_texts` folder).
- **Potential Use Cases**: This framework could be adapted for other inquests, legal reviews, or even non-legal document analysis tasks where large volumes of text need to be summarized or queried for specific insights. The prompts in `inquestindex.py` can be customized to focus on different themes or questions relevant to the new context.

Adapting this repository offers a head start compared to building a solution from scratch, especially for users familiar with Python. For those without programming expertise, collaboration with a developer might be necessary to modify the scraping or processing logic for a new project.

## Troubleshooting

- **Virtual Environment Not Activated**: If you get "package not installed" errors even after installing dependencies, make sure your virtual environment is activated. Run `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows). You should see `(.venv)` in your terminal prompt.
- **Python Alias Conflicts**: If `python` still uses the system Python after activating the venv, you may have a shell alias overriding it. Check `~/.zshrc` or `~/.bashrc` for lines like `alias python=...` and remove them, then restart your terminal.
- **Groq API Key Not Set**: Ensure you have copied `.env.example` to `.env` and added your Groq API key. Get a free key at [https://console.groq.com/keys](https://console.groq.com/keys).
- **Groq Rate Limiting**: The free tier allows 30 requests/minute. The scripts include automatic rate limiting and retry logic. If you hit limits, wait a minute or use `--use-ollama` flag for local inference.
- **Ollama Not Running**: Ensure Ollama is installed and running. Start it with `ollama serve` before running scripts. Required for local embeddings.
- **Models Not Found**: Make sure you have pulled the embedding model: `ollama pull nomic-embed-text`. For local LLM fallback: `ollama pull gpt-oss:20b`.
- **Milvus Index Issues**: If you get vector store errors, try rebuilding: `python inquestindex.py --rebuild-index`.
- **Python Dependencies**: If you get import errors, reinstall: `pip install -r requirements.txt`.
- **Citation Warnings**: "Citation not found in sources" warnings mean the LLM cited a page/line that wasn't in the retrieved chunks. This helps identify potential hallucinations.
- **File Not Found Errors**: Check that documents are in `plain_texts/` folder.

---

## Understanding Retrieval Augmented Generation (RAG)

### What is Retrieval Augmented Generation?

Retrieval Augmented Generation (RAG) is a technique in Artificial Intelligence (AI) that combines the power of information retrieval with text generation to provide more accurate and contextually relevant responses. Imagine you have a vast library of documents, and you ask a librarian a question. Instead of guessing the answer, the librarian first searches the library for the most relevant books or articles, reads the pertinent sections, and then crafts a detailed response based on that information. RAG works similarly: it retrieves relevant data from a collection of documents and uses that data to augment the knowledge of a language model, ensuring the generated answers are grounded in specific, factual content rather than relying solely on the model's pre-trained knowledge, which might be outdated or incomplete.

### How is RAG Implemented in This Project?

In this project, RAG is used to analyze inquest documents through a modern multi-stage pipeline:

1. **Document Parsing**: A custom transcript parser (`document_parser.py`) extracts structured metadata from inquest transcripts, including page numbers, line numbers, speakers, and dates. This enables precise citations.

2. **Chunking & Embedding**: Documents are split into overlapping chunks (512 characters with 128 overlap) and embedded using `nomic-embed-text` via Ollama (computed locally, no data sent externally).

3. **Vector Storage**: Embeddings are stored in Milvus Lite, an embedded vector database that persists to disk. No Docker required.

4. **Retrieval & Reranking**: When querying:
   - Top-15 chunks are retrieved by vector similarity
   - A cross-encoder model reranks to the top-5 most relevant chunks
   - This two-stage approach improves precision significantly

5. **Generation with Citations**: The Groq API (Llama 3.3 70B) generates responses using the retrieved chunks. Prompts require specific page/line citations in format `[Page X, Lines Y-Z]`.

6. **Citation Verification**: After generation, the system validates that cited page/line numbers appear in the retrieved source chunks, warning about potential hallucinations.

This architecture enhances accuracy by:
- Grounding responses in actual document content
- Requiring verifiable citations for legal accuracy
- Using reranking to reduce irrelevant context
- Persisting the index to avoid re-computation

---

## License

This project is licensed under the MIT License - see the full license text below for details.

### MIT License

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
