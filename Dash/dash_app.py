import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import transform
import dash_daq as daq
import graphics
import filters


app = dash.Dash(__name__, suppress_callback_exceptions=True)


@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    if selected_columns:
        return [{
            'if': { 'column_id': i },
            'background_color': '#D2F3FF'
        } for i in selected_columns]


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
def redraw_all_graphics(start_date, end_date, direction):
    df_filtered = df[(df[transform.config.campi['data_contabile']]>=start_date) & (df[transform.config.campi['data_contabile']]<=end_date) & (df['Direzione'].isin(direction))]
    return graphics.draw_indicators(df_filtered),\
        graphics.draw_pie(df_filtered),\
        graphics.draw_abi(df_filtered),\
        graphics.draw_water(df_filtered),\
        graphics.draw_table(df_filtered[transform.orig_cols])


@app.callback(
    Output('trans_scatter', 'figure'),
    Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date'),
    Input('direction_menu', 'value'),
    Input('frac_slider', 'value')
)
def redraw_scatter(start_date, end_date, direction, frac):
    df_filtered = df[(df[transform.config.campi['data_contabile']]>=start_date)
                      & (df[transform.config.campi['data_contabile']]<=end_date)
                      & (df['Direzione'].isin(direction))]
    return graphics.draw_scatter(df_filtered, frac)


@app.callback(
    Output('div_abi', 'style'),
    Input('abi_switch', 'on')
)
def hide_abi(abi_switch):
    if not abi_switch:
        return {'display':'none'}


def create_app(data_folder):
    transform.set_config(data_folder)
    global df
    df = transform.preprocess_df(transform.import_df())
    # Layout
    app.layout = html.Div(
        children=[
            html.Div(
                id='filters_div',
                style={'width': graphics.figsize_px[0]},
                children=filters.draw(df)
            ),
            html.Div(
                id='indicators_pie_div',
                style={'width': graphics.figsize_px[0]},
                children=[
                    html.Div(
                        style={'height': graphics.figsize_px[1]*0.5,'width': graphics.figsize_px[0]*0.45},
                        children=[
                            dcc.Graph(id='indicators')
                    ]),
                    html.Div(
                        style={'height': graphics.figsize_px[1]*0.5,'width': graphics.figsize_px[0]*0.45},
                        children=[
                            dcc.Graph(id='pie_spese')
                    ])
                ]
            ),
            html.Div(
                id='trans_scatter_div',
                style={'height': graphics.figsize_px[1]*1.1,'width': graphics.figsize_px[0]},
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
                style={'width': graphics.figsize_px[0]},
                children=[
                    daq.BooleanSwitch(id='abi_switch', on=False, label='Causale ABI'),
                    html.Br(),
                    html.Div(
                        id='div_abi',
                        style={'height': graphics.figsize_px[1],'width': graphics.figsize_px[0]},
                        children=[
                            dcc.Graph(id='bar_abi')
                    ])
                ]
            ),
            html.Div(
                style={'height': graphics.figsize_px[1],'width': graphics.figsize_px[0]},
                children=[
                    dcc.Graph(id='waterfall_balance')
            ]),
            html.Div(
                id='all_table_div',
                style={'width': graphics.figsize_px[0]},
            )
    ])
