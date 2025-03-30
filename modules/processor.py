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
    Insere o texto no PDF template na posição especificada e salva um novo PDF,
    garantindo que o texto fique centralizado no ponto escolhido.
    """
    doc = fitz.open(template_pdf_path)
    page = doc[0]
    rgb_color = tuple(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))

    # Verifica se a fonte é uma das fontes padrão do PyMuPDF
    standard_fonts = ["helv", "cour", "times", "symbol", "zapfdingbats"]
    if font not in standard_fonts:
        raise ValueError(f"Font '{font}' is not supported. Use one of the standard fonts: {', '.join(standard_fonts)}")

    # Obtém a largura e altura do texto renderizado
    text_width = page.get_text_length(text, fontname=font, fontsize=font_size)
    text_height = font_size  # Aproximadamente o tamanho da fonte

    # Calcula a posição centralizada
    x_centered = position[0] - (text_width / 2)
    y_centered = position[1] + (text_height / 2)  # Ajuste para alinhar corretamente

    try:
        # Insere o texto na posição ajustada
        page.insert_text((x_centered, y_centered), text, fontsize=font_size, fontname=font, color=rgb_color)
    except Exception as e:
        raise ValueError(f"Error inserting text: {e}")

    doc.save(output_pdf_path)
    doc.close()
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
    """
    doc = fitz.open(template_pdf_path)
    page = doc[0]
    rgb_color = tuple(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))

    # Verifica se a fonte é uma das fontes padrão do PyMuPDF
    standard_fonts = ["helv", "cour", "times", "symbol", "zapfdingbats"]
    if font not in standard_fonts:
        raise ValueError(f"Font '{font}' is not supported. Use one of the standard fonts: {', '.join(standard_fonts)}")

    try:
        # Insere o texto na posição
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