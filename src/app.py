import polars as pl
import streamlit as st
from functions import load_data, build_page, save_uploaded_files
from authentication import check_password

if check_password():
    user = st.session_state['username']
    st.title("Balance Reporting")
    if f'files{user}' not in st.session_state:
        st.session_state[f'files{user}'] = 0
    data_load_state = st.text('Loading data...')
    with st.sidebar.form("file_uploader", clear_on_submit=True):
        st.write(f"User: {user}")
        uploaded_files = st.file_uploader("FILE UPLOADER", accept_multiple_files=True)
        st.session_state.username = user # For some reason session states not used in the form are resetted
        submitted = st.form_submit_button("UPLOAD!")
        if submitted and uploaded_files is not None:
            save_uploaded_files(uploaded_files, user)
    try:
        data = load_data(user)
        data_load_state.text("Done!")
        build_page(data)
    except pl.ComputeError:
        data_load_state.text("It seems there's no data")
