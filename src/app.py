import polars as pl
import streamlit as st
from functions import load_data, build_page, save_uploaded_files

st.title("Balance Reporting")
user = st.radio("Utente", ['Luigi', 'Cristina'], horizontal=True).lower()
if f'files{user}' not in st.session_state:
    st.session_state[f'files{user}'] = 0
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Use form to load files
with st.sidebar.form("file_uploader", clear_on_submit=True):
    uploaded_files = st.file_uploader("FILE UPLOADER", accept_multiple_files=True)
    submitted = st.form_submit_button("UPLOAD!")
    if submitted and uploaded_files is not None:
        save_uploaded_files(uploaded_files, user)
# load data and run the app
try:
    # Load the dataframe.
    data = load_data(user)
    # Notify the reader that the data was successfully loaded.
    data_load_state.text("Done!")
    build_page(data)
except pl.ComputeError:
    data_load_state.text("It seems there's no data")



