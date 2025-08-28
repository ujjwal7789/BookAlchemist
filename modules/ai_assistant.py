import os
from dotenv import load_dotenv

from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter

class AIAssistant:
    """
    An AI assistant that can answer questions about a specific document.
    It uses the RAG (Retrieval-Augmented Generation) pattern.
    """

    def __init__(self, structured_content):
        """
         Initializes the assistant and builds the knowledge base from the document.
        This is the "studying" phase.
        """

        print("🧠 AI Assistant is studying the document... (this may take a moment)")

        load_dotenv()
        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAIKEY NOT FOUND")
        
        full_text = "\n".join([block['content'] for block in structured_content])
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_text(full_text)

        embeddings = OpenAIEmbeddings()
        self.db = Chroma.from_texts(texts, embeddings)

        self.retriever = self.db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        self.chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0.2),
            chain_type="stuff",
            retriever=self.retriever,
        )

        print("✅ AI Assistant is ready to answer questions.")

    def ask(self, question):
        """
        Asks a question to the AI assistant
        This is the "answering" phase.
        """
        try:
            print("⏳ Thinking...")
            response = self.chain.run(question)
            return response
        except Exception as e:
            return f"An error occurred: {e}"