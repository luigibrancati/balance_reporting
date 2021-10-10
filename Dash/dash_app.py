from dash.html.Label import Label
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import transform
import dash_daq as daq

number_formatting = "{:,.2f}" # La virgola separa le migliaia, e hanno 2 valori decimali
mesi = ('Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre')
mesi_short = tuple(map(lambda e: e[:3], mesi))
valuta = '€'
figsize_px = (1366, 768)

app = dash.Dash(__name__)
df = None

# Drawing Functions
def draw_water(df_filtered):
    dftotale = df_filtered.groupby(['Anno', 'Mese'], as_index=False)[transform.config.campi['importo']].sum()\
        .assign(Direzione='Totale').append(
            df_filtered.groupby(['Anno', 'Mese', 'Direzione'], as_index=False)[transform.config.campi['importo']].sum(),
            ignore_index=True
        ).rename({transform.config.campi['importo']:'Balance'}, axis=1)
    dftotale['help_field'] = dftotale['Direzione'].apply(lambda d: {'Entrate':0, 'Uscite':1, 'Totale':2}[d])
    dftotale.sort_values(['Anno','Mese','help_field'], inplace=True)
    dftotale.drop('help_field', axis=1, inplace=True)
    dftotale['AnnoMese'] = dftotale.apply(lambda r: mesi_short[int(r['Mese'])-1]+" "+str(int(r['Anno'])), axis=1)
    

    waterfall_balance = go.Figure()

    for am in dftotale['AnnoMese'].unique():
        waterfall_balance.add_trace(
            trace = go.Waterfall(
                name = am,
                orientation = "v",
                measure = ["relative", "relative", "total"],
                x = [
                    [am]*3,
                    dftotale[dftotale['AnnoMese']==am]['Direzione'].values
                ],
                textposition = "outside",
                text = np.round(dftotale[dftotale['AnnoMese']==am]['Balance'].values, decimals=2),
                y = dftotale[dftotale['AnnoMese']==am]['Balance'].values,
                connector = {"line":{"color":"rgb(63, 63, 63)"}}
        ))

    waterfall_balance.update_layout(
        title = "Importo per Mese"+f"<br><sup>Importo transato (in entrata e in uscita) per ogni Mese</sup>",
        showlegend = True,
        height = figsize_px[1],
        width = figsize_px[0],
        uniformtext_mode = 'hide',
        uniformtext_minsize = 8,
        yaxis_title = f"Importo ({valuta})",
        transition_duration=500
    )

    waterfall_balance.update_traces(textfont_size=12, textposition='outside')

    waterfall_balance.update_traces(
        textposition='outside',
        texttemplate='%{text:,}'
    )

    df_cum = dftotale[dftotale['Direzione']=='Totale']
    df_cum['Balance_cum'] = df_cum['Balance'].cumsum() + transform.config.valore_base
    waterfall_balance.add_trace(
        go.Scatter(
            name='Cumulativo',
            mode='lines+text+markers',
            x=[
                df_cum['AnnoMese'],
                df_cum['Direzione']
            ],
            y=df_cum['Balance_cum'],
            line=dict(color='royalblue')
        )
    )
    return waterfall_balance

def draw_abi(df_filtered):
    bar_abi = go.Figure()
    try:
        bar_abi = px.bar(
            df_filtered.groupby([transform.config.campi['abi'], 'Direzione'], as_index=False)[transform.config.campi['importo']].sum(), 
            x=transform.config.campi['abi'], 
            y=transform.config.campi['importo'], 
            text=transform.config.campi['importo'],
            labels={transform.config.campi['importo']:f'Importo ({valuta})'}
        )

        bar_abi.update_layout(
            title = "Importo per Causale ABI"+f"<br><sup>Importo transato (in entrata e in uscita) per ogni Causale ABI</sup>",
            showlegend = True,
            height = figsize_px[1],
            width = figsize_px[0],
            uniformtext_mode='hide',
            uniformtext_minsize=8
        )

        bar_abi.update_traces(
            textposition='outside',
            texttemplate="%{text:,}"
        )
    except KeyError:
        pass
    return bar_abi

