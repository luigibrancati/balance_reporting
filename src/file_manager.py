from config import DATA_FOLDER
import streamlit as st
import os
from glob import glob

def list_files(user):
    yield from glob(f"{DATA_FOLDER}/{user}/*.csv")

def save_uploaded_files(uploaded_files, user):
    if not os.path.exists(f"{DATA_FOLDER}/{user}"):
        os.makedirs(f"{DATA_FOLDER}/{user}")
    st.session_state[f'files{user}'] = len(glob(f"{DATA_FOLDER}/{user}/*.csv"))
    for upl_file in uploaded_files:
        with open(f"{DATA_FOLDER}/{user}/data{st.session_state[f'files{user}']}.csv", 'wb') as output_file:
            output_file.write(upl_file.read())
        st.session_state[f'files{user}'] += 1

def delete_file(file):
    os.remove(file)

def file_upload_form(user):
    with st.form("file_uploader", clear_on_submit=True):
        uploaded_files = st.file_uploader("FILE UPLOADER", accept_multiple_files=True)
        st.session_state.username = user # For some reason session states not used in the form are reset
        submitted = st.form_submit_button("UPLOAD!")
        if submitted and uploaded_files is not None:
            save_uploaded_files(uploaded_files, user)

def file_lister(user):
    with st.expander("Saved files"):
        col1, col2 = st.columns(2)
        for file in list_files(user):
            col1.write(file.split('/')[-1])
            col2.button("Delete", on_click=lambda: delete_file(file), key=file)
