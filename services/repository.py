from __future__ import annotations

import pandas as pd
import streamlit as st


def init_repo():
    if "products_repo" not in st.session_state:
        st.session_state["products_repo"] = []


def add_product(item: dict):
    init_repo()
    st.session_state["products_repo"].append(item)


def clear_products():
    st.session_state["products_repo"] = []


def list_products() -> pd.DataFrame:
    init_repo()
    if not st.session_state["products_repo"]:
        return pd.DataFrame(
            columns=["Артикул", "Наименование", "EAN13", "Количество", "Сгенерирован"]
        )
    return pd.DataFrame(st.session_state["products_repo"])
