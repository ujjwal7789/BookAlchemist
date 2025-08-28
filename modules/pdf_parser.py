# BookAlchemist/modules/pdf_parser.py

import fitz
import re
import pytesseract
from PIL import Image
import io

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(file_path)

    # ... _get_page_text method remains unchanged ...
    def _get_page_text(self, page):
        # ... (no changes here) ...
        direct_text = page.get_text()
        if len(direct_text.strip()) > 100:
            return direct_text
        print(f"  -> Page {page.number + 1}: Low text detected. Attempting OCR...")
        try:
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            ocr_text = pytesseract.image_to_string(image)
            if len(ocr_text.strip()) > len(direct_text.strip()):
                print(f"  -> OCR successful on page {page.number + 1}.")
                return ocr_text
            else:
                return direct_text
        except Exception as e:
            print(f"  -> OCR failed on page {page.number + 1}: {e}")
            return direct_text

    def _format_dialogue(self, text):
        """
        A simple heuristic to format dialogue.
        Replaces '", "' with a newline to split consecutive quotes.
        """
        return text.replace('", "', '"\n\n"')

    def extract_structured_content(self):
        # ... (first part of the method is unchanged) ...
        structured_content = []
        full_text = ""
        print("Extracting text from PDF (with OCR fallback)...")
        for i, page in enumerate(self.doc):
            print(f"Processing page {i+1}/{len(self.doc)}...")
            full_text += self._get_page_text(page) + "\n"
        print("Text extraction complete. Structuring content...")
        
        lines = full_text.split('\n')
        current_paragraph = ""

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                if current_paragraph:
                    # --- MODIFIED: Apply dialogue formatting here ---
                    formatted_para = self._format_dialogue(current_paragraph.strip())
                    structured_content.append({
                        'type': 'paragraph',
                        'content': formatted_para
                    })
                    current_paragraph = ""
                continue
            
            # ... (the rest of the loop for titles/headings is the same) ...
            if re.match(r'^CHAPTER \d+|^\w*CHAPTER [IVXLCDM]+', stripped_line, re.IGNORECASE):
                if current_paragraph:
                    formatted_para = self._format_dialogue(current_paragraph.strip())
                    structured_content.append({'type': 'paragraph', 'content': formatted_para})
                    current_paragraph = ""
                structured_content.append({'type': 'chapter_title', 'content': stripped_line})
            elif len(stripped_line.split()) < 7 and stripped_line.isupper() and not re.search(r'\d', stripped_line):
                if current_paragraph:
                    formatted_para = self._format_dialogue(current_paragraph.strip())
                    structured_content.append({'type': 'paragraph', 'content': formatted_para})
                    current_paragraph = ""
                structured_content.append({'type': 'heading', 'content': stripped_line})
            else:
                current_paragraph += line + " "

        if current_paragraph:
            # --- MODIFIED: Apply dialogue formatting for the final paragraph ---
            formatted_para = self._format_dialogue(current_paragraph.strip())
            structured_content.append({'type': 'paragraph', 'content': formatted_para})
        
        # ... (the post-processing step for ghost chapters is unchanged) ...
        cleaned_content = []
        # ... (rest of the method is the same) ...
        i = 0
        while i < len(structured_content):
            current_block = structured_content[i]
            next_block = structured_content[i + 1] if i + 1 < len(structured_content) else None
            is_ghost_chapter = (
                current_block['type'] == 'chapter_title' and 
                next_block and 
                next_block['type'] == 'chapter_title'
            )
            if not is_ghost_chapter:
                cleaned_content.append(current_block)
            i += 1
            
        return cleaned_content

    def close(self):
        self.doc.close()