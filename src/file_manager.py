from config import DATA_FOLDER
import streamlit as st
import os
from glob import glob

def list_files():
    yield from glob(f'{DATA_FOLDER}/{st.session_state.username}/*.csv')

def delete_file(file):
    os.remove(file)

def file_lister():
    with st.expander("Saved files"):
        col1, col2 = st.columns(2)
        for file in list_files():
            col1.write(file.split('/')[-1])
            col2.button("Delete", on_click=lambda: delete_file(file), key=file)
