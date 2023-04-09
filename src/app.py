import polars as pl
import streamlit as st
from page_builders import build_page, build_sidebar, local_css
from file_management import load_data
from authentication import check_password

if check_password():
    local_css("./src/style.css")
    user = st.session_state['username']
    build_sidebar(user)
    st.title("Balance Reporting")
    data_load_state = st.text('Loading data...')
    try:
        data = load_data(user)
        data_load_state.text("Done!")
        build_page(data)
    except pl.ComputeError:
        data_load_state.text("It seems there's no data")
