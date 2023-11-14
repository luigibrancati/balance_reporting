import polars as pl
from pathlib import Path
from exceptions import NoDataException
from abc import ABC, abstractmethod
from enum import Enum

class Fields(Enum):
    Date = 'Date'
    Year = 'Year'
    Month = 'Month'
    Amount = 'Amount'
    Credit = 'Credit'
    ABI = 'ABI'
    Salary = 'Salary'
    Bank = 'Bank'


class DataReader(ABC):

    @abstractmethod
    def _standardize_amount(self, df:pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def _standardize_date(self, df:pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def _standardize_causale(self, df:pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def _add_salary(self, df:pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def _add_bank(self, df:pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError()

    def _filter_data(self, df:pl.DataFrame) -> pl.DataFrame:
        return df.filter(pl.col(Fields.Amount) > 0)

    def _typing(self, df:pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.col(Fields.Date).cast(pl.Date),
            pl.col(Fields.Year).cast(pl.UInt16),
            pl.col(Fields.Month).cast(pl.UInt8),
            pl.col(Fields.Amount).cast(pl.UInt32),
            pl.col(Fields.Credit).cast(pl.Boolean),
            pl.col(Fields.ABI).cast(pl.Utf8),
            pl.col(Fields.Salary).cast(pl.Boolean),
            pl.col(Fields.Bank).cast(pl.Utf8),
        ])

    def transform_data(self, df:pl.DataFrame) -> pl.DataFrame:
        # Coalesce numeric columns
        df = self._standardize_amount(df)
        # select best date field
        df = self._standardize_date(df)
        # Check if there's a causale field
        df = self._standardize_causale(df)
        # Add salary field
        df = self._add_salary(df)
        # Add bank
        df = self._add_bank(df)
        # filter out zeroes
        df = self._filter_data(df)
        # Set typing
        df = self._typing(df)
        return df.select([f for f in Fields])

    # def load_data(filelist: list[Path]) -> pl.DataFrame:
    #     if filelist:
    #         df = pl.concat([
    #             pl.read_csv(file, has_header=True, separator=';', try_parse_dates=True) for file in filelist
    #         ])
    #         if df[Fields.Date].dtype != pl.Date:
    #             df = df.with_columns([
    #                 pl.col(Fields.Date).str.strptime(pl.Date, '%Y-%m-%d')
    #             ])
    #         return df.sort(Fields.Date)
    #     else:
    #         raise NoDataException("No data found")


class BMEDDataReader(DataReader):
    def _standardize_amount(self, df:pl.DataFrame) -> pl.DataFrame:
        numeric_columns = ["Entrate", "Uscite"]
        df = df.with_columns([pl.col(col).fill_null(0.0) for col in numeric_columns])
        return pl.concat([
            df.with_columns([
                pl.col(numeric_columns[0]).round(2).alias(Fields.Amount),
                pl.lit(True).alias(Fields.Credit)
            ]).drop(numeric_columns),
            df.with_columns([
                pl.col(numeric_columns[1]).round(2).alias(Fields.Amount),
                pl.lit(False).alias(Fields.Credit)
            ]).drop(numeric_columns)
        ])

    def _standardize_date(self, df:pl.DataFrame) -> pl.DataFrame:
        date_col = "Data Operazione"
        df = df.with_columns([
            pl.col(date_col).alias(Fields.Date).cast(pl.Date)
        ]).with_columns([
            pl.col(Fields.Date).dt.year().alias(Fields.Year),
            pl.col(Fields.Date).dt.month().alias(Fields.Month)
        ])
        return df

    def _standardize_causale(self, df: pl.DataFrame) -> pl.DataFrame:
        causale_col = ["Causale"]
        return df.with_columns([
            pl.col(causale_col).alias(Fields.ABI)
        ])

    def _add_salary(self, df: pl.DataFrame) -> pl.DataFrame:
        causale_col = ["Causale"]
        return df.with_columns([
            (pl.col(causale_col) == 'EMOLUMENTI').alias(Fields.Salary)
        ])

    def _add_bank(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit("BMED").alias(Fields.Bank)
        ])


class FloweDataReader(DataReader):
    def _standardize_amount(self, df:pl.DataFrame) -> pl.DataFrame:
        numeric_columns = ["Entrate", "Uscite"]
        df = df.with_columns([pl.col(col).fill_null(0.0) for col in numeric_columns])
        return pl.concat([
            df.with_columns([
                pl.col(numeric_columns[0]).round(2).alias(Fields.Amount),
                pl.lit(True).alias(Fields.Credit)
            ]).drop(numeric_columns),
            df.with_columns([
                pl.col(numeric_columns[1]).round(2).alias(Fields.Amount),
                pl.lit(False).alias(Fields.Credit)
            ]).drop(numeric_columns)
        ])

    def _standardize_date(self, df:pl.DataFrame) -> pl.DataFrame:
        date_col = "Data Op"
        df = df.with_columns([
            pl.col(date_col).alias(Fields.Date).cast(pl.Date)
        ]).with_columns([
            pl.col(Fields.Date).dt.year().alias(Fields.Year),
            pl.col(Fields.Date).dt.month().alias(Fields.Month)
        ])
        return df

    def _standardize_causale(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.col("").alias(Fields.ABI)
        ])

    def _add_salary(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit(False).alias(Fields.Salary)
        ])

    def _add_bank(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit("FLOWE").alias(Fields.Bank)
        ])


source_mapping = {
    "BMED": BMEDDataReader,
    "Flowe": FloweDataReader
}