def draw_scatter(df_filtered, frac=0.6):
    trans_scatter = px.scatter(
        df_filtered,
        x=transform.config.campi['data_contabile'],
        y=transform.config.campi['importo'],
        labels={transform.config.campi['importo']:f'Importo ({valuta})'},
        trendline='lowess',
        trendline_color_override='red',
        trendline_options=dict(frac=frac)
    )

    trans_scatter.update_layout(
        title = 'Distribuzione transazioni per data',
        showlegend = True,
        height = figsize_px[1],
        width = figsize_px[0],
        uniformtext_mode='hide',
        uniformtext_minsize=8
    )

    trans_scatter.update_traces(
        texttemplate='%{value:,.2f}'
    )
    return trans_scatter
    
def draw_pie(df_filtered):
    pie_spese = px.pie(
        df_filtered.groupby('Direzione', as_index=False)['Importo_abs'].sum(),
        names='Direzione',
        values='Importo_abs',
        hole=0.5
    )
    
    pie_spese.update_traces(textposition='inside', textinfo='label+percent')

    pie_spese.update_layout(
        title = 'Direzione spesa',
        uniformtext_mode='hide',
        uniformtext_minsize=8,
        height = figsize_px[1]*0.5,
        width = figsize_px[0]*0.45
    )

    return pie_spese

def draw_indicators(df_filtered):
    indicators = go.Figure()
    indicator_font_size = 40
    indicator_title_size = 20

    indicators.add_trace(
        go.Indicator(
            mode='number+delta',
            value=df_filtered[transform.config.campi['importo']].sum()+transform.config.valore_base,
            delta={'reference':transform.config.valore_base, 'relative': True, 'valueformat':',.0%'},
            number={'prefix':valuta, 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            domain={'x':[0,0.4], 'y':[0.6,1]},
            title={"text": 'Totale transazioni', 'font': {'size': indicator_title_size}}
        )
    )

    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=df_filtered[transform.config.campi['importo']].count(),
            number={'valueformat':',.0f', 'font':{'size':indicator_font_size}},
            domain={'x':[0.6,1], 'y':[0.6,1]},
            title={"text": '# transazioni', 'font': {'size': indicator_title_size}}
        )
    )

    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=df_filtered[transform.config.campi['importo']].max(),
            number={'prefix':valuta, 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            domain={'x':[0,0.4], 'y':[0,0.4]},
            title={"text": 'Max in entrata', 'font': {'size': indicator_title_size}}
        )
    )

    indicators.add_trace(
        go.Indicator(
            mode='number',
            value=df_filtered[transform.config.campi['importo']].min(),
            number={'prefix':valuta, 'valueformat':',.2f', 'font':{'size':indicator_font_size}},
            domain={'x':[0.6,1], 'y':[0,0.4]},
            title={"text": 'Max in uscita', 'font': {'size': indicator_title_size}}
        )
    )

    indicators.update_layout(
        uniformtext_mode='hide',
        uniformtext_minsize=8,
        height = figsize_px[1]*0.5,
        width = figsize_px[0]*0.45
    )

    return indicators

def draw_table(df_filtered):
    all_table = dash_table.DataTable(
        id='datatable-interactivity',
        columns=[{'name':i, 'id':i, 'deletable':True} for i in df_filtered.columns],
        data=df_filtered.to_dict('records'),
        export_format="csv",
        style_table={'width':figsize_px[0]*0.9, 'overflowY': 'auto', 'overflowX':'auto'},
        style_data={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0
        },
        style_header={
            'whitespace':'fixed',
            'width':'auto'
        },
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df.to_dict('records')
        ],
        tooltip_duration=None,
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_deletable=True,
        page_action="native",
        page_current= 0,
        page_size=40
    )

    return [
        html.H3(
            style={'font-family':'"Open Sans", verdana, arial, sans-serif','font-size':'17px','font-weight':'normal','white-space': 'pre', 'fill':'rgb(42, 63, 95)'}, 
            children="Dettaglio transazioni"
            ),
        all_table]

    global update_styles
    @app.callback(
        Output('datatable-interactivity', 'style_data_conditional'),
        Input('datatable-interactivity', 'selected_columns')
    )
    def update_styles(selected_columns):
        return [{
            'if': { 'column_id': i },
            'background_color': '#D2F3FF'
        } for i in selected_columns]

