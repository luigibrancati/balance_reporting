import polars as pl
import streamlit as st
from file_manager import file_lister, file_upload_form, list_files
from data_manager import load_data
from graphics import indicators, histplot, piecharts, scatter, month_barplot
from pathlib import Path
from exceptions import NoDataException

def local_css(filename:Path) -> None:
    with open(filename) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

def build_sidebar() -> None:
    with st.sidebar:
        st.write(f"User: {st.session_state.username}")
        file_upload_form()
        file_lister(list_files())

def build_graphics(df:pl.DataFrame) -> None:
    start_date_col, end_date_col, credit_multi_col, conto_multi_col = st.columns(4)
    start_date = start_date_col.date_input("Start date", df['Date'].min())
    end_date = end_date_col.date_input("End date", df['Date'].max())
    credit_multi = credit_multi_col.multiselect("Credit", [True, False], default=[True, False])
    conto_multi = conto_multi_col.multiselect("Conto", df['Conto'].unique().to_list(), default=df['Conto'].unique().to_list())
    amount_min, amount_max = st.slider("Amount", df['Amount'].min(), df['Amount'].max(), (df['Amount'].min(), df['Amount'].max()))
    df_filtered = df.filter(
        (pl.col('Date') >= start_date) &
        (pl.col('Date') <= end_date) &
        (pl.col('Amount') >= amount_min) &
        (pl.col('Amount') <= amount_max) &
        (pl.col('Credit').is_in(credit_multi)) &
        (pl.col('Conto').is_in(conto_multi))
    )
    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.dataframe(df_filtered.to_pandas(), use_container_width=True)
    st.subheader('KPIs')
    st.plotly_chart(indicators(df_filtered))
    st.plotly_chart(piecharts(df_filtered))
    st.subheader('Amount distribution')
    st.plotly_chart(histplot(df_filtered))
    st.subheader('Transactions')
    st.plotly_chart(scatter(df_filtered))
    st.subheader('Total by month')
    st.plotly_chart(month_barplot(df_filtered))

def build_page() -> None:
    local_css("./src/style.css")
    build_sidebar()
    st.title("Balance Reporting")
    data_load_state = st.text('Loading data...')
    try:
        data = load_data(list_files())
        data_load_state.text("Done!")
        build_graphics(data)
    except NoDataException:
        data_load_state.text("It seems there's no data")