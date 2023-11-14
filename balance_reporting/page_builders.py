import polars as pl
import streamlit as st
from file_manager import file_upload_form, list_files, delete_file, convert_file, load_saved_files
from balance_reporting.data_reader.data_reader import Fields
from graphics import indicators, histplot, piecharts, scatter, month_barplot
from pathlib import Path
from exceptions import NoDataException

def local_css(filename:Path) -> None:
    with open(filename) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


def file_lister(filelist: list[Path]) -> None:
    with st.expander("Saved files"):
        col1, col2, col3 = st.columns([2,1,1])
        for file in filelist:
            col1.write(file.name)
            col2.download_button("Download", data=convert_file(file), file_name=file.name)
            col3.button("Delete", on_click=lambda: delete_file(file), key=file)


def build_sidebar() -> None:
    with st.sidebar:
        st.write(f"User: {st.session_state.username}")
        file_upload_form()
        file_lister(list_files())

def build_graphics(df:pl.DataFrame) -> None:
    if not df.is_empty():
        start_date_col, end_date_col, credit_multi_col, conto_multi_col = st.columns(4)
        start_date = start_date_col.date_input("Start date", df[Fields.Date].min())
        end_date = end_date_col.date_input("End date", df[Fields.Date].max())
        credit_multi = credit_multi_col.multiselect("Credit", [True, False], default=[True, False])
        conto_var = df[Fields.Bank].unique().sort().to_list()
        conto_multi = conto_multi_col.multiselect("Conto", conto_var, default=conto_var)
        amount_min, amount_max = st.slider("Amount", df[Fields.Amount].min(), df[Fields.Amount].max(), (df[Fields.Amount].min(), df[Fields.Amount].max()))
        df_filtered = df.filter(
            (pl.col(Fields.Date) >= start_date) &
            (pl.col(Fields.Date) <= end_date) &
            (pl.col(Fields.Amount) >= amount_min) &
            (pl.col(Fields.Amount) <= amount_max) &
            (pl.col(Fields.Credit).is_in(credit_multi)) &
            (pl.col(Fields.Bank).is_in(conto_multi))
        )
        if not df_filtered.is_empty():
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
    else:
        raise NoDataException()

def build_page() -> None:
    local_css("./src/style.css")
    build_sidebar()
    st.title("Balance Reporting")
    data_load_state = st.text('Loading data...')
    try:
        data = load_saved_files()
        data_load_state.text("Done!")
        build_graphics(data)
    except NoDataException:
        data_load_state.text("It seems there's no data")