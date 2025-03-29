import fitz  # PyMuPDF
from PIL import Image
import io


def pdf_to_image(pdf_path):
    """
    Abre o PDF e converte a primeira página em uma imagem (PIL Image)
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img_data = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_data))
    doc.close()
    return image


def add_text_to_pdf(template_pdf_path, output_pdf_path, position, text, font_size=12, font="helv"):
    """
    Insere o texto no PDF template na posição especificada e salva um novo PDF.

    Parâmetros:
    - template_pdf_path: caminho do PDF template.
    - output_pdf_path: caminho onde o novo PDF será salvo.
    - position: tupla (x, y) com a posição do texto.
    - text: texto a ser inserido.
    - font_size: tamanho da fonte.
    - font: nome da fonte (ex.: "helv" para Helvetica).
    """
    doc = fitz.open(template_pdf_path)
    page = doc[0]
    page.insert_text(position, text, fontsize=font_size, fontname=font, color=(0, 0, 0))
    doc.save(output_pdf_path)
    doc.close()
