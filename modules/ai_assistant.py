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

        model_name_gguf = "mistral-7b-instruct-v0.2.q4_k_m.gguf"
        model_path = os.path.join("models", model_name_gguf)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}.")
        
        # --- PERFORMANCE TUNING ---
        # 1. Increased GPU Layers: We are pushing more of the model to the GPU.
        #    For a 4GB card, 30 is an aggressive but often achievable number for a 7B Q4 model.
        #    If you get memory errors, try 28. If it works well, you can even try 32.
        N_GPU_LAYERS = 33
        
        # 2. Increased Batch Size: Processes more tokens in parallel.
        #    This can improve throughput but uses slightly more VRAM.
        N_BATCH = 4096
        
        # --- PART 1: SETUP THE GENERATION LLM (MISTRAL 7B) ---
        model_name_gguf = "mistral-7b-instruct-v0.2.q4_k_m.gguf"
        model_path = os.path.join("models", model_name_gguf)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}.")
        
        # We increase the GPU layers slightly for more performance, 25 is a good target for 4GB VRAM
        self.llm = LlamaCpp(
            model_path=model_path,
            n_gpu_layers=N_GPU_LAYERS,
            n_batch=N_BATCH,
            n_ctx=4096, # The 'attention span' of the model. 4096 is good for Mistral.
            temperature=0.3,
            verbose=False,
        )
        print(f"✅ Generation LLM loaded with {N_GPU_LAYERS} layers offloaded to GPU.")


        # --- PART 2: SETUP THE EMBEDDING MODEL (PERFORMANCE-TUNED) ---
        embed_model_name = "all-MiniLM-L6-v2"
        print(f"🧠 Loading embedding model '{embed_model_name}'...")
        
        # --- !! CRITICAL PERFORMANCE FIX !! ---
        # We are telling the embedding model to use the 'cuda' (NVIDIA GPU) device.
        # This will make the "studying" phase 10x-20x faster.
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embed_model_name,
            model_kwargs={'device': 'cuda'} 
        )
        print("✅ Embedding Model (MiniLM) loaded onto GPU.")
        
        self.chain = None

    def ingest_document(self, structured_content, book_id):
        # ... (This entire method is unchanged) ...
        db_path = os.path.join("./chroma_cache", book_id)
        if os.path.exists(db_path):
            print(f"🧠 Loading cached knowledge base for '{book_id}'...")
            db = Chroma(persist_directory=db_path, embedding_function=self.embeddings)
        else:
            print(f"📚 Creating new knowledge base for '{book_id}'...")
            full_text = "\n\n".join([block['content'] for block in structured_content])
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_text(full_text)
            print(f"📄 Document split into {len(texts)} chunks. Now embedding on GPU...")
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
        # ... (This method is unchanged) ...
        if not self.chain:
            return "Error: No document has been loaded. Please process a book first."
        try:
            print("⏳ Thinking...")
            response = self.chain.invoke(question)
            return response.get('result', "Sorry, I couldn't find an answer.")
        except Exception as e:
            return f"An error occurred: {e}"