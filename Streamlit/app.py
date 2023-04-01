import polars as pl
import streamlit as st
from functions import load_data, indicators, piecharts, histplot, scatter

st.title("Balance Reporting")
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache_data)")

start_date = st.date_input("Start date", data['Date'].min())
end_date = st.date_input("End date", data['Date'].max())
data = data.filter((pl.col('Date')>=start_date) & (pl.col('Date')<=end_date))

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data.to_pandas())

st.subheader('Amounts')
st.plotly_chart(indicators(data))
st.plotly_chart(piecharts(data))
st.subheader('Amount distribution')
st.plotly_chart(histplot(data))
st.subheader('Transactions')
st.plotly_chart(scatter(data))

