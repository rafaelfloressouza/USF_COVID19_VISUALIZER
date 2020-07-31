import dash
import dash_bootstrap_components as dbc
import layouts
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
import data
import graph_generator as gg
from datetime import datetime
import helper_functions as hf
from dash.exceptions import PreventUpdate
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

server = Flask(__name__)

# Initializing the web application.
app = dash.Dash(
    __name__, external_stylesheets=['/assets/stylesheet.css', dbc.themes.FLATLY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1, minimum-scale = 1, maximum-scale=1"}
    ],
    server=server,
    suppress_callback_exceptions=True,
)
app.title = 'USF-COVID19'
app._favicon = '/assets/favicon.ico'

# SQLAlchemy
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://dklnylfkfanqcg:5fc17b0733a2bdc958ff310c0577e2909753574a177ff033d8ee9306a9dff6fc@ec2-3-215-83-17.compute-1.amazonaws.com:5432/dq5q0b3f9djga"
db = SQLAlchemy(app.server)

# Apps layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    layouts.navbar,
    dcc.Store(id='data', data=data.get_data().to_json()),
    html.Div(id='page-content', children=layouts.USF_layout),
    layouts.footer
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def page(pathname):
    try:
        if pathname == '/table-header':
            return layouts.table
        elif pathname == '/home':
            return layouts.USF_layout
        else:
            return layouts.USF_layout
    except:
        raise PreventUpdate


@app.callback(
    [Output('table', 'columns'),
     Output('table', 'data')],
    [Input('data', 'data')]
)
def update_data_table(data):
    df = hf.string_to_df(data)
    data_table = hf.generate_data_table(df)
    return data_table[0], data_table[1]


# Functions and Callbacks
@app.callback(
    [Output("tampa_card_total_cases", 'children'),
     Output('tampa_card_health_total_cases', 'children'),
     Output("st_pete_card_total_cases", 'children'),
     Output('tampa_card_update', 'children'),
     Output('health_tampa_card_update', 'children'),
     Output('st_pete_card_update', 'children')],
    [Input('data', 'data')])
def update_cards(data):
    df = hf.string_to_df(data)

    dfs_by_location = hf.get_df_by_location(df)
    total_cases_tampa, total_cases_st_pete, total_cases_health = hf.get_total_cases_by_location(dfs_by_location)
    daily_cases_tampa, daily_cases_st_pete, daily_cases_tampa_health = hf.get_daily_cases_by_location(
        dfs_by_location)

    return str(total_cases_tampa), \
           str(total_cases_health), \
           str(total_cases_st_pete), \
           hf.create_daily_cases_str(daily_cases_tampa), \
           hf.create_daily_cases_str(daily_cases_tampa_health), \
           hf.create_daily_cases_str(daily_cases_st_pete), \


@app.callback([Output('daily-bar-graph', 'figure'),
               Output('total-scatter-graph', 'figure')],
              [Input('data', 'data'),
               Input('graph_type', 'value')])
def create_general_graphs(data, graph_type):
    df = hf.string_to_df(data)
    prediction_df = pd.read_sql_table('prediction', con=db.engine)
    df['dates'] = df['dates'].apply(lambda date: datetime.strptime(date, "%B %d %Y"))

    location_list = hf.get_daily_cases_by_location(hf.get_df_by_location(df))
    prediction_list = hf.get_prediction_by_location(prediction_df)

    return dict(data=gg.generate_daily_bar_graph(location_list),
                layout=gg.generate_bar_layout('Daily Cases on USF Campuses', 'group')), \
           dict(data=gg.generate_total_scatter(graph_type, location_list, prediction_list),
                layout=gg.general_graph_layout('Total Cases USF Campuses'))


@app.callback([
    Output('employee-student-daily-graph', 'figure'),
    Output('employee-student-box', 'figure'),
    Output('employee-student-pie', 'figure'),
    Output('employee-student-total-graph', 'figure'),
    Output('general-overview', 'children'),
    Output('general-daily-average', 'children'),
    Output('collapse-text', 'children')],
    [Input('data', 'data'),
     Input('general-tabs', 'active_tab')])
def campus_graphs(data, active_tab):
    return tab_content(hf.string_to_df(data), active_tab)


def tab_content(df, active_tab):
    new_df = df[df['locations'] == active_tab]
    new_df['dates'] = new_df['dates'].apply(lambda date: datetime.strptime(date, '%B %d %Y'))
    employee_avg, student_avg = hf.get_daily_average(new_df)
    result, status, most_recent, last_value = hf.get_percent(new_df)

    occupation_list = hf.get_df_by_occupation(new_df)

    return dict(data=gg.generate_employee_student_daily_graph(occupation_list),
                layout=gg.generate_bar_layout(f'Student Vs. Employee Daily Cases (USF {active_tab})', 'stack'), ), \
           dict(data=gg.generate_box_plot(occupation_list),
                layout=gg.general_graph_layout(f'Box Plot For Daily Cases Per Occupation (USF {active_tab})')), \
           dict(data=gg.generate_pie_plot(occupation_list),
                layout=gg.general_graph_layout(f'Total Cases Percentage Per Occupation (USF {active_tab})')), \
           dict(data=gg.generate_employee_student_total_graph(occupation_list),
                layout=gg.general_graph_layout(f'Student Vs. Employee Total Cases (USF {active_tab})')), \
           f'USF {active_tab} has seen a {result:.2%} {status} in cases in the two weeks. The number of cases went from {last_value} to {most_recent}.', \
           hf.create_avg_string(employee_avg, student_avg, active_tab), hf.generate_collapse(active_tab)


# Collapse Elements Callbacks
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True)
