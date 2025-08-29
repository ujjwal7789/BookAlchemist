# BookAlchemist/app_gui.py

import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import shutil
import asyncio

# Import our backend modules
from modules.pdf_parser import PDFParser
from modules.styling_engine import StylingEngine
from modules.pdf_generator import PDFGenerator
from modules.ai_assistant import AIAssistant
from modules.cache_manager import SemanticCache

class BookAlchemistApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Book Alchemist")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        # --- State Variables ---
        self.pdf_path = None
        self.structured_content = None
        self.assistant = None
        self.semantic_cache = None
        self.active_ai_book_name = None
        self.active_ai_book_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- UI Frames ---
        process_frame = ctk.CTkFrame(self)
        process_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        process_frame.grid_columnconfigure(0, weight=1)

        self.process_button = ctk.CTkButton(
            process_frame,
            text="Initializing AI, please wait...",
            height=40,
            command=self.select_and_process,
            state="disabled"
        )
        self.process_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.file_label = ctk.CTkLabel(process_frame, text="Welcome to Book Alchemist!", text_color="gray", anchor="w")
        self.file_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        style_frame = ctk.CTkFrame(self)
        style_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.theme_label = ctk.CTkLabel(style_frame, text="Theme:")
        self.theme_label.grid(row=0, column=0, padx=10, pady=10)
        self.theme_menu = ctk.CTkOptionMenu(style_frame, values=["classic_scholar", "procedural_vintage"])
        self.theme_menu.grid(row=0, column=1, padx=10, pady=10)

        chat_frame = ctk.CTkFrame(self)
        chat_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        self.chatbox = ctk.CTkTextbox(chat_frame, state="disabled", wrap="word")
        self.chatbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.input_box = ctk.CTkEntry(chat_frame, placeholder_text="Ask a question...", state="disabled")
        self.input_box.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.input_box.bind("<Return>", self.send_message_thread)
        self.send_button = ctk.CTkButton(chat_frame, text="Send", command=self.send_message_thread, state="disabled")
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # --- THE HANGING FIX ---
        # Schedule the slow AI initialization to start *after* the GUI has had a moment to load and draw itself.
        self.after(100, self.start_ai_initialization_thread)

    def start_ai_initialization_thread(self):
        """This function is called by the mainloop shortly after startup."""
        threading.Thread(target=self._initialize_ai, daemon=True).start()

    def _initialize_ai(self):
        """This runs in a background thread and enables the UI when ready."""
        try:
            self.assistant = AIAssistant()
            self.semantic_cache = SemanticCache(embedding_model=self.assistant.embeddings)
            self.process_button.configure(state="normal", text="Select a Book to Process")
            self.file_label.configure(text="AI Ready. Please select a book.")
        except Exception as e:
            self.process_button.configure(text="Error! AI Failed to Load. Restart App.", text_color="red")
            self.file_label.configure(text=f"Error: {e}")

    def select_and_process(self):
        # ... (This method is unchanged) ...
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path = path
            self.file_label.configure(text=f"Selected: {os.path.basename(path)}", text_color="white")
            self.add_message("System", f"Selected book: {os.path.basename(path)}")
            self.start_processing_thread()

    def start_processing_thread(self):
        # ... (This method is unchanged) ...
        self.process_button.configure(state="disabled", text="Processing...")
        self.input_box.configure(state="disabled")
        self.send_button.configure(state="disabled")
        threading.Thread(target=self.process_book, daemon=True).start()
    
    def process_book(self):
        # ... (This method is unchanged) ...
        self.active_ai_book_name = os.path.basename(self.pdf_path)
        self.active_ai_book_id = os.path.splitext(self.active_ai_book_name)[0].lower().replace(" ", "_")
        self.add_message("System", "Step 1: Parsing document...")
        parser = PDFParser(file_path=self.pdf_path)
        self.structured_content = parser.extract_structured_content()
        parser.close()
        self.add_message("System", "✅ Parsing complete.")
        theme = self.theme_menu.get()
        self.add_message("System", f"Step 2: Generating PDF with '{theme}' theme...")
        engine = StylingEngine(structured_content=self.structured_content)
        html = engine.generate_html(theme_name=theme, book_title=self.active_ai_book_id)
        pdf_path = os.path.join("output_docs", f"{self.active_ai_book_id}_{theme}.pdf")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(PDFGenerator.generate_pdf_from_html(html, pdf_path))
        loop.close()
        self.add_message("System", f"✅ PDF saved to {pdf_path}")
        try:
            self.add_message("System", "AI is now studying the new book...")
            self.assistant.ingest_document(self.structured_content, self.active_ai_book_id)
            self.add_message("System", f"✅ AI Assistant is ready! You can now ask questions about '{self.active_ai_book_name}'.")
            self.input_box.configure(state="normal")
            self.send_button.configure(state="normal")
            self.process_button.configure(state="normal", text="Process a Different Book")
        except Exception as e:
            self.add_message("Error", f"Could not process book with AI: {e}")
            self.process_button.configure(state="normal", text="Error! Try Again.")

    def send_message_thread(self, event=None):
        # ... (This method is unchanged) ...
        if self.input_box.cget("state") == "normal":
            threading.Thread(target=self.ask_ai, daemon=True).start()

    def ask_ai(self):
        # ... (This method is unchanged) ...
        question = self.input_box.get()
        if not question.strip(): return
        self.add_message("You", question)
        self.input_box.delete(0, 'end')
        self.input_box.configure(state="disabled")
        self.send_button.configure(state="disabled")
        cached_answer = self.semantic_cache.get_similar_answer(self.active_ai_book_id, question)
        if cached_answer:
            self.add_message("AI Assistant (from smart cache)", cached_answer)
        else:
            answer = self.assistant.ask(question)
            self.semantic_cache.add_answer(self.active_ai_book_id, question, answer)
            self.add_message("AI Assistant", answer)
        self.input_box.configure(state="normal")
        self.send_button.configure(state="normal")
    
    def add_message(self, sender, message):
        # ... (This method is unchanged) ...
        self.chatbox.configure(state="normal")
        self.chatbox.insert("end", f"{sender}:\n{message}\n\n")
        self.chatbox.configure(state="disabled")
        self.chatbox.see("end")

if __name__ == "__main__":
    os.makedirs("output_docs", exist_ok=True)
    os.makedirs("chroma_cache", exist_ok=True)
    app = BookAlchemistApp()
    app.mainloop()