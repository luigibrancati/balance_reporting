from config import DATA_FOLDER
import streamlit as st
import os
from glob import glob
import polars as pl
from pathlib import Path
from typing import Generator

def list_files() -> Generator[Path, None, None]:
    return (Path(p) for p in glob(f'{DATA_FOLDER}/{st.session_state.username}/*.csv'))

def delete_file(file:Path) -> None:
    os.remove(file)

@st.cache_data
def convert_df(filepath:Path) -> bytes:
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    df = pl.read_csv(filepath, has_header=True, separator=';', try_parse_dates=True)
    return df.write_csv().encode('utf-8')

def file_lister() -> None:
    with st.expander("Saved files"):
        col1, col2, col3 = st.columns(3)
        for file in list_files():
            col1.write(file.name)
            col2.download_button("Download", data=convert_df(file), file_name=file.name)
            col3.button("Delete", on_click=lambda: delete_file(file), key=file)
