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
        st.write(f"User: {st.session_state.username}")
        file_upload_form()
        file_lister()

def build_graphics(df):
    start_date_col, end_date_col, credit_multi_col = st.columns(3)
    start_date = start_date_col.date_input("Start date", df['Date'].min())
    end_date = end_date_col.date_input("End date", df['Date'].max())
    credit_multi = credit_multi_col.multiselect("Credit", [True, False], default=[True, False])
    amount_min, amount_max = st.slider("Amount", df['Amount'].min(), df['Amount'].max(), (df['Amount'].min(), df['Amount'].max()))
    df = df.filter(
        (pl.col('Date') >= start_date) &
        (pl.col('Date') <= end_date) &
        (pl.col('Amount') >= amount_min) &
        (pl.col('Amount') <= amount_max) &
        (pl.col('Credit').is_in(credit_multi))
    )
    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.dataframe(df.to_pandas(), use_container_width=True)
    st.subheader('KPIs')
    st.plotly_chart(indicators(df))
    st.plotly_chart(piecharts(df))
    st.subheader('Amount distribution')
    st.plotly_chart(histplot(df))
    st.subheader('Transactions')
    st.plotly_chart(scatter(df))
    st.subheader('Total by month')
    st.plotly_chart(month_barplot(df))

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