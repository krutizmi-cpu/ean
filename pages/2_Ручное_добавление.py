import datetime as dt

import streamlit as st

from services.archive_service import build_result_csv, build_zip_bundle
from services.barcode_service import ensure_ean13
from services.excel_service import result_to_xlsx
from services.label_service import generate_labels_pdf
from services.repository import add_product, clear_products, list_products

st.set_page_config(page_title="Ручное добавление", page_icon="✏️", layout="wide")
st.title("✏️ Ручное добавление товара")

with st.form("manual_add_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        article = st.text_input("Артикул *")
        name = st.text_input("Наименование *")
    with col2:
        ean13 = st.text_input("EAN13 (необязательно)")
        qty = st.number_input("Количество этикеток", min_value=1, value=1, step=1)
    submitted = st.form_submit_button("➕ Добавить товар", use_container_width=True)

if submitted:
    try:
        if not article.strip():
            raise ValueError("Артикул обязателен.")
        if not name.strip():
            raise ValueError("Наименование обязательно.")
        current_count = len(list_products()) + 1
        final_ean13, generated = ensure_ean13(
            article=article, ean13=ean13, sequence=current_count
        )
        add_product({
            "Артикул": article.strip(),
            "Наименование": name.strip(),
            "EAN13": final_ean13,
            "Количество": int(qty),
            "Сгенерирован": "Да" if generated else "Нет",
        })
        st.success(f"Товар ‘{name.strip()}’ добавлен. EAN13: {final_ean13}")
    except Exception as e:
        st.error(str(e))

st.divider()
repo_df = list_products()

col_title, col_clear = st.columns([4, 1])
with col_title:
    st.subheader(f"Текущий список ({len(repo_df)} поз.) ")
with col_clear:
    if st.button("🗑️ Очистить список", use_container_width=True):
        clear_products()
        st.rerun()

st.dataframe(repo_df, use_container_width=True)

if not repo_df.empty:
    result_xlsx = result_to_xlsx(repo_df)
    result_csv = build_result_csv(repo_df)
    pdf_56x40 = generate_labels_pdf(repo_df, label_format="56x40")
    pdf_a6 = generate_labels_pdf(repo_df, label_format="A6")
    now_str = dt.datetime.now().strftime("%Y%m%d_%H%M")
    zip_bytes = build_zip_bundle(
        result_xlsx=result_xlsx,
        result_csv=result_csv,
        pdf_56x40=pdf_56x40,
        pdf_a6=pdf_a6,
    )
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Скачать Excel",
            data=result_xlsx,
            file_name=f"manual_result_{now_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "🗂️ Скачать ZIP-комплект",
            data=zip_bytes,
            file_name=f"manual_bundle_{now_str}.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary",
        )
