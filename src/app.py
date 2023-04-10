import polars as pl
import streamlit as st
from page_builders import build_page, build_sidebar, local_css
from data_loader import load_data
from authentication import check_password

if check_password():
    local_css("./src/style.css")
    build_sidebar()
    st.title("Balance Reporting")
    data_load_state = st.text('Loading data...')
    try:
        data = load_data()
        data_load_state.text("Done!")
        build_page(data)
    except pl.ComputeError:
        data_load_state.text("It seems there's no data")
