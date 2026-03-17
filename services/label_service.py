from __future__ import annotations

import os
from io import BytesIO

import pandas as pd
from reportlab.lib.pagesizes import A6
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from services.barcode_service import barcode_png_bytes

MM = 72 / 25.4


def _register_fonts():
    """Register a Unicode-capable TTF font for Cyrillic support."""
    candidates = [
        os.path.join(
            os.path.dirname(__import__("matplotlib").__file__),
            "mpl-data", "fonts", "ttf", "DejaVuSans.ttf",
        ),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            pdfmetrics.registerFont(TTFont("Unicode", path))
            pdfmetrics.registerFont(TTFont("Unicode-Bold", path))
            return
    import urllib.request
    url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
    tmp = "/tmp/DejaVuSans.ttf"
    if not os.path.isfile(tmp):
        urllib.request.urlretrieve(url, tmp)
    pdfmetrics.registerFont(TTFont("Unicode", tmp))
    pdfmetrics.registerFont(TTFont("Unicode-Bold", tmp))


_register_fonts()


def mm(value: float) -> float:
    return value * MM


def _truncate(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else text[:max_chars - 1] + "..."


def draw_label_56x40(c: canvas.Canvas, item: dict):
    width = mm(56)
    height = mm(40)
    name = str(item.get("Наименование", ""))
    article = str(item.get("Артикул", ""))
    ean13 = str(item.get("EAN13", ""))
    c.setFont("Unicode-Bold", 7)
    c.drawString(mm(2), height - mm(5), _truncate(name, 38))
    c.setFont("Unicode", 6.5)
    c.drawString(mm(2), height - mm(9), "Арт: " + _truncate(article, 22))
    barcode_bytes = barcode_png_bytes(ean13)
    barcode_img = ImageReader(BytesIO(barcode_bytes))
    c.drawImage(
        barcode_img,
        mm(2),
        mm(9),
        width=mm(52),
        height=mm(17),
        preserveAspectRatio=True,
        mask="auto",
    )
    c.setFont("Unicode", 7.5)
    c.drawCentredString(width / 2, mm(4), ean13)


def draw_label_a6(c: canvas.Canvas, item: dict):
    width, height = A6
    name = str(item.get("Наименование", ""))
    article = str(item.get("Артикул", ""))
    ean13 = str(item.get("EAN13", ""))
    c.setFont("Unicode-Bold", 13)
    c.drawString(mm(8), height - mm(14), _truncate(name, 42))
    c.setFont("Unicode", 10)
    c.drawString(mm(8), height - mm(22), "Артикул: " + article)
    barcode_bytes = barcode_png_bytes(ean13)
    barcode_img = ImageReader(BytesIO(barcode_bytes))
    c.drawImage(
        barcode_img,
        mm(8),
        mm(28),
        width=width - mm(16),
        height=mm(38),
        preserveAspectRatio=True,
        mask="auto",
    )
    c.setFont("Unicode", 12)
    c.drawCentredString(width / 2, mm(20), ean13)


def generate_labels_pdf(df: pd.DataFrame, label_format: str) -> bytes:
    output = BytesIO()
    if label_format == "56x40":
        page_size = (mm(56), mm(40))
    elif label_format == "A6":
        page_size = A6
    else:
        raise ValueError("Неизвестный формат этикетки.")
    c = canvas.Canvas(output, pagesize=page_size)
    for _, row in df.iterrows():
        qty = int(row.get("Количество", 1))
        item = row.to_dict()
        for _ in range(qty):
            if label_format == "56x40":
                draw_label_56x40(c, item)
            else:
                draw_label_a6(c, item)
            c.showPage()
    c.save()
    return output.getvalue()
