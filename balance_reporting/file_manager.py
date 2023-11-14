from config import DATA_FOLDER
import streamlit as st
import os
from glob import glob
import polars as pl
from pathlib import Path
from balance_reporting.data_reader.data_reader import source_mapping, Fields


@st.cache_data
def convert_file(filepath:Path) -> bytes:
    df = pl.read_parquet(filepath)
    return df.write_csv().encode('utf-8')


def list_files() -> list[Path]:
    return [Path(p) for p in glob(f'{DATA_FOLDER}/{st.session_state.username}/*.parquet')]


def load_saved_files() -> pl.DataFrame:
    files = list_files()
    df = pl.DataFrame()
    for f in files:
        df = pl.concat(
            df,
            pl.read_parquet(f)
        )
    return df


def save_uploaded_files() -> None:
    if st.session_state['uploaded_files']:
        user = st.session_state.username
        if not os.path.exists(f"{DATA_FOLDER}/{user}"):
            os.makedirs(f"{DATA_FOLDER}/{user}")
        source = st.session_state['uploaded_source']
        files = st.session_state['uploaded_files']
        file_df = pl.DataFrame()
        for upl_file in files:
            temp_file_df = pl.read_csv(upl_file, has_header=True, separator=';', try_parse_dates=True)
            temp_file_df = source_mapping[source](temp_file_df)
            file_df = pl.concat([
                file_df,
                temp_file_df
            ])
        filename = f"{source}_{file_df[Fields.Date].min().strftime('%y%m%d')}_{file_df[Fields.Date].max().strftime('%y%m%d')}.parquet"
        file_df.write_parquet(f"{DATA_FOLDER}/{user}/{filename}", separator=';', date_format='%Y-%m-%d', datetime_format='%Y-%m-%d')


def file_upload_form() -> None:
    user = st.session_state.username
    with st.expander("Data loader"):
        with st.form("file_uploader", clear_on_submit=True):
            st.session_state['uploaded_files'] = st.file_uploader("FILE UPLOADER", accept_multiple_files=True)
            st.session_state.username = user # For some reason session states not used in the form are reset
            st.session_state['uploaded_source'] = st.selectbox("Source", source_mapping.keys())
            submitted = st.form_submit_button("UPLOAD!")
            if submitted:
                save_uploaded_files()


def delete_file(file:Path) -> None:
    os.remove(file)
