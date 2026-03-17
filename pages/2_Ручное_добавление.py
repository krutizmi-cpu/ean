import datetime as dt

import streamlit as st

from services.archive_service import build_result_csv, build_zip_bundle
from services.barcode_service import ensure_ean13
from services.excel_service import result_to_xlsx
from services.label_service import generate_labels_pdf
from services.repository import add_product, clear_products, list_products

st.title("✏️ Ручное добавление товара")

with st.form("manual_add_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        article = st.text_input("Артикул *")
        name = st.text_input("Наименование *")
    with col2:
        ean13 = st.text_input("EAN13 (необязательно)")
        qty = st.number_input("Количество", min_value=1, value=1, step=1)
    submitted = st.form_submit_button("➕ Добавить")

if submitted:
    if not article or not name:
        st.error("Артикул и Наименование обязательны")
    else:
        final_ean13, _ = ensure_ean13(article=article, ean13=ean13)
        add_product({
            "Артикул": article,
            "Наименование": name,
            "EAN13": final_ean13,
            "Количество": int(qty),
        })
        st.success(f"Добавлено: {name} ({final_ean13})")

products_df = list_products()

if not products_df.empty:
    st.subheader(f"Список товаров ({len(products_df)} шт.)")
    st.dataframe(products_df, use_container_width=True)

    if st.button("🗑️ Очистить список"):
        clear_products()
        st.rerun()

    if st.button("🎯 Сформировать результат"):
        with st.spinner("Генерация..."):
            result_xlsx = result_to_xlsx(products_df)
            result_csv = build_result_csv(products_df)
            pdf_56x40 = generate_labels_pdf(products_df, label_format="56x40")
            pdf_a6 = generate_labels_pdf(products_df, label_format="A6")
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
                "📦 Скачать ZIP-комплект",
                data=zip_bytes,
                file_name=f"manual_bundle_{now_str}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
            )
else:
    st.info("Список пуст. Добавьте товары выше.")
