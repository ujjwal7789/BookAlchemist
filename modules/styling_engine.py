# BookAlchemist/modules/styling_engine.py

from pathlib import Path
import base64
import os

class StylingEngine:
    def __init__(self, structured_content):
        self.content = structured_content

    def generate_html(self, theme_name, book_title, dominant_font=None):
        css_styles = self._get_theme_css(theme_name, dominant_font)
        
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
            
            if block_type in ['paragraph', 'chapter_title', 'heading', 'code_block', 'image_caption']:
                block_content = block['content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                if block_type == 'paragraph':
                    html_body_parts.append(f'<p class="paragraph">{block_content}</p>')
                elif block_type == 'chapter_title':
                    html_body_parts.append(f'<h1 class="chapter_title">{block_content}</h1>')
                elif block_type == 'heading':
                    html_body_parts.append(f'<h2 class="heading">{block_content}</h2>')
                elif block_type == 'code_block':
                    html_body_parts.append(f'<pre class="code_block"><code>{block_content}</code></pre>')
                elif block_type == 'image_caption':
                    html_body_parts.append(f'<p class="image-caption">{block_content}</p>')

            elif block_type == 'image':
                # Embed image data directly using Data URIs for robustness
                relative_image_path = os.path.join("output_docs", block['path'])
                absolute_image_path = os.path.abspath(relative_image_path)
                try:
                    with open(absolute_image_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    image_url = f"data:image/png;base64,{encoded_string}"
                    html_body_parts.append(f'<div class="image-container"><img src="{image_url}" class="embedded-image"></div>')
                except FileNotFoundError:
                    continue
        return "\n".join(html_body_parts)

    def _get_theme_css(self, theme_name, dominant_font=None):
        base_font_override = ""
        if dominant_font:
            # If a dominant font was found, we inject it as a high-priority rule.
            base_font_override = f"body {{ font-family: '{dominant_font}', serif !important; }}"

        if theme_name == "premium_novel":
            return base_font_override + """
            @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;700&display=swap');
            @page { 
                margin: 1.25in 1in;
                @bottom-center {
                    content: counter(page);
                    font-size: 10pt;
                    color: #666;
                }
            }
            body {
                font-family: 'EB Garamond', serif;
                font-size: 12pt;
                line-height: 1.6;
                color: #222;
                background-color: #fdfaf3;
                margin: 0;
            }
            h1.chapter_title {
                font-size: 2.5em;
                font-weight: 400;
                text-align: center;
                margin-top: 2em;
                margin-bottom: 2em;
                page-break-before: always;
            }
            h1.chapter_title + p.paragraph::first-letter {
                font-size: 4em;
                float: left;
                line-height: 0.8;
                padding-right: 0.1em;
                margin-top: 0.05em;
            }
            p.paragraph {
                text-align: justify;
                text-indent: 2em;
                margin-bottom: 0.2em;
                hyphens: auto;
                font-variant-ligatures: common-ligatures;
            }
            .image-container { text-align: center; margin: 2em 0; page-break-inside: avoid; }
            .embedded-image { max-width: 90%; height: auto; border: 1px solid #ddd; }
            .image-caption { text-align: center; font-style: italic; font-size: 0.9em; color: #555; margin-top: 0.5em; }
            """

        elif theme_name == "formal_textbook":
            return base_font_override + """
            @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;700&family=Source+Code+Pro&display=swap');
            @page { 
                margin: 1in;
                @bottom-right { content: counter(page); font-size: 9pt; color: #888; }
            }
            body {
                font-family: 'Source Sans 3', sans-serif;
                font-size: 11pt;
                line-height: 1.7;
                color: #111;
                background-color: #fff;
                margin: 0;
            }
            h1.chapter_title {
                font-size: 2.5em;
                font-weight: 700;
                color: #2a3a7d;
                border-bottom: 2px solid #2a3a7d;
                padding-bottom: 0.3em;
                margin-top: 1.5em;
                margin-bottom: 1.5em;
            }
            h2.heading {
                font-size: 1.8em;
                font-weight: 700;
                color: #333;
                border-bottom: 1px solid #ccc;
                padding-bottom: 0.2em;
                margin-top: 2em;
                margin-bottom: 1em;
            }
            p.paragraph { text-align: left; margin-bottom: 1.2em; }
            pre.code_block {
                font-family: 'Source Code Pro', monospace;
                font-size: 9.5pt;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 1em;
                overflow-x: auto;
                white-space: pre-wrap;
            }
            .image-container { text-align: center; margin: 2em 0; page-break-inside: avoid; }
            .embedded-image { max-width: 90%; height: auto; border: 1px solid #eee; }
            .image-caption { text-align: center; font-weight: 700; font-size: 0.9em; color: #444; margin-top: 0.5em; }
            """
        
        else: # Fallback to a clean default
            return "body { font-family: sans-serif; margin: 1in; }"