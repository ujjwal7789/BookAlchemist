# BookAlchemist/modules/pdf_parser.py

import fitz  # PyMuPDF
import re
import pytesseract
from PIL import Image
import io

# Optional: If tesseract is not in your PATH, include the following line
# pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
# For example, on Windows:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(file_path)

    def _get_page_text(self, page):
        """
        Extracts text from a page, falling back to OCR if needed.
        """
        # First, try the fast, direct text extraction
        direct_text = page.get_text()
        
        # Heuristic: If direct text is very short (less than 100 characters),
        # it might be a scanned page. Let's try OCR.
        if len(direct_text.strip()) > 100:
            return direct_text
        
        print(f"  -> Page {page.number + 1}: Low text detected. Attempting OCR...")
        try:
            # Render the page to an image (pixmap)
            pix = page.get_pixmap(dpi=300) # Higher DPI for better OCR
            img_data = pix.tobytes("png")
            
            # Open the image data with Pillow
            image = Image.open(io.BytesIO(img_data))
            
            # Use Tesseract to extract text from the image
            ocr_text = pytesseract.image_to_string(image)
            
            # OCR is often more accurate, so we prefer it if it returns significant text
            if len(ocr_text.strip()) > len(direct_text.strip()):
                print(f"  -> OCR successful on page {page.number + 1}.")
                return ocr_text
            else:
                return direct_text # Fallback to original if OCR was poor

        except Exception as e:
            print(f"  -> OCR failed on page {page.number + 1}: {e}")
            return direct_text # Return whatever we got if OCR fails

    def extract_structured_content(self):
        structured_content = []
        full_text = ""

        print("Extracting text from PDF (with OCR fallback)...")
        for i, page in enumerate(self.doc):
            print(f"Processing page {i+1}/{len(self.doc)}...")
            full_text += self._get_page_text(page) + "\n"
        
        print("Text extraction complete. Structuring content...")
        # ... (The rest of this method, including the heuristics and post-processing, is THE SAME)
        lines = full_text.split('\n')
        current_paragraph = ""

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                if current_paragraph:
                    structured_content.append({
                        'type': 'paragraph',
                        'content': current_paragraph.strip()
                    })
                    current_paragraph = ""
                continue

            if re.match(r'^CHAPTER \d+|^\w*CHAPTER [IVXLCDM]+', stripped_line, re.IGNORECASE):
                if current_paragraph:
                    structured_content.append({'type': 'paragraph', 'content': current_paragraph.strip()})
                    current_paragraph = ""
                structured_content.append({'type': 'chapter_title', 'content': stripped_line})
            
            elif len(stripped_line.split()) < 7 and stripped_line.isupper() and not re.search(r'\d', stripped_line):
                if current_paragraph:
                    structured_content.append({'type': 'paragraph', 'content': current_paragraph.strip()})
                    current_paragraph = ""
                structured_content.append({'type': 'heading', 'content': stripped_line})
            else:
                current_paragraph += line + " "

        if current_paragraph:
            structured_content.append({'type': 'paragraph', 'content': current_paragraph.strip()})
        
        cleaned_content = []
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