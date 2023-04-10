from config import DATA_FOLDER
import streamlit as st
import os
from glob import glob

def save_uploaded_files():
    user = st.session_state.username
    if not os.path.exists(f"{DATA_FOLDER}/{user}"):
        os.makedirs(f"{DATA_FOLDER}/{user}")
    st.session_state[f'files{user}'] = len(glob(f"{DATA_FOLDER}/{user}/*.csv"))
    for upl_file in st.session_state.uploaded_files:
        with open(f"{DATA_FOLDER}/{user}/data{st.session_state[f'files{user}']}.csv", 'wb') as output_file:
            output_file.write(upl_file.read())
        st.session_state[f'files{user}'] += 1

def file_upload_form():
    user = st.session_state.username
    with st.expander("Data loader"):
        with st.form("file_uploader", clear_on_submit=True):
            st.file_uploader("FILE UPLOADER", key='uploaded_files', accept_multiple_files=True)
            st.session_state.username = user # For some reason session states not used in the form are reset
            submitted = st.form_submit_button("UPLOAD!")
            if submitted is not None and st.session_state.get('uploaded_files'):
                save_uploaded_files()
