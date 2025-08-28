# BookAlchemist/modules/styling_engine.py

class StylingEngine:
    """
    Converts a structured content list into a styled HTML document
    based on a selected theme.
    """
    def __init__(self, structured_content):
        """
        Initializes the engine with the content to be styled.
        """
        self.content = structured_content

    def _get_theme_css(self, theme_name="classic_scholar"):
        """
        Returns the CSS styles for a given theme name.
        In a real app, this might load from .css files.
        For now, we'll define them directly in the code.
        """
        if theme_name == "classic_scholar":
            return """
            @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700&display=swap');
            
            body {
                font-family: 'Cormorant Garamond', serif;
                line-height: 1.6;
                margin: 2in 1.5in; /* Generous margins for a book feel */
                background-color: #fdfaf3; /* Creamy paper color */
                color: #333;
            }
            .chapter_title {
                font-size: 2.5em;
                font-weight: bold;
                margin-top: 3em;
                margin-bottom: 1.5em;
                text-align: center;
                page-break-before: always; /* Each chapter on a new page */
            }
            .heading {
                font-size: 1.5em;
                font-weight: bold;
                margin-top: 2em;
                margin-bottom: 1em;
                text-align: center;
            }
            .paragraph {
                text-indent: 2em; /* Indent first line of paragraphs */
                margin-bottom: 0.5em;
                text-align: justify;
            }
            /* Add a drop cap to the first paragraph after a chapter title */
            .chapter_title + .paragraph::first-letter {
                font-size: 4em;
                float: left;
                padding-right: 0.1em;
                line-height: 0.8;
                margin-top: 0.05em;
            }
            """
        # --- Placeholder for a second theme ---
        elif theme_name == "modern_minimalist":
            return """
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

            body {
                font-family: 'Inter', sans-serif;
                line-height: 1.5;
                margin: 1.5in 1in;
                background-color: #ffffff;
                color: #111;
            }
            .chapter_title {
                font-size: 2em;
                font-weight: 700;
                margin-top: 2.5em;
                margin-bottom: 2em;
                border-bottom: 1px solid #ddd;
                padding-bottom: 0.5em;
                page-break-before: always;
            }
            .heading {
                font-size: 1.25em;
                font-weight: 700;
                margin-top: 1.5em;
                margin-bottom: 0.75em;
            }
            .paragraph {
                margin-bottom: 1em;
                text-align: left;
            }
            """
        else:
            # Default fallback theme (very basic)
            return "body { font-family: sans-serif; margin: 1in; }"


    def generate_html(self, theme_name="classic_scholar", book_title="My Book"):
        """
        Generates the full HTML string for the document.

        Args:
            theme_name (str): The name of the theme to apply.
            book_title (str): The title to be used for the HTML document.

        Returns:
            str: A complete HTML document as a string.
        """
        
        css_styles = self._get_theme_css(theme_name)
        
        html_body_parts = []
        for block in self.content:
            block_type = block['type']
            block_content = block['content']

            # Sanitize content for HTML
            # This is a basic sanitation, a real app would use a library like 'bleach'
            block_content = block_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            # Map our content type to an HTML tag and a CSS class
            if block_type == 'chapter_title':
                html_body_parts.append(f'<h1 class="chapter_title">{block_content}</h1>')
            elif block_type == 'heading':
                html_body_parts.append(f'<h2 class="heading">{block_content}</h2>')
            elif block_type == 'paragraph':
                html_body_parts.append(f'<p class="paragraph">{block_content}</p>')
            # We can add more types here later (e.g., blockquotes, lists)

        body_content = "\n".join(html_body_parts)

        # Assemble the final HTML document
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{book_title}</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            {body_content}
        </body>
        </html>
        """
        
        return html_template