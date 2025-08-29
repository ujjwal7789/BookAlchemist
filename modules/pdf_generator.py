import asyncio
from playwright.async_api import async_playwright

class PDFGenerator:
    @staticmethod
    async def generate_pdf_from_html(html_content, output_path):
        """
        Takes an HTML string and saves it as a PDF at the specified path.
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.set_content(html_content, wait_until="networkidle")
                
                # --- CHANGE: Define a custom, novel-like paper size ---
                await page.pdf(
                    path=output_path,
                    # We are removing format='A4' and specifying width and height directly.
                    # 6in x 9in is a very common and professional "trade paperback" size.
                    width='6in',
                    height='9in',
                    print_background=True,
                    margin={'top': '0in', 'right': '0in', 'bottom': '0in', 'left': '0in'}
                )
                
                await browser.close()
            return True
        except Exception as e:
            print(f"❌ Error during PDF generation: {e}")
            return False