from config import DATA_FOLDER
import streamlit as st
import os
from glob import glob
import re
import polars as pl

def select_best_date_field(date_cols:list):
    best_data = list(filter(re.compile('data valuta', re.I).match, date_cols))
    if not best_data:
        best_data = date_cols
    return best_data[0]

def transform_data(df):
    # Coalesce numeric columns
    numeric_columns = df.select(pl.col(pl.NUMERIC_DTYPES)).columns
    bool_column = df.select(pl.col(pl.Boolean)).columns
    match len(numeric_columns), len(bool_column):
        case 2, 0:
            df = df.with_columns([
                pl.coalesce(numeric_columns).round(2).alias('Amount'),
                pl.col(numeric_columns[0]).is_not_null().alias('Credit')
            ])
        case 1, 1:
            df = df.with_columns([
                pl.col(numeric_columns).round(2).alias('Amount'),
                pl.col(bool_column).round(2).alias('Credit')
            ])
    # select best date field
    best_date_col = select_best_date_field(
        list(filter(re.compile('^(data|date)', re.I).search, df.columns))
    )
    df = df.with_columns([
        pl.col(best_date_col).alias('Date').cast(pl.Date)
    ]).with_columns([
        pl.col('Date').dt.year().alias('Year'),
        pl.col('Date').dt.month().alias('Month')
    ])
    # Check if there's a causale field
    causale_col = list(filter(re.compile('^(causale)', re.I).search, df.columns))
    if causale_col:
        df = df.with_columns([
            pl.col(causale_col).alias('Causale'),
            (pl.col(causale_col) == 'EMOLUMENTI').alias('Salary')
        ])
        return df.select(['Date', 'Year', 'Month', 'Amount', 'Credit', 'Causale', 'Salary'])
    else:
        return df.select(['Date', 'Year', 'Month', 'Amount', 'Credit'])

def save_uploaded_files():
    user = st.session_state.username
    if not os.path.exists(f"{DATA_FOLDER}/{user}"):
        os.makedirs(f"{DATA_FOLDER}/{user}")
    st.session_state[f'files{user}'] = len(glob(f"{DATA_FOLDER}/{user}/*.csv"))
    for upl_file in st.session_state.uploaded_files:
        file_df = pl.read_csv(upl_file, has_header=True, separator=';', try_parse_dates=True)
        file_df = transform_data(file_df)
        file_df.write_csv(f"{DATA_FOLDER}/{user}/data{st.session_state[f'files{user}']}.csv", separator=';', date_format='%Y-%m-%d', datetime_format='%Y-%m-%d')
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

def load_data():
    df = pl.read_csv(f'{DATA_FOLDER}/{st.session_state.username}/*.csv', has_header=True, separator=';', try_parse_dates=True)
    if df['Date'].dtype != pl.Date:
        df = df.with_columns([
            pl.col('Date').str.strptime(pl.Date, '%Y-%m-%d')
        ])
    return df.sort('Date')