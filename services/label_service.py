from __future__ import annotations

from io import BytesIO

import pandas as pd
from reportlab.lib.pagesizes import A6
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from services.barcode_service import barcode_png_bytes

MM = 72 / 25.4


def mm(value: float) -> float:
    return value * MM


def _truncate(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else text[:max_chars - 1] + "…"


def draw_label_56x40(c: canvas.Canvas, item: dict):
    width = mm(56)
    height = mm(40)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mm(2), height - mm(5), _truncate(str(item["Наименование"]), 36))
    c.setFont("Helvetica", 7)
    c.drawString(mm(2), height - mm(9), f"Арт: {_truncate(str(item['Артикул']), 20)}")
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
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, mm(5), item["EAN13"])


def draw_label_a6(c: canvas.Canvas, item: dict):
    width, height = A6
    c.setFont("Helvetica-Bold", 14)
    c.drawString(mm(8), height - mm(14), _truncate(str(item["Наименование"]), 40))
    c.setFont("Helvetica", 11)
    c.drawString(mm(8), height - mm(22), f"Артикул: {item['Артикул']}")
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
    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, mm(20), item["EAN13"])


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
        qty = int(row["Количество"])
        item = row.to_dict()
        for _ in range(qty):
            if label_format == "56x40":
                draw_label_56x40(c, item)
            else:
                draw_label_a6(c, item)
            c.showPage()
    c.save()
    return output.getvalue()
