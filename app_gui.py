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
        self.active_ai_book = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- UI Frames ---
        # --- Frame 1: Combined File Selection and Processing ---
        # This frame now holds our single, smart button.
        process_frame = ctk.CTkFrame(self)
        process_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        process_frame.grid_columnconfigure(0, weight=1) # Make the button's column expandable

        # --- NEW "SMART" BUTTON ---
        # It starts by selecting a file, and its command will change later.
        self.process_button = ctk.CTkButton(
            process_frame,
            text="1. Select a Book to Process",
            height=40, # Make the button taller
            command=self.select_and_process
        )
        self.process_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew") # sticky="ew" makes it span horizontally

        self.file_label = ctk.CTkLabel(process_frame, text="Welcome to Book Alchemist!", text_color="gray", anchor="w")
        self.file_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # --- Frame 2: Styling Options ---
        style_frame = ctk.CTkFrame(self)
        style_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.theme_label = ctk.CTkLabel(style_frame, text="Theme:")
        self.theme_label.grid(row=0, column=0, padx=10, pady=10)

        self.theme_menu = ctk.CTkOptionMenu(style_frame, values=["classic_scholar", "procedural_vintage"])
        self.theme_menu.grid(row=0, column=1, padx=10, pady=10)

        # --- Frame 3: AI Chat ---
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

    def select_and_process(self):
        """NEW: This single function handles both selecting a file and starting the processing."""
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path = path
            self.file_label.configure(text=f"Selected: {os.path.basename(path)}", text_color="white")
            self.add_message("System", f"Selected book: {os.path.basename(path)}")
            
            # Now that a file is selected, immediately start the processing thread
            self.start_processing_thread()

    def start_processing_thread(self):
        # Disable the main button to prevent multiple clicks
        self.process_button.configure(state="disabled", text="Processing...")
        self.input_box.configure(state="disabled")
        self.send_button.configure(state="disabled")
        
        # Start the backend processing in a new thread
        threading.Thread(target=self.process_book, daemon=True).start()
    
    def process_book(self):
        selected_book_name = os.path.basename(self.pdf_path)
        book_id = os.path.splitext(selected_book_name)[0].lower().replace(" ", "_")

        # --- PDF Parsing and Generation ---
        self.add_message("System", "Step 1: Parsing document...")
        parser = PDFParser(file_path=self.pdf_path)
        self.structured_content = parser.extract_structured_content()
        parser.close()
        self.add_message("System", "✅ Parsing complete.")

        theme = self.theme_menu.get()
        self.add_message("System", f"Step 2: Generating PDF with '{theme}' theme...")
        engine = StylingEngine(structured_content=self.structured_content)
        html = engine.generate_html(theme_name=theme, book_title=book_id)
        pdf_path = os.path.join("output_docs", f"{book_id}_{theme}.pdf")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(PDFGenerator.generate_pdf_from_html(html, pdf_path))
        loop.close()
        self.add_message("System", f"✅ PDF saved to {pdf_path}")
        
        # --- AI Ingestion Logic ---
        try:
            if not self.assistant:
                self.add_message("System", "Initializing AI models for the first time... (This is a one-time slow step)")
                self.assistant = AIAssistant()
            
            self.assistant.ingest_document(self.structured_content, book_id)
            self.active_ai_book = selected_book_name
            
            self.add_message("System", f"✅ AI Assistant is ready! You can now ask questions about '{self.active_ai_book}'.")
            self.input_box.configure(state="normal")
            self.send_button.configure(state="normal")
            # --- NEW: Update the main button's text and re-enable it ---
            self.process_button.configure(state="normal", text="Process a Different Book")
            
        except Exception as e:
            self.add_message("Error", f"Could not process book with AI: {e}")
            self.process_button.configure(state="normal", text="Error! Try a different book.")

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

        answer = self.assistant.ask(question)
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
    os.makedirs("chroma_cache", exist_ok=True) # Ensure cache directory exists
    app = BookAlchemistApp()
    app.mainloop()