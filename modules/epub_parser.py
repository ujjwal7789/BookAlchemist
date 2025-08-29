# BookAlchemist/modules/epub_parser.py

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

class EpubParser:
    """
    Parses an EPUB file and extracts its content into our standard
    structured format.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_structured_content(self):
        """
        Reads the EPUB, parses its XHTML chapters, and extracts text.
        """
        book = epub.read_epub(self.file_path)
        structured_content = []

        # EPUBs are made of "items". We want the HTML documents.
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            # The content is XHTML, so we use BeautifulSoup to parse it.
            soup = BeautifulSoup(item.get_body_content(), 'lxml')

            # Find all major text elements like headings and paragraphs
            # This is a simple heuristic. It can be made more advanced.
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'pre']):
                text = element.get_text().strip()
                if not text:
                    continue

                # Classify the block type based on its HTML tag
                if element.name in ['h1', 'h2']:
                    block_type = 'chapter_title'
                elif element.name in ['h3', 'h4']:
                    block_type = 'heading'
                elif element.name == 'pre':
                    block_type = 'code_block'
                else:
                    block_type = 'paragraph'
                
                structured_content.append({'type': block_type, 'content': text})
        
        return structured_content

    def close(self):
        # EbookLib doesn't require an explicit close. This is for API consistency.
        pass