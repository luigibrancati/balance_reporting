import polars as pl
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
        return df.filter(pl.col(Fields.Amount.value) > 0)

    def _typing(self, df:pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.col(Fields.Date.value).cast(pl.Date),
            pl.col(Fields.Year.value).cast(pl.UInt16),
            pl.col(Fields.Month.value).cast(pl.UInt8),
            pl.col(Fields.Amount.value).cast(pl.Float32),
            pl.col(Fields.Credit.value).cast(pl.Boolean),
            pl.col(Fields.ABI.value).cast(pl.Utf8),
            pl.col(Fields.Salary.value).cast(pl.Boolean),
            pl.col(Fields.Bank.value).cast(pl.Utf8),
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
        # df = self._typing(df)
        return df.select([f.value for f in Fields])


class BMEDDataReader(DataReader):
    def _standardize_amount(self, df:pl.DataFrame) -> pl.DataFrame:
        numeric_columns = ["Entrate", "Uscite"]
        df = df.with_columns([pl.col(col).fill_null(0.0).cast(pl.Float32) for col in numeric_columns])
        return pl.concat([
            df.with_columns([
                pl.col(numeric_columns[0]).round(2).alias(Fields.Amount.value),
                pl.lit(True).alias(Fields.Credit.value)
            ]).drop(numeric_columns),
            df.with_columns([
                pl.col(numeric_columns[1]).round(2).alias(Fields.Amount.value),
                pl.lit(False).alias(Fields.Credit.value)
            ]).drop(numeric_columns)
        ])

    def _standardize_date(self, df:pl.DataFrame) -> pl.DataFrame:
        date_col = "Operazione"
        df = df.with_columns([
            pl.col(date_col).str.strptime(pl.Date, "%d/%m/%Y").alias(Fields.Date.value)
        ]).with_columns([
            pl.col(Fields.Date.value).dt.year().alias(Fields.Year.value),
            pl.col(Fields.Date.value).dt.month().alias(Fields.Month.value)
        ])
        return df

    def _standardize_causale(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit("").alias(Fields.ABI.value)
        ])

    def _add_salary(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit(False).alias(Fields.Salary.value)
        ])

    def _add_bank(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit("BMED").alias(Fields.Bank.value)
        ])


class FloweDataReader(DataReader):
    def _standardize_amount(self, df:pl.DataFrame) -> pl.DataFrame:
        numeric_columns = ["ENTRATE", "USCITE"]
        df = df.with_columns([pl.col(col).fill_null(0.0).cast(pl.Float32) for col in numeric_columns])
        return pl.concat([
            df.with_columns([
                pl.col(numeric_columns[0]).round(2).alias(Fields.Amount.value),
                pl.lit(True).alias(Fields.Credit.value)
            ]).drop(numeric_columns),
            df.with_columns([
                pl.col(numeric_columns[1]).round(2).alias(Fields.Amount.value),
                pl.lit(False).alias(Fields.Credit.value)
            ]).drop(numeric_columns)
        ])

    def _standardize_date(self, df:pl.DataFrame) -> pl.DataFrame:
        date_col = "DATA OP"
        df = df.with_columns([
            pl.col(date_col).str.strptime(pl.Date, "%d/%m/%Y").alias(Fields.Date.value)
        ]).with_columns([
            pl.col(Fields.Date.value).dt.year().alias(Fields.Year.value),
            pl.col(Fields.Date.value).dt.month().alias(Fields.Month.value)
        ])
        return df

    def _standardize_causale(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit("").alias(Fields.ABI.value)
        ])

    def _add_salary(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit(False).alias(Fields.Salary.value)
        ])

    def _add_bank(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.lit("FLOWE").alias(Fields.Bank.value)
        ])


source_mapping = {
    "BMED": BMEDDataReader,
    "FLOWE": FloweDataReader
}
