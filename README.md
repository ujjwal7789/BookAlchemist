# Book Alchemist 

**Transform any document into a beautiful, intelligent ebook.**

Book Alchemist is a sophisticated desktop application that converts plain documents (PDF, EPUB, MOBI) into exquisitely styled, premium-format ebooks. More than just a styler, it features a powerful, fully offline conversational AI assistant that can answer questions, explain concepts, and discuss themes based on the content of your book.

This project is built with a local-first, privacy-focused philosophy, allowing all core AI functionalities to run on your machine without needing an internet connection.

---

### ✨ Features

*   **Advanced Styling Engine:** Convert unstructured documents into beautifully typeset PDFs using one of two master-class themes:
    *   **Impeccable Novel:** A theme designed with professional typographic principles, featuring procedural page textures, running headers, and a layout that mimics a high-quality hardbound classic.
    *   **Formal Textbook:** A clean, clear, and professional theme perfect for academic papers, manuals, and technical documents, with special styling for code blocks and images.
*   **Multi-Format Support:** Ingests `.pdf`, `.epub`, and `.mobi` files seamlessly.
*   **Dual-Mode Conversational AI:** Chat with your documents using a powerful Retrieval-Augmented Generation (RAG) pipeline.
    *   **Local AI (Default):** Runs a powerful LLM (Mistral 7B) directly on your machine for a 100% offline and private experience. GPU acceleration via CUDA is supported.
    *   **API Mode (Optional):** Configure the app to use external API providers like OpenAI or Perplexity with your own key.
*   **Semantic Caching:** The AI remembers previously asked questions. Semantically similar queries are answered instantly from a local cache, dramatically boosting speed and reducing redundant computations.
*   **Image & Caption Retention:** Intelligently extracts images and their captions from source documents and preserves them in the final styled output.
*   **Responsive Desktop GUI:** A modern, multi-threaded user interface built with CustomTkinter ensures the app never freezes, even during intensive AI processing.

### 📸 Screenshots

*(It is highly recommended to replace these placeholders with actual screenshots of your application)*

<img src="images/app_ss.png" width=1000px>
*The main interface after loading a book.*



<img src="images/original_from_project_gutenberg.png" width=1000px>
*An example of the epub input from Project Gutenberg*



<img src="images/app_proceed_image.png" width=1200px>
*One page of the App processed epub converted to pdf* 

### 🛠️ Technology Stack

*   **Backend:** Python
*   **GUI:** CustomTkinter
*   **Document Parsing:** PyMuPDF (for PDF), EbookLib & BeautifulSoup4 (for EPUB)
*   **Document Conversion:** Calibre Command-Line Tools (for MOBI)
*   **AI Orchestration:** LangChain
*   **Local LLM:** Llama.cpp (running Mistral 7B GGUF)
*   **Vector Database:** ChromaDB
*   **Embedding Models:** Hugging Face Sentence-Transformers
*   **PDF Generation:** Playwright (headless Chromium)

---

### 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

#### Prerequisites

1.  **Python:** Version 3.11 (64-bit) is recommended.
2.  **Git:** Required to clone the repository.
3.  **Calibre:** Required for `.mobi` file conversion.
    *   Download and install from the [official Calibre website](https://calibre-ebook.com/download).
    *   **Crucial:** Ensure you add the Calibre installation directory to your system's PATH environment variable so the `ebook-convert` command is accessible.
4.  **Hardware (for Local AI):** A modern computer with a dedicated NVIDIA GPU (at least 4GB of VRAM) is strongly recommended for a good experience.

#### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/BookAlchemist.git
    cd BookAlchemist
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate it (Windows)
    .\venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    *   Create a file named `requirements.txt` in the project root and paste the content below into it.
    *   Then, run the installation command.

    **`requirements.txt`:**
    ```text
    customtkinter
    PyMuPDF
    playwright
    langchain
    langchain-openai
    langchain-perplexity
    langchain-community
    langchain-huggingface
    chromadb
    sentence-transformers
    numpy
    scikit-learn
    EbookLib
    beautifulsoup4
    lxml
    torch
    torchvision
    torchaudio
    llama-cpp-python
    ```

    **Installation Command:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install PyTorch with CUDA support:**
    *   For GPU acceleration of the embedding model, reinstall PyTorch with the correct CUDA version. Go to the [PyTorch website](https://pytorch.org/get-started/locally/), select your configuration (e.g., Pip, Windows, CUDA 12.1), and run the generated command.

5.  **Install Playwright browsers:**
    ```bash
    playwright install
    ```

#### AI Model Setup

You can choose to use the default Local AI or an external API.

**1. Local AI (Default & Recommended)**
*   **Download the LLM:** This application is optimized for a quantized version of Mistral 7B.
    *   Go to [TheBloke/Mistral-7B-Instruct-v0.2-GGUF on Hugging Face](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/tree/main).
    *   Download the `mistral-7b-instruct-v0.2.q4_k_m.gguf` file (~4.37 GB).
*   **Place the Model:** Create a folder named `models` in the root of your project and place the downloaded `.gguf` file inside it.

**2. API Mode (OpenAI / Perplexity)**
*   Run the application once. It will create a `config.json` file.
*   Click the "Settings" button in the app.
*   Select your provider from the dropdown, enter your API key, and click "Save and Close".
*   Restart the application for the changes to take effect.

### 💻 How to Use

1.  **Launch the application:**
    ```bash
    python app_gui.py
    ```
2.  Wait for the AI models to pre-load (the main button will become active).
3.  Click **"Select Book"** and choose a `.pdf`, `.epub`, or `.mobi` file.
4.  Once the document is analyzed, two action buttons will become active:
    *   **Generate Styled PDF:** Choose a theme from the dropdown and click this button to create the beautiful PDF output.
    *   **Chat with this Book:** Click this button to have the AI "study" the document. Once ready, you can start asking questions in the chat box below.

---

### 📜 License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.
