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
    # Try DejaVuSans from matplotlib (always available on Streamlit Cloud)
    candidates = [
        # matplotlib bundled fonts
        os.path.join(
            os.path.dirname(__import__("matplotlib").__file__),
            "mpl-data", "fonts", "ttf", "DejaVuSans.ttf",
        ),
        # system fonts on Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            pdfmetrics.registerFont(TTFont("Unicode", path))
            pdfmetrics.registerFont(TTFont("Unicode-Bold", path))
            return
    # Fallback: download DejaVuSans at runtime
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
    return text if len(text) <= max_chars else text[: max_chars - 1] + "\u2026"


def draw_label_56x40(c: canvas.Canvas, item: dict):
    width = mm(56)
    height = mm(40)
    c.setFont("Unicode-Bold", 7)
    c.drawString(mm(2), height - mm(5), _truncate(str(item["\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435"]), 38))
    c.setFont("Unicode", 6.5)
    c.drawString(mm(2), height - mm(9), f"\u0410\u0440\u0442: {_truncate(str(item['\u0410\u0440\u0442\u0438\u043a\u0443\u043b']), 22)}")
    barcode_bytes = barcode_png_bytes(item["EAN13"])
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
    c.drawCentredString(width / 2, mm(4), item["EAN13"])


def draw_label_a6(c: canvas.Canvas, item: dict):
    width, height = A6
    c.setFont("Unicode-Bold", 13)
    c.drawString(mm(8), height - mm(14), _truncate(str(item["\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435"]), 42))
    c.setFont("Unicode", 10)
    c.drawString(mm(8), height - mm(22), f"\u0410\u0440\u0442\u0438\u043a\u0443\u043b: {item['\u0410\u0440\u0442\u0438\u043a\u0443\u043b']}")
    barcode_bytes = barcode_png_bytes(item["EAN13"])
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
    c.drawCentredString(width / 2, mm(20), item["EAN13"])


def generate_labels_pdf(df: pd.DataFrame, label_format: str) -> bytes:
    output = BytesIO()
    if label_format == "56x40":
        page_size = (mm(56), mm(40))
    elif label_format == "A6":
        page_size = A6
    else:
        raise ValueError("\u041d\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043d\u044b\u0439 \u0444\u043e\u0440\u043c\u0430\u0442 \u044d\u0442\u0438\u043a\u0435\u0442\u043a\u0438.")
    c = canvas.Canvas(output, pagesize=page_size)
    for _, row in df.iterrows():
        qty = int(row["\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e"])
        item = row.to_dict()
        for _ in range(qty):
            if label_format == "56x40":
                draw_label_56x40(c, item)
            else:
                draw_label_a6(c, item)
            c.showPage()
    c.save()
    return output.getvalue()
