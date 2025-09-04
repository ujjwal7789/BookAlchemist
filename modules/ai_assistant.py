# BookAlchemist/modules/ai_assistant.py

import os
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma

class AIAssistant:
    def __init__(self, provider="local", api_key=None):
        print(f"🧠 Initializing AI Assistant with provider: {provider.upper()}")
        self.provider = provider
        
        if self.provider == "local":
            self._initialize_local_models()
        elif self.provider == "openai":
            if not api_key: raise ValueError("OpenAI API key is required.")
            self._initialize_openai_models(api_key)
        elif self.provider == "perplexity":
            if not api_key: raise ValueError("Perplexity API key is required.")
            self._initialize_perplexity_models(api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
        self.chain = None

    def _initialize_local_models(self):
        from langchain_community.llms import LlamaCpp
        from langchain_huggingface import HuggingFaceEmbeddings
        # ... (rest of local init is the same)
        print("✅ Local models loaded successfully.")

    def _initialize_openai_models(self, api_key):
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2, openai_api_key=api_key)
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        print("✅ OpenAI models initialized successfully.")

    def _initialize_perplexity_models(self, api_key):
        """NEW: Initializes Perplexity models."""
        from langchain_perplexity import ChatPerplexity
        from langchain_openai import OpenAIEmbeddings # Perplexity is compatible with OpenAI embeddings
        
        # Perplexity has excellent models. 'llama-3-sonar-large-32k-online' is a great choice.
        self.llm = ChatPerplexity(model="llama-3-sonar-large-32k-online", temperature=0.2, pplx_api_key=api_key)
        
        # For embeddings, we can still use OpenAI's model. If you have an OpenAI key, it will use that.
        # If not, it's better to fall back to the local model.
        # For simplicity, we'll assume the user might have both or we use local.
        try:
            # Try to use OpenAI embeddings if the key is available
            from modules.config_manager import ConfigManager
            openai_key = ConfigManager().get_api_key('openai')
            if openai_key:
                self.embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
                print("Using OpenAI for embeddings.")
            else:
                raise Exception("No OpenAI key for embeddings")
        except:
            print("OpenAI key not found for embeddings, falling back to local model.")
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
            
        print("✅ Perplexity models initialized successfully.")

    def ingest_document(self, structured_content, book_id):
        db_path = os.path.join("./chroma_cache", book_id)
        if os.path.exists(db_path):
            print(f"🧠 Loading cached knowledge base for '{book_id}'...")
            db = Chroma(persist_directory=db_path, embedding_function=self.embeddings)
        else:
            print(f"📚 Creating new knowledge base for '{book_id}'...")
            text_based_content = [block['content'] for block in structured_content if 'content' in block]
            full_text = "\n\n".join(text_based_content)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_text(full_text)
            print(f"📄 Document split into {len(texts)} text chunks. Now embedding...")
            db = Chroma.from_texts(texts=texts, embedding=self.embeddings, persist_directory=db_path)
        
        print("✅ Knowledge base is ready.")
        retriever = db.as_retriever(search_kwargs={"k": 4})

        prompt_template = """
        Use the following pieces of context to answer the question at the end. If you don't know the answer from the context, just say that you don't know.
        Context: {context}
        Question: {question}
        """
        # A slightly different prompt for OpenAI, as it doesn't need the [INST] tags
        if self.provider == "local":
            prompt_template = "[INST]" + prompt_template + "[/INST]"

        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm, chain_type="stuff", retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT}
        )

    def ask(self, question):
        if not self.chain:
            return "Error: No document has been loaded. Please process a book first."
        try:
            print("⏳ Thinking...")
            # LangChain v0.1 uses .invoke(), older versions might use .run() or .__call__()
            response = self.chain.invoke(question)
            # The key for the answer can be 'result' or 'answer' depending on the chain type
            return response.get('result', response.get('answer', "Sorry, I couldn't find an answer."))
        except Exception as e:
            return f"An error occurred: {e}"