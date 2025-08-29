# BookAlchemist/modules/pdf_parser.py

import fitz
import re
# (We no longer need the OCR libraries in this specific file)

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(file_path)

    def extract_structured_content(self):
        """
        Extracts content and structures it, now with a heuristic to detect
        indented code blocks.
        """
        structured_content = []
        full_text = ""
        for page in self.doc:
            full_text += page.get_text() + "\n"
        
        lines = full_text.split('\n')
        current_paragraph = ""

        for line in lines:
            stripped_line = line.strip()

            # --- NEW HEURISTIC FOR CODE BLOCKS ---
            # If a line is indented (e.g., starts with 4 spaces), we treat it
            # as a potential code block.
            if line.startswith('    '):
                # If we were building a regular paragraph, save it first.
                if current_paragraph:
                    structured_content.append({'type': 'paragraph', 'content': current_paragraph.strip()})
                    current_paragraph = ""
                # Add the line as-is (preserving indentation) to a code block.
                # We use a special marker to distinguish it.
                structured_content.append({'type': 'code_line', 'content': line})
                continue

            # If we hit a non-indented line, the potential code block is over.
            # Now, process the non-code line.
            if not stripped_line:
                if current_paragraph:
                    structured_content.append({'type': 'paragraph', 'content': current_paragraph.strip()})
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
        
        # --- Post-processing to group consecutive code lines ---
        final_content = []
        i = 0
        while i < len(structured_content):
            block = structured_content[i]
            if block['type'] == 'code_line':
                code_block_content = []
                # Group all subsequent code_line blocks together
                while i < len(structured_content) and structured_content[i]['type'] == 'code_line':
                    code_block_content.append(structured_content[i]['content'])
                    i += 1
                # Add the combined lines as a single 'code_block'
                final_content.append({'type': 'code_block', 'content': '\n'.join(code_block_content)})
            else:
                final_content.append(block)
                i += 1
        
        return final_content

    def close(self):
        self.doc.close()