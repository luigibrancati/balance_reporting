import polars as pl
import streamlit as st
from file_manager import file_lister
from data_manager import file_upload_form, load_data
from graphics import indicators, histplot, piecharts, scatter, month_barplot

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

def build_sidebar():
    with st.sidebar:
        with st.container():
            st.write(f"User: {st.session_state.username}")
        with st.container():
            file_upload_form()
        with st.container():
            file_lister()

def build_graphics(data):
    start_date_col, end_date_col, _ = st.columns(3)
    start_date = start_date_col.date_input("Start date", data['Date'].min())
    end_date = end_date_col.date_input("End date", data['Date'].max())
    data = data.filter((pl.col('Date') >= start_date) & (pl.col('Date') <= end_date))
    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.dataframe(data.to_pandas(), use_container_width=True)
    st.subheader('Amounts')
    st.plotly_chart(indicators(data))
    st.plotly_chart(piecharts(data))
    st.subheader('Amount distribution')
    st.plotly_chart(histplot(data))
    st.subheader('Transactions')
    st.plotly_chart(scatter(data))
    st.subheader('Total by month')
    st.plotly_chart(month_barplot(data))

def build_page():
    local_css("./src/style.css")
    build_sidebar()
    st.title("Balance Reporting")
    data_load_state = st.text('Loading data...')
    try:
        data = load_data()
        data_load_state.text("Done!")
        build_graphics(data)
    except pl.ComputeError or FileNotFoundError:
        data_load_state.text("It seems there's no data")