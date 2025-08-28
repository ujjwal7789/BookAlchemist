# BookAlchemist/modules/styling_engine.py

import random

class StylingEngine:
    """
    Converts a structured content list into a styled HTML document.
    Supports standard themes and special procedural themes with random variations.
    """
    def __init__(self, structured_content):
        """
        Initializes the engine with the content to be styled.
        """
        self.content = structured_content

    def generate_html(self, theme_name="classic_scholar", book_title="My Book"):
        """
        Generates the full HTML string for the document.

        This method acts as a dispatcher, choosing the correct HTML generation
        strategy based on the selected theme.
        """
        css_styles = self._get_theme_css(theme_name)
        
        # Dispatch to the appropriate generator based on the theme
        if theme_name == "procedural_vintage":
            body_content = self._generate_paged_html_procedural()
        else:
            # All other themes use the standard, straightforward generator
            body_content = self._generate_standard_html()

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

    def _generate_standard_html(self):
        """Generates HTML for simple themes without complex page structures."""
        html_body_parts = []
        for block in self.content:
            block_type = block['type']
            # Basic HTML sanitation
            block_content = block['content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            if block_type == 'chapter_title':
                html_body_parts.append(f'<h1 class="chapter_title">{block_content}</h1>')
            elif block_type == 'heading':
                html_body_parts.append(f'<h2 class="heading">{block_content}</h2>')
            elif block_type == 'paragraph':
                html_body_parts.append(f'<p class="paragraph">{block_content}</p>')
        
        return "\n".join(html_body_parts)

    def _generate_paged_html_procedural(self):
        """
        Generates HTML for the procedural_vintage theme, grouping content
        into page divs and adding random defects.
        """
        pages = []
        current_page_content = []
        # Heuristic for page size: group ~20 paragraphs before creating a page div.
        # This is for distributing visual effects, not for actual pagination.
        paragraphs_per_page = 20 
        para_count = 0

        for block in self.content:
            block_type = block['type']
            block_content = block['content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Chapters always start a new page
            if block_type == 'chapter_title':
                if current_page_content:
                    pages.append(self._create_page_div(current_page_content))
                current_page_content = [f'<h1 class="chapter_title">{block_content}</h1>']
                para_count = 0
                continue

            # Add content to the current page buffer
            if block_type == 'heading':
                current_page_content.append(f'<h2 class="heading">{block_content}</h2>')
            elif block_type == 'paragraph':
                current_page_content.append(f'<p class="paragraph">{block_content}</p>')
                para_count += 1
            
            # When page buffer is "full", create the page div
            if para_count >= paragraphs_per_page:
                pages.append(self._create_page_div(current_page_content))
                current_page_content = []
                para_count = 0
        
        # Don't forget the last page!
        if current_page_content:
            pages.append(self._create_page_div(current_page_content))

        return "\n".join(pages)

    def _create_page_div(self, content_list):
        """
        Helper function to wrap content in a page div and inject
        randomly selected defect elements.
        """
        defect_classes = []
        # 15% chance to add a "coffee ring" type stain
        if random.random() < 0.15:
            defect_classes.append(random.choice(['stain-1', 'stain-2']))
        # 10% chance to add a "folded corner" crease
        if random.random() < 0.10:
            defect_classes.append('crease')
            
        page_content_html = "".join(content_list)
        defect_elements_html = "".join([f'<div class="{cls}"></div>' for cls in defect_classes])
        
        return f'<div class="page">{page_content_html}{defect_elements_html}</div>'

    def _get_theme_css(self, theme_name="classic_scholar"):
        """
        Returns the CSS styles for a given theme name.
        This is the central theme gallery.
        """
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

        # --- THEME 2: MODERN MINIMALIST ---
        elif theme_name == "modern_minimalist":
            return """
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            body { font-family: 'Inter', sans-serif; line-height: 1.5; margin: 1.5in 1in; background-color: #ffffff; color: #111; }
            .chapter_title { font-size: 2em; font-weight: 700; margin-top: 2.5em; margin-bottom: 2em; border-bottom: 1px solid #ddd; padding-bottom: 0.5em; page-break-before: always; }
            .heading { font-size: 1.25em; font-weight: 700; margin-top: 1.5em; margin-bottom: 0.75em; }
            .paragraph { margin-bottom: 1em; text-align: left; }
            """
        
        # --- THEME 3: PROCEDURAL VINTAGE (CSS ONLY) ---
        # elif theme_name == "procedural_vintage":
        #     return """
        #     @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English&display=swap');
        #     body {
        #         font-family: 'IM Fell English', serif; font-size: 13pt;
        #         line-height: 1.7; color: #3b2f2f; margin: 0;
        #         background-color: #333; /* Dark background for contrast with pages */
        #     }
        #     .page {
        #         background-color: #fdf8e8; /* Base paper color */
        #         background-image:
        #             radial-gradient(circle at 80% 20%, rgba(180, 160, 140, 0.15), transparent 40%),
        #             radial-gradient(circle at 15% 70%, rgba(180, 160, 140, 0.2), transparent 30%),
        #             linear-gradient(rgba(210, 190, 170, 0.1), rgba(210, 190, 170, 0.2));
        #         margin: 2.5in auto; /* Center the pages horizontally */
        #         padding: 1.5in;
        #         max-width: 8.5in; /* Simulate a standard paper width */
        #         min-height: 11in; /* Simulate a standard paper height */
        #         box-sizing: border-box; /* Include padding in width/height */
        #         box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        #         position: relative; overflow: hidden;
        #     }
        #     .page::before {
        #         content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        #         filter: sepia(0.2) contrast(0.9) brightness(1.05); pointer-events: none;
        #     }
        #     .chapter_title { font-size: 2.2em; text-align: center; margin-top: 1em; margin-bottom: 2em; page-break-before: always; }
        #     .heading { font-size: 1.5em; text-align: center; margin-top: 1.5em; margin-bottom: 1em; }
        #     .paragraph { text-indent: 2em; margin-bottom: 0.5em; text-align: justify; }
        #     .chapter_title + .paragraph::first-letter { font-size: 4em; float: left; padding-right: 0.1em; line-height: 0.8; margin-top: 0.05em; }

        #     /* Styles for Random Defect Variations */
        #     .stain, .crease { position: absolute; z-index: 0; /* Behind text */ }
        #     .stain-1 { width: 150px; height: 150px; top: 5%; right: 5%; border-radius: 50%; border: 2px solid rgba(110, 90, 70, 0.1); box-shadow: inset 0 0 40px rgba(110, 90, 70, 0.1); }
        #     .stain-2 { width: 80px; height: 80px; bottom: 10%; left: 5%; border-radius: 50%; border: 1px solid rgba(110, 90, 70, 0.08); box-shadow: inset 0 0 20px rgba(110, 90, 70, 0.15); }
        #     .crease { width: 300px; height: 300px; top: -50px; left: -50px; background: linear-gradient(45deg, rgba(0,0,0,0.0), rgba(0,0,0,0.08) 50%, rgba(0,0,0,0.0)); }
        #     """
        
        # --- DEFAULT FALLBACK THEME ---
        else:
            return "body { font-family: sans-serif; margin: 1in; }"