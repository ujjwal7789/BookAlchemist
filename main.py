# BookAlchemist/main.py

import os
import asyncio
from modules.pdf_parser import PDFParser
from modules.styling_engine import StylingEngine
from modules.pdf_generator import PDFGenerator
from modules.ai_assistant import AIAssistant

def main():
    """
    Main entry point for the application.
    Sets up the document path and calls the processing function.
    """
    INPUT_DOC_NAME = "pride-and-prejudice.pdf"  # <-- CHANGE THIS to your PDF's filename
    
    doc_path = os.path.join("input_docs", INPUT_DOC_NAME)

    # Ensure output directory exists
    os.makedirs("output_docs", exist_ok=True)

    if not os.path.exists(doc_path):
        print(f"Error: The file was not found at {doc_path}")
        print("Please make sure the file exists in the 'input_docs' directory and the filename is correct.")
        return

    process_book(doc_path)


def process_book(file_path):
    """
    Runs the full pipeline: Parse -> Style -> Generate PDF -> Initialize AI.
    """
    print(f"--- 🚀 Starting to process: {os.path.basename(file_path)} ---")

    # --- Step 1: Parsing the PDF ---
    print("\n--- Step 1: Parsing Document ---")
    parser = PDFParser(file_path=file_path)
    try:
        # This is the structured content we will use for everything else.
        structured_content = parser.extract_structured_content()
        print(f"✅ Successfully parsed {len(structured_content)} content blocks.")
    except Exception as e:
        print(f"❌ Critical Error during parsing: {e}")
        print("Aborting process.")
        return
    finally:
        parser.close()

    if not structured_content:
        print("No content was extracted from the document. Aborting.")
        return

    # --- Step 2: Styling and PDF Generation ---
    print("\n--- Step 2: Generating Styled PDFs ---")
    engine = StylingEngine(structured_content=structured_content)
    book_title = os.path.splitext(os.path.basename(file_path))[0]
    
    themes_to_generate = ["classic_scholar", "procedural_vintage"]
    
    for theme in themes_to_generate:
        print(f"\nProcessing theme: {theme}")
        try:
            # Generate HTML
            final_html = engine.generate_html(theme_name=theme, book_title=book_title)
            
            # Generate PDF from HTML
            pdf_output_path = os.path.join("output_docs", f"{book_title}_{theme}.pdf")
            print(f"⏳ Generating PDF, this may take a moment...")
            
            success = asyncio.run(PDFGenerator.generate_pdf_from_html(final_html, pdf_output_path))
            
            if success:
                print(f"✅ Saved stylized PDF to: {pdf_output_path}")
            else:
                print(f"❌ Failed to generate PDF for theme: {theme}")

        except Exception as e:
            print(f"❌ An error occurred during processing for theme '{theme}': {e}")
            continue # Continue to the next theme if one fails

    # --- Step 3: Initialize and Interact with AI Assistant ---
    print("\n--- Step 3: Initializing Conversational AI ---")
    try:
        # We pass the 'structured_content' we successfully parsed in Step 1
        assistant = AIAssistant(structured_content=structured_content)
        
        print("\n--- 📖 Conversational Mode Activated ---")
        print("Ask anything about the book. Type 'exit' to quit.")
        
        while True:
            question = input("\nYour question: ")
            if question.lower().strip() == 'exit':
                print("Exiting conversational mode. Goodbye! 👋")
                break
            
            answer = assistant.ask(question)
            print(f"\nAI Assistant: {answer}")

    except Exception as e:
        print(f"\n❌ Could not initialize AI Assistant: {e}")
        print("Please check your OpenAI API key and environment setup in the .env file.")


if __name__ == "__main__":
    main()