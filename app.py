import polars as pl
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

credit_discrete_map = {False: 'blue', True:'red'}
files = 0

@st.cache_data
def load_data():
    df = pl.read_csv('~/.streamlit/data/data*.csv', has_header=True, separator=';', try_parse_dates=True)
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

def indicators(df):
    temp = df
    indicators = make_subplots(
        2, 2,
        specs=[[{"type": "domain"}, {"type": "domain"}], [{"type": "domain"}, {"type": "domain"}]]
    )
    indicator_font_size = 50
    indicator_title_size = 27
    indicators.add_trace(
        go.Indicator(
            mode='number+delta',
            value=temp.filter(pl.col('Credit'))['Amount'].sum() - temp.filter(~pl.col('Credit'))['Amount'].sum(),
            delta={'reference':0.1, 'relative': True, 'valueformat':',.0%'},
            number={'prefix':'€', 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            title={"text": 'Netto transazioni', 'font': {'size': indicator_title_size}}
        ),
        row=1,
        col=1
    )
    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=temp['Amount'].len(),
            number={'valueformat':',.0f', 'font':{'size':indicator_font_size}},
            title={"text": '# transazioni', 'font': {'size': indicator_title_size}}
        ),
        row=1,
        col=2
    )
    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=temp.filter(pl.col('Credit'))['Amount'].max(),
            number={'prefix':'€', 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            title={"text": 'Max in entrata', 'font': {'size': indicator_title_size}}
        ),
        row=2,
        col=1
    )
    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=temp.filter(~pl.col('Credit'))['Amount'].max(),
            number={'prefix':'€', 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            title={"text": 'Max in uscita', 'font': {'size': indicator_title_size}}
        ),
        row=2,
        col=2
    )
    indicators.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=11,
        width=1000
    )
    return indicators

def piecharts(df):
    temp = (
        df.groupby('Credit')
        .agg(
            pl.col('Amount').sum().alias('Amount'),
            pl.col('Date').count().alias('Count')
        ).select('Credit', pl.col('Amount')/pl.col('Amount').sum(), pl.col('Count')/pl.col('Count').sum())
    )
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]], subplot_titles=("Amount", "Count"))
    fig.add_trace(
        go.Pie(
            labels = temp['Credit'].to_list(),
            values = temp['Amount'].to_list(),
            hole = 0.4
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Pie(
            labels = temp['Credit'].to_list(),
            values = temp['Count'].to_list(),
            hole = 0.4
        ),
        row=1,
        col=2
    )
    fig.update_layout(height=500, width=1000, legend={'title':'Credit'})
    return fig

def histplot(df):
    fig = px.histogram(
        data_frame = df.to_pandas(),
        x = 'Amount',
        histnorm = 'percent',
        title = 'Amount distribution',
        facet_row = 'Credit',
        color = 'Credit',
        color_discrete_map = credit_discrete_map,
        nbins = 50,
        height = 800
    )
    return fig

def scatter(df):
    fig = px.scatter(
        data_frame = df.to_pandas(),
        x = 'Date',
        y = 'Amount',
        color = 'Credit',
        color_discrete_map=credit_discrete_map
    )
    return fig


st.title("Balance Reporting")
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load the dataframe.
try:
    data = load_data()
except pl.ComputeError:
    data_load_state = st.text("It seems there's no data")
    uploaded_file = st.file_uploader("Upload Data")
    if uploaded_file is not None:
        data_load_state.text("Received file")
        file = pl.read_csv(uploaded_file, separator=';')
        st.write(file.to_pandas())
        data_load_state.text("Read file")
        file.write_csv(f'~/.streamlit/data/data{files}.csv', separator=';')
        data_load_state.text("Written file")
        files += 1
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

