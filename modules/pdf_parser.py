# BookAlchemist/modules/pdf_parser.py

import fitz # PyMuPDF
import os
from collections import Counter

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(file_path)
        self.image_output_dir = os.path.join("output_docs", "images")
        os.makedirs(self.image_output_dir, exist_ok=True)

    def find_dominant_font(self):
        """
        Analyzes the document to find the most used font and size for body text.
        This is a 'sure method' based on character count.
        """
        font_counts = Counter()
        for page in self.doc:
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                if block['type'] == 0: # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            # We only consider common paragraph-like font sizes
                            if 8 < span['size'] < 16:
                                key = f"{span['font']}|{round(span['size'])}"
                                font_counts[key] += len(span['text'])
        
        if not font_counts:
            return None, None
            
        # The dominant font is the one with the most characters
        dominant_style = font_counts.most_common(1)[0][0]
        font_name, font_size = dominant_style.split('|')
        return font_name, int(font_size)

    def extract_structured_content(self):
        """
        Extracts content, including images and now attempts to identify captions.
        """
        structured_content = []
        for page_num, page in enumerate(self.doc):
            blocks = page.get_text("blocks")
            image_blocks = page.get_images(full=True)

            all_blocks = []
            for b in blocks:
                all_blocks.append({'y0': b[1], 'type': 'text', 'content': b[4], 'bbox': b[0:4]})
            for img_index, img in enumerate(image_blocks):
                xref = img[0]
                bbox = page.get_image_bbox(img)
                all_blocks.append({'y0': bbox.y0, 'type': 'image', 'xref': xref, 'page_num': page_num, 'img_index': img_index})
            
            all_blocks.sort(key=lambda b: b['y0'])

            i = 0
            while i < len(all_blocks):
                block = all_blocks[i]
                if block['type'] == 'text':
                    clean_text = block['content'].strip()
                    if clean_text:
                        # Simple heuristics for titles and headings
                        if len(clean_text.split()) < 7 and clean_text.isupper():
                             structured_content.append({'type': 'heading', 'content': clean_text})
                        else:
                             structured_content.append({'type': 'paragraph', 'content': clean_text})
                
                elif block['type'] == 'image':
                    pix = fitz.Pixmap(self.doc, block['xref'])
                    if pix.n - pix.alpha >= 4: # CMYK -> RGB
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    
                    img_filename = f"page{block['page_num']}-img{block['img_index']}.png"
                    img_path = os.path.join(self.image_output_dir, img_filename)
                    pix.save(img_path)
                    
                    image_block = {'type': 'image', 'path': os.path.join("images", img_filename)}
                    structured_content.append(image_block)

                    # --- HEURISTIC FOR CAPTION DETECTION ---
                    # Check if the *next* block is text and close to this image.
                    if i + 1 < len(all_blocks) and all_blocks[i+1]['type'] == 'text':
                        next_block = all_blocks[i+1]
                        # If the next text block starts shortly after the image ends
                        if next_block['y0'] - block['y0'] < 100: 
                             caption_text = next_block['content'].strip()
                             structured_content.append({'type': 'image_caption', 'content': caption_text})
                             i += 1 # Skip the next block since we've consumed it as a caption
                i += 1
        return structured_content

    def close(self):
        self.doc.close()