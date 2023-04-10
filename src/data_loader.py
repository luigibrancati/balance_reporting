import polars as pl
from config import DATA_FOLDER

def load_data(user):
    df = pl.read_csv(f'{DATA_FOLDER}/{user}/*.csv', has_header=True, separator=';', try_parse_dates=True)
    df = (
        df.rename({'Data valuta':'Date'})
        .with_columns([
            pl.coalesce([pl.col('Entrate'), pl.col('Uscite')]).alias('Amount'),
            pl.col('Entrate').is_not_null().alias('Credit'),
            (pl.col('Causale') == 'EMOLUMENTI').alias('Salary'),
            pl.col('Date').str.strptime(pl.Date, "%d/%m/%Y")
        ])
        .with_columns([
            pl.col('Date').dt.year().alias('Year'),
            pl.col('Date').dt.month().alias('Month')
        ])
        .select(['Date', 'Year', 'Month', 'Amount', 'Credit', 'Salary'])
    )
    df = df.sort('Date')
    return df
