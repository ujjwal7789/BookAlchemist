# BookAlchemist/app_gui.py

import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import shutil
import asyncio

# --- Note: We only need ONE PDF parser now, but support EPUB/MOBI ---
from modules.pdf_parser import PDFParser
from modules.epub_parser import EpubParser
from modules.mobi_converter import convert_mobi_to_epub

from modules.styling_engine import StylingEngine
from modules.pdf_generator import PDFGenerator
from modules.ai_assistant import AIAssistant
from modules.cache_manager import SemanticCache

class BookAlchemistApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Book Alchemist - Final Edition")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        # --- THE FIX: Correct method name (no underscore) ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- State Variables ---
        self.file_path = None
        self.structured_content = None
        self.dominant_font = None # To store the detected font
        self.assistant = None
        self.semantic_cache = None
        self.active_ai_book_name = None
        self.active_ai_book_id = None

        # --- UI Frames ---
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)
        
        self.select_button = ctk.CTkButton(
            file_frame, text="Select Book", height=40,
            command=self.select_book, state="disabled"
        )
        self.select_button.grid(row=0, column=0, padx=10, pady=10)

        self.file_label = ctk.CTkLabel(file_frame, text="Initializing AI, please wait...", text_color="gray", anchor="w")
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        action_frame.grid_columnconfigure((0, 2), weight=1)

        self.style_button = ctk.CTkButton(
            action_frame, text="1. Generate Styled PDF",
            command=self.start_styling_thread, state="disabled"
        )
        self.style_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.theme_menu = ctk.CTkOptionMenu(action_frame, values=["premium_novel", "formal_textbook"])
        self.theme_menu.grid(row=0, column=1, padx=10, pady=10)

        self.chat_button = ctk.CTkButton(
            action_frame, text="2. Chat with this Book",
            command=self.start_ai_ingestion_thread, state="disabled"
        )
        self.chat_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

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

        self.after(100, self.start_ai_initialization_thread)

    def start_ai_initialization_thread(self):
        threading.Thread(target=self._initialize_ai, daemon=True).start()

    def _initialize_ai(self):
        try:
            self.assistant = AIAssistant()
            self.semantic_cache = SemanticCache(embedding_model=self.assistant.embeddings)
            self.select_button.configure(state="normal")
            self.file_label.configure(text="AI Ready. Please select a book to begin.")
        except Exception as e:
            self.file_label.configure(text=f"Error: AI Failed to Load. Details: {e}", text_color="red")

    def select_book(self):
        path = filedialog.askopenfilename(
            title="Select a Book",
            filetypes=[
                ("All Supported Books", "*.pdf *.epub *.mobi"),
                ("PDF Documents", "*.pdf"),
                ("EPUB Books", "*.epub"),
                ("MOBI Books", "*.mobi")
            ]
        )
        if path:
            self.file_path = path
            self.file_label.configure(text=f"Selected: {os.path.basename(path)}", text_color="white")
            self.add_message("System", f"Selected book: {os.path.basename(path)}")
            
            self.style_button.configure(state="disabled")
            self.chat_button.configure(state="disabled")
            self.input_box.configure(state="disabled")
            self.send_button.configure(state="disabled")

            threading.Thread(target=self._parse_document_thread, daemon=True).start()

    def _parse_document_thread(self):
        self.add_message("System", "Analyzing document...")
        
        parser = None
        path_to_parse = self.file_path
        
        try:
            if path_to_parse.lower().endswith('.pdf'):
                parser = PDFParser(file_path=path_to_parse)
                self.structured_content = parser.extract_structured_content()
                # Find dominant font only for PDFs
                self.dominant_font, _ = parser.find_dominant_font()
                self.add_message("System", f"Dominant font found: {self.dominant_font or 'N/A'}")
            
            elif path_to_parse.lower().endswith('.epub'):
                parser = EpubParser(file_path=path_to_parse)
                self.structured_content = parser.extract_structured_content()
                self.dominant_font = None # EPUBs use CSS, so we don't override
            
            elif path_to_parse.lower().endswith('.mobi'):
                converted_epub_path = convert_mobi_to_epub(path_to_parse)
                if converted_epub_path:
                    path_to_parse = converted_epub_path
                    parser = EpubParser(file_path=path_to_parse)
                    self.structured_content = parser.extract_structured_content()
                    self.dominant_font = None
                else:
                    self.add_message("Error", "MOBI to EPUB conversion failed. Please check Calibre.")
                    return
            
            if parser:
                parser.close()
                self.add_message("System", f"✅ Analysis complete. Ready for action.")
                self.style_button.configure(state="normal")
                self.chat_button.configure(state="normal")
            else:
                self.add_message("Error", f"Unsupported file type.")

        except Exception as e:
            self.add_message("Error", f"Failed to parse document: {e}")

    def start_styling_thread(self):
        self.style_button.configure(state="disabled")
        self.chat_button.configure(state="disabled")
        threading.Thread(target=self._run_styling_pipeline, daemon=True).start()

    def _run_styling_pipeline(self):
        try:
            theme = self.theme_menu.get()
            book_id = os.path.splitext(os.path.basename(self.file_path))[0].lower().replace(" ", "_")
            self.add_message("System", f"Generating PDF with '{theme}' theme...")
            
            engine = StylingEngine(structured_content=self.structured_content)
            html = engine.generate_html(theme_name=theme, book_title=book_id, dominant_font=self.dominant_font)
            
            base_pdf_path = os.path.join("output_docs", f"{book_id}_{theme}.pdf")
            final_pdf_path = base_pdf_path
            counter = 1
            while os.path.exists(final_pdf_path):
                name, ext = os.path.splitext(base_pdf_path)
                final_pdf_path = f"{name} ({counter}){ext}"
                counter += 1
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(PDFGenerator.generate_pdf_from_html(html, final_pdf_path))
            loop.close()
            
            self.add_message("System", f"✅ PDF saved to {os.path.basename(final_pdf_path)}")
        except Exception as e:
            self.add_message("Error", f"Failed to generate PDF: {e}")
        finally:
            self.style_button.configure(state="normal")
            self.chat_button.configure(state="normal")

    def start_ai_ingestion_thread(self):
        self.style_button.configure(state="disabled")
        self.chat_button.configure(state="disabled")
        threading.Thread(target=self._run_ai_ingestion, daemon=True).start()

    def _run_ai_ingestion(self):
        try:
            self.active_ai_book_name = os.path.basename(self.file_path)
            self.active_ai_book_id = os.path.splitext(self.active_ai_book_name)[0].lower().replace(" ", "_")
            
            self.add_message("System", "AI is now studying the book...")
            self.assistant.ingest_document(self.structured_content, self.active_ai_book_id)
            self.add_message("System", f"✅ AI is ready! You can now ask questions about '{self.active_ai_book_name}'.")
            
            self.input_box.configure(state="normal")
            self.send_button.configure(state="normal")
        except Exception as e:
            self.add_message("Error", f"Could not load book into AI: {e}")
        finally:
            self.style_button.configure(state="normal")
            self.chat_button.configure(state="normal")

    def send_message_thread(self, event=None):
        if self.input_box.cget("state") == "normal":
            threading.Thread(target=self.ask_ai, daemon=True).start()

    def ask_ai(self):
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
        self.chatbox.configure(state="normal")
        self.chatbox.insert("end", f"{sender}:\n{message}\n\n")
        self.chatbox.configure(state="disabled")
        self.chatbox.see("end")

if __name__ == "__main__":
    os.makedirs("output_docs", exist_ok=True)
    os.makedirs("chroma_cache", exist_ok=True)
    app = BookAlchemistApp()
    app.mainloop()