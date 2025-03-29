import io

import fitz  # PyMuPDF
from PIL import Image


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


def add_text_to_pdf(template_pdf_path, output_pdf_path, position, text, font_size=12, font="helv", color="#000000"):
    """
    Insere o texto no PDF template na posição especificada e salva um novo PDF.

    Parâmetros:
    - template_pdf_path: caminho do PDF template.
    - output_pdf_path: caminho onde o novo PDF será salvo.
    - position: tupla (x, y) com a posição do texto.
    - text: texto a ser inserido.
    - font_size: tamanho da fonte.
    - font: nome da fonte (apenas fontes padrão do PyMuPDF são suportadas).
    - color: cor do texto em formato hexadecimal (ex.: "#FF0000" para vermelho).
    """
    doc = fitz.open(template_pdf_path)
    page = doc[0]
    rgb_color = tuple(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))

    # Verifica se a fonte é uma das fontes padrão do PyMuPDF
    standard_fonts = ["helv", "cour", "times", "symbol", "zapfdingbats"]
    if font not in standard_fonts:
        raise ValueError(f"Font '{font}' is not supported. Use one of the standard fonts: {', '.join(standard_fonts)}")

    try:
        # Insere o texto usando uma fonte padrão
        page.insert_text(position, text, fontsize=font_size, fontname=font, color=rgb_color)
    except Exception as e:
        raise ValueError(f"Error inserting text: {e}")
    doc.save(output_pdf_path)
    doc.close()


def generate_preview_image(template_pdf_path, position, text, font_size=12, font="helv", color="#000000"):
    """
    Gera uma imagem de pré-visualização do certificado com o texto inserido.

    Parâmetros:
    - template_pdf_path: caminho do PDF template.
    - position: tupla (x, y) com a posição do texto.
    - text: texto a ser inserido.
    - font_size: tamanho da fonte.
    - font: nome da fonte (apenas fontes padrão do PyMuPDF são suportadas).
    - color: cor do texto em formato hexadecimal (ex.: "#FF0000" para vermelho).

    Retorna:
    - Uma imagem PIL com o texto inserido.
    """
    doc = fitz.open(template_pdf_path)
    page = doc[0]
    rgb_color = tuple(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))

    # Verifica se a fonte é uma das fontes padrão do PyMuPDF
    standard_fonts = ["helv", "cour", "times", "symbol", "zapfdingbats"]
    if font not in standard_fonts:
        raise ValueError(f"Font '{font}' is not supported. Use one of the standard fonts: {', '.join(standard_fonts)}")

    try:
        # Insere o texto na página
        page.insert_text(position, text, fontsize=font_size, fontname=font, color=rgb_color)

        # Converte a página em imagem
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
    except Exception as e:
        raise ValueError(f"Error generating preview: {e}")
    finally:
        doc.close()

    return image
