# BookAlchemist/modules/styling_engine.py

import random

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
            block_content = block['content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            if block_type == 'chapter_title':
                html_body_parts.append(f'<h1 class="chapter_title">{block_content}</h1>')
            elif block_type == 'heading':
                html_body_parts.append(f'<h2 class="heading">{block_content}</h2>')
            elif block_type == 'paragraph':
                html_body_parts.append(f'<p class="paragraph">{block_content}</p>')
            # --- NEW: Handle the code block type ---
            elif block_type == 'code_block':
                # Use <pre><code> for semantic correctness and to preserve whitespace
                html_body_parts.append(f'<pre class="code_block"><code>{block_content}</code></pre>')
        
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
            body {
                font-family: 'Cormorant Garamond', serif; font-size: 14pt;
                line-height: 1.8; margin: 2.5in 2in;
                background-color: #fdfaf3; color: #333;
            }
            .chapter_title { font-size: 2.5em; font-weight: bold; margin-top: 3em; margin-bottom: 1.5em; text-align: center; page-break-before: always; }
            .heading { font-size: 1.5em; font-weight: bold; margin-top: 2em; margin-bottom: 1em; text-align: center; }
            .paragraph { text-indent: 2em; margin-bottom: 0.5em; text-align: justify; }
            .chapter_title + .paragraph::first-letter { font-size: 4em; float: left; padding-right: 0.1em; line-height: 0.8; margin-top: 0.05em; }
            """

        # --- THEME 2: PROCEDURAL VINTAGE (Unchanged) ---
        elif theme_name == "modern_minimalist":
            return """
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            body { font-family: 'Inter', sans-serif; line-height: 1.5; margin: 1.5in 1in; background-color: #ffffff; color: #111; }
            .chapter_title { font-size: 2em; font-weight: 700; margin-top: 2.5em; margin-bottom: 2em; border-bottom: 1px solid #ddd; padding-bottom: 0.5em; page-break-before: always; }
            .heading { font-size: 1.25em; font-weight: 700; margin-top: 1.5em; margin-bottom: 0.75em; }
            .paragraph { margin-bottom: 1em; text-align: left; }
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
                margin: 1in 1.25in;
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