# BookAlchemist/modules/ai_assistant.py

import os
from langchain.chains import RetrievalQA
from langchain_community.llms import LlamaCpp
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

# --- NEW IMPORTS for the robust architecture ---
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class AIAssistant:
    def __init__(self, structured_content):
        print("🧠 Initializing Local AI Assistant with new architecture...")
        
        # --- PART 1: SETUP THE GENERATION LLM (MISTRAL 7B) ---
        model_name_gguf = "mistral-7b-instruct-v0.2.q4_k_m.gguf"
        model_path = os.path.join("models", model_name_gguf)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}.")

        N_GPU_LAYERS = 20
        N_BATCH = 256

        self.llm = LlamaCpp(
            model_path=model_path,
            n_gpu_layers=N_GPU_LAYERS,
            n_batch=N_BATCH,
            n_ctx=4096,
            temperature=0.3,
            verbose=False,
        )
        print("✅ Generation LLM (Mistral) loaded.")

        # --- PART 2: SETUP THE EMBEDDING MODEL ---
        # This is a small, fast model that runs on your CPU/GPU and is specialized for embeddings.
        # It will be downloaded automatically the first time you run this.
        print("🧠 Loading embedding model (first time may require download)...")
        embed_model_name = "all-MiniLM-L6-v2"
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embed_model_name,
            model_kwargs={'device': 'cpu'} # Use CPU for embeddings to save VRAM for the LLM. Change to 'cuda' if you have >6GB VRAM.
        )
        print("✅ Embedding Model (MiniLM) loaded.")

        # --- PART 3: CHUNK, EMBED, AND STORE THE DOCUMENT ---
        print("📚 Processing and chunking the document...")
        full_text = "\n\n".join([block['content'] for block in structured_content])
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_text(full_text)
        print(f"📄 Document split into {len(texts)} chunks.")

        print("🧠 Creating vector store... (This will be much faster now)")
        # Now we use the stable and correct Chroma.from_texts with our new embedding model.
        self.db = Chroma.from_texts(texts=texts, embedding=self.embeddings, persist_directory="./chroma_db")
        self.retriever = self.db.as_retriever(search_kwargs={"k": 4})
        print("✅ Vector store created successfully.")

        # --- PART 4: SETUP THE QA CHAIN ---
        prompt_template = """
        [INST]
        You are a helpful reading assistant. Use the following pieces of context from the book to answer the question at the end.
        If you don't know the answer from the context provided, just say that you don't know. Do not try to make up an answer.
        Keep the answer concise and grounded in the text.

        Context: {context}

        Question: {question}
        [/INST]
        """
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        print("✅ AI Assistant is ready to answer questions.")

    def ask(self, question):
        try:
            print("⏳ Thinking...")
            response = self.chain.invoke(question)
            return response.get('result', "Sorry, I couldn't find an answer.")
        except Exception as e:
            return f"An error occurred: {e}"