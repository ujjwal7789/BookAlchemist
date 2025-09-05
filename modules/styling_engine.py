from pathlib import Path
import base64
import os
import html


class StylingEngine:
    def __init__(self, structured_content):
        self.content = structured_content

    def generate_html(self, theme_name, book_title, dominant_font=None):
        css_styles = self._get_theme_css(theme_name, dominant_font)
        body_content = self._generate_standard_html()
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <title>{html.escape(book_title)}</title>
            <style>{css_styles}</style>
          </head>
          <body>{body_content}</body>
        </html>
        """
        return html_template

    def _generate_standard_html(self):
        html_body_parts = []
        for block in self.content:
            block_type = block['type']

            # Safely escape HTML special characters in text content
            if block_type in ['paragraph', 'chapter_title', 'heading', 'code_block', 'image_caption']:
                block_content = html.escape(block['content'])

                if block_type == 'paragraph':
                    html_body_parts.append(f'<p class="paragraph">{block_content}</p>')
                elif block_type == 'chapter_title':
                    html_body_parts.append(f'<h1 class="chapter_title">{block_content}</h1>')
                elif block_type == 'heading':
                    html_body_parts.append(f'<h2 class="heading">{block_content}</h2>')
                elif block_type == 'code_block':
                    html_body_parts.append(f'<pre class="code_block"><code>{block_content}</code></pre>')
                elif block_type == 'image_caption':
                    # Use figcaption for semantic captioning (within figure below)
                    html_body_parts.append(f'<figcaption class="image-caption">{block_content}</figcaption>')

            elif block_type == 'image':
                # Encode image as data URI for portability
                relative_image_path = os.path.join("output_docs", block['path'])
                absolute_image_path = os.path.abspath(relative_image_path)

                try:
                    with open(absolute_image_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    image_url = f"data:image/png;base64,{encoded_string}"
                    # Wrap image and caption (if any) together with semantic <figure>
                    html_body_parts.append(f'<figure class="image-container"><img src="{image_url}" alt="Image" class="embedded-image"/>')
                    # Insert following block if it's an immediate caption (handled outside this method)
                    # But we rely on caption block separately appended; so no inline here.
                    html_body_parts.append('</figure>')
                except FileNotFoundError:
                    # Skip missing images gracefully
                    continue

        return "\n".join(html_body_parts)

    def _get_theme_css(self, theme_name, dominant_font=None):
        base_font_override = ""
        if dominant_font:
            # Inject dominant font with high priority if available
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
                font-size: 13pt; /* Slightly larger font for comfortable reading */
                line-height: 1.7; /* Relaxed line height */
                color: #222;
                background-color: #fdfaf3;
                margin: 0;
                -webkit-font-feature-settings: "liga", "clig", "calt"; /* Ligatures on */
                font-feature-settings: "liga", "clig", "calt";
                max-width: 38em; /* Limit line length for readable measure */
                margin-left: auto;
                margin-right: auto;
                padding: 1.5em 1em; /* Page padding */
            }
            h1.chapter_title {
                font-size: 2.8em;
                font-weight: 400;
                text-align: center;
                margin-top: 3em;
                margin-bottom: 3em;
                page-break-before: always;
                font-variant: small-caps;
                letter-spacing: 0.05em;
            }
            h1.chapter_title + p.paragraph::first-letter {
                font-size: 4.5em;
                font-weight: 700;
                float: left;
                line-height: 0.8;
                padding-right: 0.12em;
                margin-top: 0.05em;
                font-family: 'EB Garamond', serif;
                color: #4b4b4b;
                text-transform: uppercase;
            }
            p.paragraph {
                text-align: justify;
                text-indent: 2.5em;
                margin-bottom: 0.3em;
                hyphens: auto;
                font-variant-ligatures: common-ligatures;
                letter-spacing: 0.02em;
            }
            figure.image-container {
                text-align: center;
                margin: 3em 0;
                page-break-inside: avoid;
            }
            img.embedded-image {
                max-width: 90%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 6px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            figcaption.image-caption {
                text-align: center;
                font-style: italic;
                font-size: 0.95em;
                color: #555;
                margin-top: 0.6em;
                font-family: 'EB Garamond', serif;
            }
            """

        elif theme_name == "formal_textbook":
            return base_font_override + """
            @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;700&family=Source+Code+Pro&display=swap');
            @page {
                margin: 2em 2em;
                padding: 1em 1em;
                @bottom-right {
                    content: counter(page);
                    font-size: 9pt;
                    color: #888;
                }
            }
            body {
                font-family: 'Source Sans 3', sans-serif;
                font-size: 11pt;
                line-height: 1.75;
                color: #111;
                background-color: #fff;
                margin: 0;
                max-width: 48em; /* Wider measure for textbooks */
                margin-left: auto;
                margin-right: auto;
                padding: 2em 2em;
                -webkit-font-feature-settings: "liga", "clig";
                font-feature-settings: "liga", "clig";
            }
            h1.chapter_title {
                page-break-before: always
                font-size: 2.6em;
                font-weight: 700;
                color: #2a3a7d;
                border-bottom: 3px solid #2a3a7d;
                padding-bottom: 0.4em;
                margin-top: 2em;
                margin-bottom: 2em;
                page-break-before: always;
                font-variant: normal;
                letter-spacing: normal;
                text-transform: none;
                text-align: center
            }
            h2.heading {
                font-size: 1.9em;
                font-weight: 700;
                color: #333;
                border-bottom: 1.5px solid #ccc;
                padding-bottom: 0.3em;
                margin-top: 2.5em;
                margin-bottom: 1.2em;
            }
            p.paragraph {
                text-align: justify; 
                text-indent: 2em;
                hyphens: none;
                
                margin: auto;
            }
            pre.code_block {
                font-family: 'Source Code Pro', monospace;
                font-size: 9.5pt;
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 1em;
                overflow-x: auto;
                white-space: pre-wrap;
                margin-bottom: 1.5em;
            }
            figure.image-container {
                text-align: center;
                margin: 2.5em 0;
                page-break-inside: avoid;
            }
            img.embedded-image {
                max-width: 90%;
                height: auto;
                border: 1px solid #eee;
                box-shadow: none;
                border-radius: 3px;
            }
            figcaption.image-caption {
                font-weight: 700;
                text-align: center;
                font-size: 0.9em;
                color: #444;
                margin-top: 0.5em;
                font-family: 'Source Sans 3', sans-serif;
                font-style: normal;
            }
            """

        # Fallback simple style
        return "body { font-family: sans-serif; margin: 1in; }"
