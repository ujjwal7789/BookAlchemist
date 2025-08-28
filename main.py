# BookAlchemist/main.py

import os
import asyncio
from modules.pdf_parser import PDFParser
from modules.styling_engine import StylingEngine
from modules.pdf_generator import PDFGenerator

def process_book(file_path):
    """
    Main function to process a single book.
    """
    print(f"--- Starting to process: {os.path.basename(file_path)} ---")

    # 1. Initialize the parser with our PDF
    parser = PDFParser(file_path=file_path)
    content = []

    # 2. Extract the structured content
    try:
        content = parser.extract_structured_content()
        print(f"✅ Step 1: Successfully parsed {len(content)} content blocks from PDF.")
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        return # Stop processing if parsing fails
    finally:
        parser.close()

    if not content:
        print("No content was extracted. Aborting.")
        return

     # 2. Initialize the styling engine with the parsed content
    engine = StylingEngine(structured_content=content)

    book_title = os.path.splitext(os.path.basename(file_path))[0]
    
    # Let's generate HTML for both themes to compare
    themes_to_generate = ["classic_scholar", "modern_minimalist", "procedural_vintage"]
    
    for theme in themes_to_generate:
        print(f"\n--- Generating HTML for theme: {theme} ---")

        # 3. Generate the final HTML string
        try:
            final_html = engine.generate_html(theme_name=theme, book_title=book_title)
            print(f"✅ Step 2: Successfully generated HTML content.")

            # # 4. Save the HTML to a file in the output_docs directory
            # output_filename = f"{book_title}_{theme}.html"
            # output_path = os.path.join("output_docs", output_filename)
            
            # with open(output_path, "w", encoding="utf-8") as f:
            #     f.write(final_html)
            
            # print(f"✅ Step 3: Saved styled HTML to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error during HTML generation or saving: {e}"); continue

        pdf_output_path = os.path.join("output_docs", f"{book_title}_{theme}.pdf")

        print(f"⏳ Step 2b: Generating PDF, this may take a moment...")

        success = asyncio.run(PDFGenerator.generate_pdf_from_html(final_html, pdf_output_path))

        if success:
            print(f"✅ Step 2c: Saved stylized PDF to: {pdf_output_path}")

if __name__ == "__main__":
    INPUT_DOC_NAME = "PrideandPrejudice.pdf" # <-- CHANGE THIS to your PDF's filename
    
    doc_path = os.path.join("input_docs", INPUT_DOC_NAME)

    # Ensure output directory exists
    os.makedirs("output_docs", exist_ok=True)

    if os.path.exists(doc_path):
        process_book(doc_path)
    else:
        print(f"Error: File not found at {doc_path}")