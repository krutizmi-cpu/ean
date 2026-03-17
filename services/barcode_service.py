from __future__ import annotations

import re
from io import BytesIO
from typing import Optional

import barcode
from barcode.writer import ImageWriter

DIGITS_RE = re.compile(r"^\d+$")


def normalize_digits(value: Optional[str]) -> str:
    if value is None:
        return ""
    return re.sub(r"\D", "", str(value).strip())


def calculate_ean13_check_digit(first_12_digits: str) -> str:
    if len(first_12_digits) != 12 or not DIGITS_RE.match(first_12_digits):
        raise ValueError("Для расчета контрольной цифры нужно ровно 12 цифр.")
    total = 0
    for idx, ch in enumerate(first_12_digits):
        digit = int(ch)
        if (idx + 1) % 2 == 0:
            total += digit * 3
        else:
            total += digit
    check = (10 - (total % 10)) % 10
    return str(check)


def build_ean13(first_12_digits: str) -> str:
    return first_12_digits + calculate_ean13_check_digit(first_12_digits)


def validate_ean13(ean13: str) -> bool:
    ean13 = normalize_digits(ean13)
    if len(ean13) != 13 or not DIGITS_RE.match(ean13):
        return False
    return build_ean13(ean13[:12]) == ean13


def generate_internal_ean13(article: str, sequence: int, prefix: str = "20") -> str:
    article_digits = normalize_digits(article)
    article_digits = article_digits[-5:].zfill(5)
    seq_digits = str(sequence).zfill(5)
    base12 = f"{prefix}{article_digits}{seq_digits}"
    if len(base12) != 12:
        raise ValueError("Не удалось собрать 12 цифр для внутреннего EAN-13.")
    return build_ean13(base12)


def ensure_ean13(
    article: str,
    ean13: Optional[str],
    sequence: int = 1,
    prefix: str = "20",
) -> tuple[str, bool]:
    cleaned = normalize_digits(ean13)
    if cleaned:
        if not validate_ean13(cleaned):
            raise ValueError(f"Некорректный EAN-13: {ean13}")
        return cleaned, False
    return generate_internal_ean13(article=article, sequence=sequence, prefix=prefix), True


def barcode_png_bytes(ean13: str) -> bytes:
    if not validate_ean13(ean13):
        raise ValueError("Нельзя построить изображение: EAN-13 некорректен.")
    ean = barcode.get("ean13", ean13[:-1], writer=ImageWriter())
    buffer = BytesIO()
    ean.write(
        buffer,
        options={
            "write_text": False,
            "module_width": 0.25,
            "module_height": 15,
            "quiet_zone": 2.5,
            "dpi": 300,
        },
    )
    return buffer.getvalue()
