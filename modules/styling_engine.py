# BookAlchemist/modules/styling_engine.py

import random
import os
from pathlib import Path

class StylingEngine:
    def __init__(self, structured_content):
        self.content = structured_content

    def generate_html(self, theme_name="classic_scholar", book_title="My Book"):
        css_styles = self._get_theme_css(theme_name)
        
        # Dispatch to the appropriate generator based on the theme
        if theme_name == "procedural_vintage":
            body_content = self._generate_paged_html_procedural()
        else:
            body_content = self._generate_standard_html()

        html_template = f"""
        <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{book_title}</title><style>{css_styles}</style></head>
        <body>{body_content}</body></html>
        """
        return html_template

    def _generate_standard_html(self):
        html_body_parts = []
        for block in self.content:
            block_type = block['type']
            
            if block_type in ['paragraph', 'chapter_title', 'heading', 'code_block']:
                block_content = block['content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                if block_type == 'paragraph':
                    html_body_parts.append(f'<p class="paragraph">{block_content}</p>')
                elif block_type == 'chapter_title':
                    html_body_parts.append(f'<h1 class="chapter_title">{block_content}</h1>')
                elif block_type == 'heading':
                    html_body_parts.append(f'<h2 class="heading">{block_content}</h2>')
                elif block_type == 'code_block':
                    html_body_parts.append(f'<pre class="code_block"><code>{block_content}</code></pre>')

            elif block_type == 'image':
                # --- THE FINAL, DEFINITIVE FIX: EMBED IMAGE DATA DIRECTLY ---
                relative_image_path = os.path.join("output_docs", block['path'])
                absolute_image_path = os.path.abspath(relative_image_path)
                
                try:
                    # 1. Read the image file in binary mode
                    with open(absolute_image_path, "rb") as image_file:
                        # 2. Encode the binary data into a Base64 string
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    
                    # 3. Create a Data URI
                    # The format is "data:[<mediatype>];base64,[<data>]"
                    image_url = f"data:image/png;base64,{encoded_string}"
                    
                    # 4. Use this Data URI in the image tag
                    html_body_parts.append(f'<div class="image-container"><img src="{image_url}" class="embedded-image"></div>')
                
                except FileNotFoundError:
                    print(f"Warning: Image file not found at {absolute_image_path}. Skipping.")
                    continue
        
        return "\n".join(html_body_parts)

    
    # ... (the procedural generator is unchanged) ...
    def _generate_paged_html_procedural(self):
        # This implementation remains the same, but it won't render code blocks.
        # Could be extended to support them if needed.
        # ... (code from previous versions) ...
        pass

    def _get_theme_css(self, theme_name="classic_scholar"):
        # --- THEME 1: CLASSIC SCHOLAR (Unchanged) ---
       # --- THEME 1: CLASSIC SCHOLAR ---
        if theme_name == "classic_scholar":
            return """
            @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700&display=swap');
            
            @page {
                /* --- CHANGE: Reduced margins for the new paper size --- */
                margin: 1in; 
            }

            body {
                font-family: 'Cormorant Garamond', serif; font-size: 14pt;
                line-height: 1.8; margin: 0;
                background-color: #fdfaf3; color: #333;
            }
            .chapter_title { font-size: 2.5em; font-weight: bold; margin-top: 1em; margin-bottom: 1.5em; text-align: center; page-break-before: always; }
            /* ... (rest of the CSS is the same) ... */
            """

        # --- THEME 2: PROCEDURAL VINTAGE (UPDATED MARGINS) ---
        elif theme_name == "procedural_vintage":
            return """
            @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English&display=swap');
            
            @page {
                /* --- CHANGE: Reduced margins for the new paper size --- */
                margin: 1in;
            }

            body {
                font-family: 'IM Fell English', serif; font-size: 13pt;
                line-height: 1.7; color: #3b2f2f; margin: 0;
                background-color: #333;
            }
            """

        

        # --- NEW THEME 3: ACADEMIC JOURNAL ---
        elif theme_name == "academic_journal":
            return """
            @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
            body {
                font-family: 'Lato', sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                margin: 1in;
                background-color: #ffffff;
                color: #222;
            }
            .chapter_title { font-size: 2em; font-weight: 700; margin-top: 2em; margin-bottom: 1em; border-bottom: 2px solid #333; padding-bottom: 0.25em; }
            .heading { font-size: 1.5em; font-weight: 700; margin-top: 1.5em; margin-bottom: 0.5em; }
            .paragraph { margin-bottom: 1em; text-align: justify; }
            """

        # --- NEW THEME 4: CODING MANUAL ---
        elif theme_name == "coding_manual":
            return """
            @import url('https://fonts.googleapis.com/css2?family=Fira+Code&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            body {
                font-family: 'Roboto', sans-serif;
                font-size: 12pt;
                line-height: 1.7;
                margin: 1in;
                background-color: #f7f7f7;
                color: #333;
            }
            .chapter_title { font-size: 2.2em; font-weight: 700; color: #005A9C; margin-top: 2em; margin-bottom: 1em; }
            .heading { font-size: 1.6em; font-weight: 700; color: #005A9C; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; margin-top: 1.5em; margin-bottom: 0.75em; }
            .paragraph { margin-bottom: 1.2em; }
            .code_block {
                font-family: 'Fira Code', monospace;
                font-size: 10pt;
                background-color: #2d2d2d; /* Dark background for code */
                color: #f1f1f1; /* Light text for code */
                padding: 1em;
                border-radius: 5px;
                overflow-x: auto; /* Allow horizontal scrolling */
                white-space: pre-wrap; /* Preserve whitespace and wrap lines */
            }
            """
        else:
            return "body { font-family: sans-serif; margin: 1in; }"