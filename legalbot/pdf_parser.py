import requests
from io import BytesIO
from PyPDF2 import PdfReader

def parse_pdf_from_link(url: str) -> str:
    """
    Faz download do PDF e extrai o texto de todas as páginas.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    reader = PdfReader(BytesIO(resp.content))
    texto = []
    for page in reader.pages:
        texto.append(page.extract_text() or "")
    return "\n".join(texto)

def correct_pdf_text(text: str) -> str:
    return text.replace("-\n", "").replace("\n", " ")
