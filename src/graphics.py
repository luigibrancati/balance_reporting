import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import CREDIT_DISCRETE_MAP, GRAPHICS_WIDTH_PX

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
        width=GRAPHICS_WIDTH_PX
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
    fig.update_layout(height=500, width=GRAPHICS_WIDTH_PX, legend={'title':'Credit'})
    return fig

def histplot(df):
    fig = px.histogram(
        data_frame = df.to_pandas(),
        x = 'Amount',
        histnorm = 'percent',
        title = 'Amount distribution',
        facet_row = 'Credit',
        color = 'Credit',
        color_discrete_map = CREDIT_DISCRETE_MAP,
        nbins = 50,
        height = 800,
        width=GRAPHICS_WIDTH_PX
    )
    return fig

def scatter(df):
    fig = px.scatter(
        data_frame = df.to_pandas(),
        x = 'Date',
        y = 'Amount',
        color = 'Credit',
        color_discrete_map=CREDIT_DISCRETE_MAP,
        height = 800,
        width=GRAPHICS_WIDTH_PX
    )
    return fig
