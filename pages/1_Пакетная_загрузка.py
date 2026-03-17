import datetime as dt

import pandas as pd
import streamlit as st

from services.archive_service import build_result_csv, build_zip_bundle
from services.barcode_service import ensure_ean13
from services.excel_service import build_template_xlsx, read_uploaded_excel, result_to_xlsx
from services.label_service import generate_labels_pdf

st.set_page_config(page_title="Пакетная загрузка", page_icon="📄", layout="wide")
st.title("📄 Пакетная загрузка")

template_bytes = build_template_xlsx()
st.download_button(
    "Скачать шаблон Excel",
    data=template_bytes,
    file_name="import_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.divider()
uploaded_file = st.file_uploader("Загрузите Excel-файл с товарами", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = read_uploaded_excel(uploaded_file)
        ok_rows = []
        error_rows = []
        seq = 1

        for idx, row in df.iterrows():
            row_number = idx + 2
            article = row["Артикул"]
            name = row["Наименование"]
            ean13 = row["EAN13"]
            qty_raw = str(row["Количество"]).strip()

            try:
                if not article:
                    raise ValueError("Пустой артикул.")
                if not name:
                    raise ValueError("Пустое наименование.")
                try:
                    qty = int(float(qty_raw))
                except Exception:
                    raise ValueError("Количество должно быть числом.")
                if qty < 1:
                    raise ValueError("Количество >= 1.")
                final_ean13, generated = ensure_ean13(article=article, ean13=ean13, sequence=seq)
                seq += 1
                ok_rows.append({
                    "Артикул": article,
                    "Наименование": name,
                    "EAN13": final_ean13,
                    "Количество": qty,
                    "Сгенерирован": "Да" if generated else "Нет",
                    "Строка_исх": row_number,
                })
            except Exception as e:
                error_rows.append({
                    "Строка": row_number,
                    "Артикул": article,
                    "Наименование": name,
                    "EAN13": ean13,
                    "Количество": qty_raw,
                    "Ошибка": str(e),
                })

        result_df = pd.DataFrame(ok_rows)
        errors_df = pd.DataFrame(error_rows)

        if not result_df.empty:
            st.success(f"Успешно обработано строк: {len(result_df)}")
            st.dataframe(result_df, use_container_width=True)

        if not errors_df.empty:
            st.error(f"Ошибок: {len(errors_df)}")
            with st.expander("Показать журнал ошибок"):
                st.dataframe(errors_df, use_container_width=True)

        if not result_df.empty:
            result_xlsx = result_to_xlsx(result_df)
            result_csv = build_result_csv(result_df)
            pdf_56x40 = generate_labels_pdf(result_df, label_format="56x40")
            pdf_a6 = generate_labels_pdf(result_df, label_format="A6")
            now_str = dt.datetime.now().strftime("%Y%m%d_%H%M")
            zip_bytes = build_zip_bundle(
                result_xlsx=result_xlsx,
                result_csv=result_csv,
                pdf_56x40=pdf_56x40,
                pdf_a6=pdf_a6,
            )
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "Скачать Excel",
                    data=result_xlsx,
                    file_name=f"result_{now_str}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            with col2:
                st.download_button(
                    "Скачать PDF 56x40",
                    data=pdf_56x40,
                    file_name=f"labels_56x40_{now_str}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            with col3:
                st.download_button(
                    "Скачать PDF A6",
                    data=pdf_a6,
                    file_name=f"labels_A6_{now_str}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            st.download_button(
                "🗂️ Скачать весь комплект ZIP",
                data=zip_bytes,
                file_name=f"labels_bundle_{now_str}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
            )

        if not errors_df.empty:
            errors_csv = errors_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⚠️ Скачать журнал ошибок (CSV)",
                data=errors_csv,
                file_name=f"errors_{dt.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except Exception as e:
        st.error(str(e))
