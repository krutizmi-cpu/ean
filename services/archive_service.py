from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd


def build_result_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def build_result_readme() -> bytes:
    text = (
        "Архив результата генерации этикеток\n"
        "\n"
        "Файлы в архиве:\n"
        "- result.xlsx: итоговая таблица товаров\n"
        "- result.csv: та же таблица в CSV\n"
        "- labels_56x40.pdf: этикетки 56x40 мм\n"
        "- labels_A6.pdf: этикетки формата A6\n"
        "\n"
        "Если EAN13 был пустой, система сгенерировала внутренний код с префиксом 20.\n"
    )
    return text.encode("utf-8")


def build_zip_bundle(
    *,
    result_xlsx: bytes,
    result_csv: bytes,
    pdf_56x40: bytes,
    pdf_a6: bytes,
) -> bytes:
    output = BytesIO()
    with ZipFile(output, mode="w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("result.xlsx", result_xlsx)
        zf.writestr("result.csv", result_csv)
        zf.writestr("labels_56x40.pdf", pdf_56x40)
        zf.writestr("labels_A6.pdf", pdf_a6)
        zf.writestr("README_RESULT.txt", build_result_readme())
    return output.getvalue()
