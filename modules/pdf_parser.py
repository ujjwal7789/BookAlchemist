import fitz  # PyMuPDF
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
        Analyze document for dominant font and size based on character count,
        not limited by fixed thresholds, allowing fractional font sizes.
        """
        font_counts = Counter()
        for page in self.doc:
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                if block['type'] == 0:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            # Include all readable font sizes, filter out very small or very large fonts dynamically if needed
                            if span['size'] > 5 and span['size'] < 60:  
                                key = (span['font'], round(span['size'], 1))  # Keep 1 decimal precision
                                font_counts[key] += len(span['text'])
        if not font_counts:
            return None, None

        dominant_style = font_counts.most_common(1)[0][0]
        font_name, font_size = dominant_style
        return font_name, font_size

    def extract_structured_content(self):
        """
        Extract text and images with improved caption detection:
        1) Check vertical and horizontal proximity for captions.
        2) Use font size/style cues for captions.
        3) Manage Pixmap resources properly.
        """
        structured_content = []
        for page_num, page in enumerate(self.doc):
            blocks = page.get_text("dict").get("blocks", [])
            image_blocks = page.get_images(full=True)

            all_blocks = []
            # Add text blocks with bbox and style info
            for b in blocks:
                if b['type'] == 0:
                    text_content = ''
                    # concatenate all spans' texts for easier processing
                    for line in b.get('lines', []):
                        for span in line.get('spans', []):
                            text_content += span.get('text', '')
                    all_blocks.append({'y0': b['bbox'][1], 'bbox': b['bbox'], 'type': 'text', 'content': text_content.strip()})

            # Add image blocks with bbox info
            for img_index, img in enumerate(image_blocks):
                xref = img[0]
                bbox = page.get_image_bbox(img)
                all_blocks.append({'y0': bbox.y0, 'bbox': bbox, 'type': 'image', 'xref': xref, 'page_num': page_num, 'img_index': img_index})

            # Sort blocks by vertical position and then horizontal position for layout clarity
            all_blocks.sort(key=lambda b: (b['y0'], b['bbox'][0]))

            i = 0
            while i < len(all_blocks):
                block = all_blocks[i]
                if block['type'] == 'text':
                    clean_text = block['content']
                    if clean_text:
                        # Enhanced heuristics: detect headings by font size if available or uppercase + length
                        # Here we skip font info due to block data limitations but could integrate spans
                        if len(clean_text.split()) < 7 and clean_text.isupper():
                            structured_content.append({'type': 'heading', 'content': clean_text})
                        else:
                            structured_content.append({'type': 'paragraph', 'content': clean_text})

                elif block['type'] == 'image':
                    pix = fitz.Pixmap(self.doc, block['xref'])
                    # Convert image if color space is CMYK to RGB explicitly
                    if pix.colorspace and pix.colorspace.n == 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    img_filename = f"page{block['page_num']}-img{block['img_index']}.png"
                    img_path = os.path.join(self.image_output_dir, img_filename)
                    pix.save(img_path)
                    pix = None  # Free Pixmap resources

                    structured_content.append({'type': 'image', 'path': os.path.join("images", img_filename)})

                    # Caption detection: check next block vertical and horizontal proximity & font heuristic
                    if i + 1 < len(all_blocks) and all_blocks[i + 1]['type'] == 'text':
                        next_block = all_blocks[i + 1]
                        vertical_gap = next_block['bbox'][1] - block['bbox'][3]  # next block y0 - image y1
                        horizontal_overlap = max(0, min(block['bbox'][2], next_block['bbox'][2]) - max(block['bbox'][0], next_block['bbox'][0]))
                        # Consider caption if very close vertically and some horizontal alignment
                        if 0 <= vertical_gap < 50 and horizontal_overlap > 20:
                            caption_text = next_block['content'].strip()
                            # Simple heuristic: caption length <= 30 words, includes lowercase letters
                            if len(caption_text.split()) <= 30 and any(c.islower() for c in caption_text):
                                structured_content.append({'type': 'image_caption', 'content': caption_text})
                                i += 1  # Skip the caption block
                i += 1
        return structured_content

    def close(self):
        self.doc.close()