# BookAlchemist/modules/ai_assistant.py

import os
import shutil
from langchain.chains import RetrievalQA
from langchain_community.llms import LlamaCpp
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class AIAssistant:
    def __init__(self):
        print("🧠 Initializing AI models (one-time setup)...")
        
        # --- PART 1: SETUP THE GENERATION LLM (ULTRA-STABLE SETTINGS) ---
        model_name_gguf = "mistral-7b-instruct-v0.2.q4_k_m.gguf"
        model_path = os.path.join("models", model_name_gguf)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}.")
        
        # --- ULTRA-STABLE BASELINE SETTINGS FOR 4GB VRAM ---
        # 1. GPU Layers: We are setting this to a very low number (10).
        #    This is GUARANTEED to fit in your VRAM. The goal is to first
        #    confirm that GPU offloading works at all.
        N_GPU_LAYERS = 17
        
        # 2. Batch Size: 256 is a very safe value.
        N_BATCH = 256

        self.llm = LlamaCpp(
            model_path=model_path,
            n_gpu_layers=N_GPU_LAYERS,
            n_batch=N_BATCH,
            n_ctx=4096,
            temperature=0.3,
            # --- IMPORTANT: We are enabling verbose mode ---
            # This will print detailed logs from llama.cpp in your terminal,
            # which will tell us exactly what it's doing with the GPU.
            verbose=True, 
        )
        print(f"✅ Generation LLM initialized with request for {N_GPU_LAYERS} GPU layers.")

        # --- PART 2: SETUP THE EMBEDDING MODEL (ON CPU FOR STABILITY) ---
        embed_model_name = "all-MiniLM-L6-v2"
        print(f"🧠 Loading embedding model '{embed_model_name}'...")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embed_model_name,
            model_kwargs={'device': 'cpu'} 
        )
        print("✅ Embedding Model (MiniLM) loaded onto CPU.")
        
        self.chain = None
        
    def ingest_document(self, structured_content, book_id):
        """
        Ingests a new document, creating a new knowledge base if one doesn't exist
        for this book_id, or loading the cached one if it does.
        """
        db_path = os.path.join("./chroma_cache", book_id)

        if os.path.exists(db_path):
            print(f"🧠 Loading cached knowledge base for '{book_id}'...")
            db = Chroma(persist_directory=db_path, embedding_function=self.embeddings)
        else:
            print(f"📚 Creating new knowledge base for '{book_id}'...")
            
            # --- THE FINAL FIX: Filter for text-based content only ---
            # The AI can only process text, so we filter out images and other non-text blocks.
            # We do this by only including blocks that have a 'content' key.
            text_based_content = [block['content'] for block in structured_content if 'content' in block]
            full_text = "\n\n".join(text_based_content)
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_text(full_text)
            
            print(f"📄 Document split into {len(texts)} text chunks. Now embedding...")
            db = Chroma.from_texts(texts=texts, embedding=self.embeddings, persist_directory=db_path)
        
        print("✅ Knowledge base is ready.")
        retriever = db.as_retriever(search_kwargs={"k": 4})

        prompt_template = """
        [INST] You are a helpful reading assistant. Use the following pieces of context from the book to answer the question at the end. If you don't know the answer, just say that you don't know.
        Context: {context}
        Question: {question} [/INST]
        """
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm, chain_type="stuff", retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT}, return_source_documents=True
        )

    def ask(self, question):
        if not self.chain:
            return "Error: No document has been loaded. Please process a book first."
        try:
            print("⏳ Thinking...")
            response = self.chain.invoke(question)
            return response.get('result', "Sorry, I couldn't find an answer.")
        except Exception as e:
            return f"An error occurred: {e}"