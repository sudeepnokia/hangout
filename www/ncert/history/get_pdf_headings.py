

import os
from pypdf import PdfReader
import sys

def get_headings():
    """Gets the first 200 characters of each PDF."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdfs_dir = os.path.join(script_dir, "pdfs")

    filenames = os.listdir(pdfs_dir)

    for filename in filenames:
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdfs_dir, filename)
            try:
                reader = PdfReader(file_path)
                first_page_text = reader.pages[0].extract_text()
                print(f"--- {filename} ---")
                print(first_page_text[:200])
                print("\n")
            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")

if __name__ == "__main__":
    get_headings()

