# processor.py

import os
import tempfile

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_certificates(pdf_template_path, names_list, font_settings, position, output_dir, output_filename=None):
    """
    Generate certificates for each name using the PDF template.

    Args:
        pdf_template_path: Path to the PDF template
        names_list: List of names (strings)
        font_settings: Dictionary with font settings (family, size, color)
        position: Tuple (x, y) in PDF coordinates (origin at bottom-left)
        output_dir: Output directory for the generated certificates
        output_filename: Optional specific filename for the output (used for preview)

    Returns:
        List of paths to the generated certificates
    """
    generated_files = []

    for i, name in enumerate(names_list):
        # Create a PDF overlay with the name
        overlay_pdf_path = create_name_overlay(name, font_settings, position)

        # Determine output filename
        if output_filename and len(names_list) == 1:
            # Use specified filename (for preview)
            output_path = os.path.join(output_dir, output_filename)
        else:
            # Generate filename from name
            safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in name)
            output_path = os.path.join(output_dir, f"certificate_{safe_name}.pdf")

        # Merge the overlay with the template
        merge_pdfs(pdf_template_path, overlay_pdf_path, output_path)

        # Remove temporary overlay file
        if os.path.exists(overlay_pdf_path):
            os.remove(overlay_pdf_path)

        generated_files.append(output_path)

    return generated_files


def create_name_overlay(name, font_settings, position):
    """
    Create a PDF with transparent background and only the name at the specified position.

    Args:
        name: Name text to add
        font_settings: Dictionary with font settings
        position: (x, y) position in points

    Returns:
        Path to the temporary PDF file created
    """
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)

    # Create a new PDF with ReportLab
    c = canvas.Canvas(temp_path, pagesize=letter)

    # Set font properties
    font_name = font_settings["family"]
    font_size = font_settings["size"]

    c.setFont(font_name, font_size)

    # Set text color
    if "color" in font_settings and font_settings["color"]:
        color = font_settings["color"].lstrip('#')
        c.setFillColorRGB(int(color[0:2], 16) / 255, int(color[2:4], 16) / 255, int(color[4:6], 16) / 255)

    # Draw the text
    x, y = position
    c.drawString(x, y, name)

    # Save the PDF
    c.save()

    return temp_path


def merge_pdfs(template_path, overlay_path, output_path):
    """
    Merge the overlay PDF (with the name) onto the template PDF.

    Args:
        template_path: Path to the template PDF
        overlay_path: Path to the overlay PDF with the name
        output_path: Path where to save the merged PDF
    """
    # Read the PDFs
    template_pdf = PdfReader(template_path)
    overlay_pdf = PdfReader(overlay_path)

    # Create a PDF writer
    output_pdf = PdfWriter()

    # Merge the first pages
    template_page = template_pdf.pages[0]
    overlay_page = overlay_pdf.pages[0]

    # Add the overlay content to the template page
    template_page.merge_page(overlay_page)

    # Add the merged page to the output
    output_pdf.add_page(template_page)

    # Write the output file
    with open(output_path, "wb") as f:
        output_pdf.write(f)
