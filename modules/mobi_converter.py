# BookAlchemist/modules/mobi_converter.py

import subprocess
import os

def convert_mobi_to_epub(mobi_path):
    """
    Uses Calibre's 'ebook-convert' command-line tool to convert a
    .mobi file to a .epub file. The .epub is saved in the same directory.
    Returns the path to the newly created .epub file.
    """
    if not mobi_path.lower().endswith('.mobi'):
        raise ValueError("Input file must be a .mobi file")

    base_name = os.path.splitext(mobi_path)[0]
    epub_path = f"{base_name}.epub"
    
    command = ['ebook-convert', mobi_path, epub_path]
    
    try:
        print(f"Converting '{os.path.basename(mobi_path)}' to EPUB...")
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Conversion successful.")
        return epub_path
    except FileNotFoundError:
        print("ERROR: Calibre's 'ebook-convert' not found.")
        print("Please ensure Calibre is installed and its directory is in your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Calibre conversion failed: {e}")
        return None