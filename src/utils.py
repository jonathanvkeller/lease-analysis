import base64
import os
import fitz

def is_pdf(file_path):
    """Check if a file is a PDF."""
    return file_path.lower().endswith('.pdf')

def encode_pdf_to_base64(file_path):
    """Convert a PDF file to base64 encoding."""
    with open(file_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

def create_folder_structure():
    """Create the basic folder structure for the project."""
    folders = [
        "data/leases",
        "data/prompts",
        "output",
        "exceptions",
        "logs"
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

def convert_pdf_to_images(pdf_path):
    """
    Convert all pages of a PDF file to in-memory PNG images using PyMuPDF.
    :param pdf_path: Path to the PDF file.
    :return: A list of bytes objects, each containing PNG image data for a page.
    """
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap()
        image_bytes = pix.tobytes("png")
        images.append(image_bytes)
    return images
