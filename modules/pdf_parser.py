# BookAlchemist/modules/pdf_parser.py

import fitz  # PyMuPDF
import re

class PDFParser:
    """
    A class to parse a PDF document, extract its text, and identify
    basic structural elements like chapter headings.
    """
    def __init__(self, file_path):
        """
        Initializes the parser with the path to the PDF file.
        """
        self.file_path = file_path
        self.doc = fitz.open(file_path)

    def extract_structured_content(self):
        """
        Extracts content and structures it into a list of dictionaries.
        Each dictionary represents a content block (e.g., a title or a paragraph).

        Returns:
            list: A list of dictionaries, e.g.,
                  [{'type': 'title', 'content': 'Chapter 1'}, {'type': 'paragraph', 'content': '...'}]
        """
        structured_content = []
        full_text = ""

        # First, concatenate all text to handle paragraphs spanning across pages
        for page in self.doc:
            full_text += page.get_text() + "\n"
        
        # Split the text into lines and process them
        lines = full_text.split('\n')
        current_paragraph = ""

        for line in lines:
            stripped_line = line.strip()

            if not stripped_line:
                # An empty line often signifies the end of a paragraph
                if current_paragraph:
                    structured_content.append({
                        'type': 'paragraph',
                        'content': current_paragraph.strip()
                    })
                    current_paragraph = ""
                continue

            # --- Heuristics for Structure Detection ---
            # This is the "secret sauce". We make educated guesses.

            # Heuristic 1: Detect Chapter Titles (e.g., "Chapter 1", "CHAPTER IX")
            if re.match(r'^CHAPTER \d+|^\w*CHAPTER [IVXLCDM]+', stripped_line, re.IGNORECASE):
                # If we were building a paragraph, save it first
                if current_paragraph:
                    structured_content.append({'type': 'paragraph', 'content': current_paragraph.strip()})
                    current_paragraph = ""
                
                structured_content.append({'type': 'chapter_title', 'content': stripped_line})
            
            # Heuristic 2: Simple heading detection (e.g., a short, all-caps line)
            elif len(stripped_line.split()) < 7 and stripped_line.isupper():
                if current_paragraph:
                    structured_content.append({'type': 'paragraph', 'content': current_paragraph.strip()})
                    current_paragraph = ""
                
                structured_content.append({'type': 'heading', 'content': stripped_line})

            else:
                # If it's not a title or heading, it's part of a paragraph
                current_paragraph += line + " "

        # Add the last remaining paragraph if it exists
        if current_paragraph:
            structured_content.append({'type': 'paragraph', 'content': current_paragraph.strip()})
            
        return structured_content

    def close(self):
        """Closes the document."""
        self.doc.close()