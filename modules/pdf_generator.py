import asyncio
from playwright.async_api import async_playwright

class PDFGenerator:
    """
    A class to convert an HTML string into a hight quality PDF file using a headless browser
    """

    @staticmethod
    async def generate_pdf_from_html(html_content, output_path):
        """Takes an HTML string and saves it as a PDF at the specified path.

        Args:
            html_content (str): The full HTML content to be converted.

            output_path (str): The file path where the PDF will be saved.
        
        Returns:
            bool: True if successful
        """

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()

                page = await browser.new_page()

                await page.set_content(html_content, wait_until="networkidle")

                await page.pdf(
                    path=output_path,
                    format='A4',
                    print_background=True,
                    margin={'top': '0in', 'right': '0in', 'bottom': '0in', 'left': '0in'}
                )

                await browser.close()
            return True
        except Exception as e:
            print(f"❌ Error during PDF generation: {e}")
            return False