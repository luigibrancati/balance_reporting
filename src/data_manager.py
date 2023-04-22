from config import DATA_FOLDER
import streamlit as st
import re
import polars as pl

def select_best_date_field(date_cols:list[str]) -> str:
    best_data = list(filter(re.compile('data valuta', re.I).match, date_cols))
    if not best_data:
        best_data = date_cols
    return best_data[0]

def transform_data(df:pl.DataFrame) -> pl.DataFrame:
    # Coalesce numeric columns
    numeric_columns = sorted(df.select(pl.col(pl.NUMERIC_DTYPES)).columns) # Entrate, Uscite
    bool_column = df.select(pl.col(pl.Boolean)).columns
    df = df.with_columns([pl.col(col).fill_null(0.0) for col in numeric_columns])
    if len(numeric_columns) == 2 and len(bool_column) == 0:
        df = pl.concat([
            df.with_columns([pl.col(numeric_columns[0]).alias('Amount'), pl.lit(True).alias('Credit')]).drop(numeric_columns),
            df.with_columns([pl.col(numeric_columns[1]).alias('Amount'), pl.lit(False).alias('Credit')]).drop(numeric_columns)
        ])
    elif len(numeric_columns) == 1 and len(bool_column) == 1:
        df = df.with_columns([
            pl.col(numeric_columns).round(2).alias('Amount'),
            pl.col(bool_column).round(2).alias('Credit')
        ])
    # filter out zeroes
    df = df.filter(pl.col('Amount') > 0)
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
        return df.select(['Date', 'Year', 'Month', 'Amount', 'Credit', pl.lit('').alias('Causale'), pl.lit(False).alias('Salary')])

def load_data() -> pl.DataFrame:
    df = pl.read_csv(f'{DATA_FOLDER}/{st.session_state.username}/*.csv', has_header=True, separator=';', try_parse_dates=True)
    if df['Date'].dtype != pl.Date:
        df = df.with_columns([
            pl.col('Date').str.strptime(pl.Date, '%Y-%m-%d')
        ])
    return df.sort('Date')