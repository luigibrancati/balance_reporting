from dash import dcc, html
import transform

def draw(df):
    date_picker = dcc.DatePickerRange(
        id='date_picker',
        start_date=df[transform.config.campi['data_contabile']].min(),
        end_date=df[transform.config.campi['data_contabile']].max(),
        display_format="Do MMM YYYY"
    )
    direction_filter = dcc.Dropdown(
        id='direction_menu',
        options=[{'label':ca, 'value':ca} for ca in sorted(df['Direzione'].unique())],
        value=sorted(list(df['Direzione'].unique())),
        multi=True
    )
    return [html.Div(
        id='dates_div',
        children=[
            html.Label(id='dates_label', children='Date'),
            date_picker
    ]), html.Br(),
    html.Div(
        id='directions_div',
        children=[
            html.Label(id='directions_label', children='Direzione'),
            direction_filter
    ])]