def create_app(data_folder):
    transform.set_config(data_folder)
    global df
    df = transform.preprocess_df(transform.import_df())
    # Layout
    app.layout = html.Div(
        children=[
            html.Div(
                id='filters_div',
                style={'width':figsize_px[0]},
                children=[
                    html.Div(
                        id='dates_div',
                        children=[
                            html.Label(id='dates_label', children='Date'),
                            dcc.DatePickerRange(
                                id='date_picker',
                                start_date=df[transform.config.campi['data_contabile']].min(),
                                end_date=df[transform.config.campi['data_contabile']].max(),
                                display_format="Do MMM YYYY"
                            )
                    ]),
                    html.Br(),
                    html.Div(
                        id='directions_div',
                        children=[
                            html.Label(id='directions_label', children='Direzione'),
                            dcc.Dropdown(
                                id='direction_menu',
                                options=[{'label':ca, 'value':ca} for ca in sorted(df['Direzione'].unique())],
                                value=sorted(list(df['Direzione'].unique())),
                                multi=True)
                    ])
                ]
            ),
            html.Div(
                id='indicators_pie_div',
                style={'width':figsize_px[0]},
                children=[
                    html.Div(
                        style={'height':figsize_px[1]*0.5,'width':figsize_px[0]*0.45},
                        children=[
                            dcc.Graph(id='indicators')
                    ]),
                    html.Div(
                        style={'height':figsize_px[1]*0.5,'width':figsize_px[0]*0.45},
                        children=[
                            dcc.Graph(id='pie_spese')
                    ])
                ]
            ),
            html.Div(
                id='trans_scatter_div',
                style={'height':figsize_px[1]*1.1,'width':figsize_px[0]},
                children=[
                    dcc.Graph(id='trans_scatter'),
                    html.Label(
                        id='scatter-slider-label',
                        children="Use this slider to set the weight for the fitted curve in the picture above"),
                    dcc.Slider(
                        id='frac_slider',
                        min=0,
                        max=1,
                        step=None,
                        value=0.6,
                        marks={i:str(np.round(i,2)) for i in np.arange(0,1.05,0.05)}
                    )
            ]),
            html.Div(
                id='abi_div',
                style={'width':figsize_px[0]},
                children=[
                    daq.BooleanSwitch(id='abi_switch', on=False, label='Causale ABI'),
                    html.Br(),
                    html.Div(
                        id='div_abi',
                        style={'height':figsize_px[1],'width':figsize_px[0]},
                        children=[
                            dcc.Graph(id='bar_abi')
                    ])
                ]
            ),
            html.Div(
                style={'height':figsize_px[1],'width':figsize_px[0]},
                children=[
                    dcc.Graph(id='waterfall_balance')
            ]),
            html.Div(
                id='all_table_div',
                style={'width':figsize_px[0]},
            )
    ])

    global redraw_all, redraw_scatter, hide_abi
    # Callback
    @app.callback(
        Output('indicators', 'figure'),
        Output('pie_spese', 'figure'),
        Output('bar_abi', 'figure'),
        Output('waterfall_balance', 'figure'),
        Output('all_table_div', 'children'),
        Input('date_picker', 'start_date'),
        Input('date_picker', 'end_date'),
        Input('direction_menu', 'value')
    )
    def redraw_all(start_date, end_date, direction):
        df_filtered = df[(df[transform.config.campi['data_contabile']]>=start_date) & (df[transform.config.campi['data_contabile']]<=end_date) & (df['Direzione'].isin(direction))]
        return draw_indicators(df_filtered),\
            draw_pie(df_filtered),\
            draw_abi(df_filtered),\
            draw_water(df_filtered),\
            draw_table(df_filtered[transform.orig_cols])

    @app.callback(
        Output('trans_scatter', 'figure'),
        Input('date_picker', 'start_date'),
        Input('date_picker', 'end_date'),
        Input('direction_menu', 'value'),
        Input('frac_slider', 'value')
    )
    def redraw_scatter(start_date, end_date, direction, frac):
        df_filtered = df[(df[transform.config.campi['data_contabile']]>=start_date) & (df[transform.config.campi['data_contabile']]<=end_date) & (df['Direzione'].isin(direction))]
        return draw_scatter(df_filtered, frac)

    @app.callback(
        Output('div_abi', 'style'),
        Input('abi_switch', 'on')
    )
    def hide_abi(abi_switch):
        if not abi_switch:
            return {'display':'none'}