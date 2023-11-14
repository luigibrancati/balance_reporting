import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import CREDIT_DISCRETE_MAP, GRAPHICS_WIDTH_PX, MIN_FONT_SIZE
from balance_reporting.data_reader.data_reader import Fields

def indicators(df:pl.DataFrame) -> go.Figure:
    temp = df
    indicators = make_subplots(
        2, 2,
        specs=[[{"type": "domain"}, {"type": "domain"}], [{"type": "domain"}, {"type": "domain"}]]
    )
    indicator_font_size = 50
    indicator_title_size = 27
    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=temp.filter(pl.col(Fields.Credit))[Fields.Amount].sum() - temp.filter(~pl.col(Fields.Credit))[Fields.Amount].sum(),
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
            value=temp[Fields.Amount].len(),
            number={'valueformat':',.0f', 'font':{'size':indicator_font_size}},
            title={"text": '# transazioni', 'font': {'size': indicator_title_size}}
        ),
        row=1,
        col=2
    )
    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=temp.filter(pl.col(Fields.Credit))[Fields.Amount].max(),
            number={'prefix':'€', 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            title={"text": 'Max in entrata', 'font': {'size': indicator_title_size}}
        ),
        row=2,
        col=1
    )
    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=temp.filter(~pl.col(Fields.Credit))[Fields.Amount].max(),
            number={'prefix':'€', 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            title={"text": 'Max in uscita', 'font': {'size': indicator_title_size}}
        ),
        row=2,
        col=2
    )
    indicators.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
        width=GRAPHICS_WIDTH_PX
    )
    return indicators

def piecharts(df:pl.DataFrame) -> go.Figure:
    temp = (
        df.groupby(Fields.Credit)
        .agg(
            pl.col(Fields.Amount).sum().alias(Fields.Amount),
            pl.col(Fields.Date).count().alias('Count')
        ).select(Fields.Credit, pl.col(Fields.Amount)/pl.col(Fields.Amount).sum(), pl.col('Count')/pl.col('Count').sum())
        .sort(Fields.Credit, descending=True)
    )
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]], subplot_titles=("Amount", "Count"))
    fig.add_trace(
        go.Pie(
            labels = temp[Fields.Credit].to_list(),
            values = temp[Fields.Amount].to_list(),
            marker_colors = temp[Fields.Credit].apply(lambda c: CREDIT_DISCRETE_MAP[c]).to_list(),
            hole = 0.4
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Pie(
            labels = temp[Fields.Credit].to_list(),
            values = temp['Count'].to_list(),
            marker_colors = temp[Fields.Credit].apply(lambda c: CREDIT_DISCRETE_MAP[c]).to_list(),
            hole = 0.4
        ),
        row=1,
        col=2
    )
    fig.update_layout(
        height=500,
        width=GRAPHICS_WIDTH_PX,
        legend={'title':Fields.Credit},
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
    )
    return fig

def histplot(df:pl.DataFrame) -> go.Figure:
    fig = px.histogram(
        data_frame = df.to_pandas(),
        x = Fields.Amount,
        histnorm = 'percent',
        barmode='group',
        color = Fields.Credit,
        color_discrete_map = CREDIT_DISCRETE_MAP,
        category_orders = {Fields.Credit: [True, False]},
        nbins = 40,
        height = 800,
        width=GRAPHICS_WIDTH_PX,
        labels = {Fields.Amount:'Amount (€)'}
    )
    fig.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
    )
    return fig

def scatter(df:pl.DataFrame) -> go.Figure:
    fig = px.scatter(
        data_frame = df.to_pandas(),
        x = Fields.Date,
        y = Fields.Amount,
        color = Fields.Credit,
        color_discrete_map=CREDIT_DISCRETE_MAP,
        category_orders = {Fields.Credit: [True, False]},
        height = 800,
        width=GRAPHICS_WIDTH_PX,
        labels = {Fields.Amount:'Amount (€)'},
        hover_data=[Fields.Date, Fields.Amount, Fields.Credit, Fields.Bank]
    )
    fig.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
    )
    return fig

def month_barplot(df:pl.DataFrame) -> go.Figure:
    temp = (
        df.with_columns([
            pl.col(Fields.Credit).cast(str),
            pl.col(Fields.Date).dt.strftime('%Y-%m').alias('YearMonth')
        ])
        .groupby(['YearMonth', Fields.Credit])
        .agg(pl.sum(Fields.Amount).alias(Fields.Amount)).sort(['YearMonth', Fields.Credit])
    )
    temp = pl.concat([
        temp,
        temp.pivot(values=Fields.Amount, columns=Fields.Credit, index=['YearMonth'])
        .select(
            'YearMonth',
            pl.lit('total').alias(Fields.Credit),
            (pl.col('true') - pl.col('false')).alias(Fields.Amount)
        )
    ])
    fig = px.bar(
        data_frame=temp.to_pandas(),
        x = 'YearMonth',
        y = Fields.Amount,
        color = Fields.Credit,
        barmode='group',
        color_discrete_map=CREDIT_DISCRETE_MAP,
        category_orders = {Fields.Credit: ['true', 'false', 'total']},
        height = 800,
        width=GRAPHICS_WIDTH_PX,
        text_auto = '.1f',
        labels = {Fields.Amount:'Amount (€)'}
    )
    fig.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
    )
    return fig
