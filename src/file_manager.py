from config import DATA_FOLDER
import streamlit as st
import os
from glob import glob
import polars as pl
from pathlib import Path
from typing import Generator
from data_manager import transform_data

def save_uploaded_files() -> None:
    if st.session_state['uploaded_files']:
        user = st.session_state.username
        if not os.path.exists(f"{DATA_FOLDER}/{user}"):
            os.makedirs(f"{DATA_FOLDER}/{user}")
        for upl_file in st.session_state['uploaded_files']:
            file_df = pl.read_csv(upl_file, has_header=True, separator=';', try_parse_dates=True)
            file_df = transform_data(file_df)
            filename = f"{file_df['Date'].min().strftime('%Y%m%d')}_{file_df['Date'].max().strftime('%Y%m%d')}.csv"
            file_df.write_csv(f"{DATA_FOLDER}/{user}/{filename}", separator=';', date_format='%Y-%m-%d', datetime_format='%Y-%m-%d')

def file_upload_form() -> None:
    user = st.session_state.username
    with st.expander("Data loader"):
        with st.form("file_uploader", clear_on_submit=True):
            st.session_state['uploaded_files'] = st.file_uploader("FILE UPLOADER", accept_multiple_files=True)
            st.session_state.username = user # For some reason session states not used in the form are reset
            submitted = st.form_submit_button("UPLOAD!")
            if submitted:
                save_uploaded_files()

def list_files() -> list[Path]:
    return [Path(p) for p in glob(f'{DATA_FOLDER}/{st.session_state.username}/*.csv')]

def delete_file(file:Path) -> None:
    os.remove(file)

@st.cache_data
def convert_df(filepath:Path) -> bytes:
    df = pl.read_csv(filepath, has_header=True, separator=';', try_parse_dates=True)
    return df.write_csv().encode('utf-8')

def file_lister(filelist: list[Path]) -> None:
    with st.expander("Saved files"):
        col1, col2, col3 = st.columns([2,1,1])
        for file in filelist:
            col1.write(file.name)
            col2.download_button("Download", data=convert_df(file), file_name=file.name)
            col3.button("Delete", on_click=lambda: delete_file(file), key=file)
