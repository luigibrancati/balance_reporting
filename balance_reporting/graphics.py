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
            value=temp.filter(pl.col(Fields.Credit.value))[Fields.Amount.value].sum() - temp.filter(~pl.col(Fields.Credit.value))[Fields.Amount.value].sum(),
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
            value=temp[Fields.Amount.value].len(),
            number={'valueformat':',.0f', 'font':{'size':indicator_font_size}},
            title={"text": '# transazioni', 'font': {'size': indicator_title_size}}
        ),
        row=1,
        col=2
    )
    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=temp.filter(pl.col(Fields.Credit.value))[Fields.Amount.value].max(),
            number={'prefix':'€', 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            title={"text": 'Max in entrata', 'font': {'size': indicator_title_size}}
        ),
        row=2,
        col=1
    )
    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=temp.filter(~pl.col(Fields.Credit.value))[Fields.Amount.value].max(),
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
        df.groupby(Fields.Credit.value)
        .agg(
            pl.col(Fields.Amount.value).sum().alias(Fields.Amount.value),
            pl.col(Fields.Date.value).count().alias('Count')
        ).select(Fields.Credit.value, pl.col(Fields.Amount.value)/pl.col(Fields.Amount.value).sum(), pl.col('Count')/pl.col('Count').sum())
        .sort(Fields.Credit.value, descending=True)
    )
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]], subplot_titles=("Amount", "Count"))
    fig.add_trace(
        go.Pie(
            labels = temp[Fields.Credit.value].to_list(),
            values = temp[Fields.Amount.value].to_list(),
            marker_colors = temp[Fields.Credit.value].apply(lambda c: CREDIT_DISCRETE_MAP[c]).to_list(),
            hole = 0.4
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Pie(
            labels = temp[Fields.Credit.value].to_list(),
            values = temp['Count'].to_list(),
            marker_colors = temp[Fields.Credit.value].apply(lambda c: CREDIT_DISCRETE_MAP[c]).to_list(),
            hole = 0.4
        ),
        row=1,
        col=2
    )
    fig.update_layout(
        height=500,
        width=GRAPHICS_WIDTH_PX,
        legend={'title':Fields.Credit.value},
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
    )
    return fig

def histplot(df:pl.DataFrame) -> go.Figure:
    fig = px.histogram(
        data_frame = df.to_pandas(),
        x = Fields.Amount.value,
        histnorm = 'percent',
        barmode='group',
        color = Fields.Credit.value,
        color_discrete_map = CREDIT_DISCRETE_MAP,
        category_orders = {Fields.Credit.value: [True, False]},
        nbins = 40,
        height = 800,
        width=GRAPHICS_WIDTH_PX,
        labels = {Fields.Amount.value:'Amount (€)'}
    )
    fig.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
    )
    return fig

def scatter(df:pl.DataFrame) -> go.Figure:
    fig = px.scatter(
        data_frame = df.to_pandas(),
        x = Fields.Date.value,
        y = Fields.Amount.value,
        color = Fields.Credit.value,
        color_discrete_map=CREDIT_DISCRETE_MAP,
        category_orders = {Fields.Credit.value: [True, False]},
        height = 800,
        width=GRAPHICS_WIDTH_PX,
        labels = {Fields.Amount.value:'Amount (€)'},
        hover_data=[Fields.Date.value, Fields.Amount.value, Fields.Credit.value, Fields.Bank.value]
    )
    fig.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
    )
    return fig

def month_barplot(df:pl.DataFrame) -> go.Figure:
    temp = (
        df.with_columns([
            pl.col(Fields.Credit.value).cast(str),
            pl.col(Fields.Date.value).dt.strftime('%Y-%m').alias('YearMonth')
        ])
        .groupby(['YearMonth', Fields.Credit.value])
        .agg(pl.sum(Fields.Amount.value).alias(Fields.Amount.value)).sort(['YearMonth', Fields.Credit.value])
    )
    temp = pl.concat([
        temp,
        temp.pivot(values=Fields.Amount.value, columns=Fields.Credit.value, index=['YearMonth'])
        .select(
            'YearMonth',
            pl.lit('total').alias(Fields.Credit.value),
            (pl.col('true') - pl.col('false')).alias(Fields.Amount.value)
        )
    ])
    fig = px.bar(
        data_frame=temp.to_pandas(),
        x = 'YearMonth',
        y = Fields.Amount.value,
        color = Fields.Credit.value,
        barmode='group',
        color_discrete_map=CREDIT_DISCRETE_MAP,
        category_orders = {Fields.Credit.value: ['true', 'false', 'total']},
        height = 800,
        width=GRAPHICS_WIDTH_PX,
        text_auto = '.1f',
        labels = {Fields.Amount.value:'Amount (€)'}
    )
    fig.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=MIN_FONT_SIZE,
    )
    return fig
