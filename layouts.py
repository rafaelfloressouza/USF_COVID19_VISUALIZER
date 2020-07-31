import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import constants as const
import dash_table

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/home")),
        dbc.NavItem(dbc.NavLink("Data Table", href="/table-header")),
        dbc.NavItem(dbc.NavLink("USF Covid Website", href="https://www.usf.edu/coronavirus/", target='__black',
                                external_link=True, style=dict(hover=const.COLORS.LIGHT_GOLD)))
    ],
    brand="COVID-19 Dashboard for University of South Florida ",
    style=dict(overflowX='hidden', borderBottom='solid 1px white'),
    brand_href="/home",
    color=const.COLORS.LIGHT_GREEN,
    fluid=True,
    dark=True,
    id='navigation',
    expand='lg',
)

# Cards
tampa_card_content = [
    dbc.CardHeader(html.H4("Tampa Campus"),
                   style=dict(color=const.COLORS.DARK_GREEN, background=const.COLORS.LIGHT_GREY)),
    dbc.CardBody(
        [
            html.H4("Total Cases", className="card-title"),
            html.H5(
                "",
                id='tampa_card_total_cases',
                className="card-text",
            ),

            html.H4('Latest Update', className='card-title'),
            html.H5(
                "",
                id='tampa_card_update',
                className="card-text",
            ),
        ]
    ),
]

saint_pete_card_content = [
    dbc.CardHeader(html.H4("St. Petersburg Campus"),
                   style=dict(color=const.COLORS.DARK_GREEN, background=const.COLORS.LIGHT_GREY)),
    dbc.CardBody(
        [
            html.H4("Total Cases", className="card-title"),
            html.H5(
                "",
                id='st_pete_card_total_cases',
                className="card-text",
            ),

            html.H4('Latest Update', className='card-title'),
            html.H5(
                "",
                id='st_pete_card_update',
                className="card-text",
            ),
        ],
    )
]

health_card_content = [
    dbc.CardHeader(html.H4("USF Health"),
                   style=dict(color=const.COLORS.DARK_GREEN, background=const.COLORS.LIGHT_GREY)),
    dbc.CardBody(
        [
            html.H4("Total Cases", className="card-title"),
            html.H5(
                "",
                id='tampa_card_health_total_cases',
                className="card-text",
            ),
            html.H4('Latest Update', className='card-title'),
            html.H5(
                "",
                id='health_tampa_card_update',
                className="card-text",
            ),
        ]
    ),
]

cards = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(tampa_card_content, className='shadow'),
                    className='col-sm'
                ),
                dbc.Col(
                    dbc.Card(saint_pete_card_content, className='shadow'),
                    className='col-sm'
                ),

                dbc.Col(
                    dbc.Card(health_card_content, className='shadow'),
                    className='col-sm'
                ),
            ],
            className="mb-4",
            align='stretch',
            style=dict(marginTop='1rem')
        ),
    ], className='d-flex justify-content-center', id='cards'
)

# Graph Layouts
daily_bar_graph = dcc.Graph(
    id='daily-bar-graph',
    config=dict(doubleClickDelay=1, displaylogo=False, displayModeBar=False, scrollZoom=False),
)

total_scatter_graph = dcc.Graph(
    id='total-scatter-graph',
    config=dict(doubleClickDelay=1, displaylogo=False, displayModeBar=False, scrollZoom=False),
)

predict = dcc.Graph(
    id='predict',
    config=dict(doubleClickDelay=1, displaylogo=False, displayModeBar=False, scrollZoom=False),
)

# Alerts
alert_dialog = html.Div(
    dbc.Alert(
        children="The purpose of this website is only to present COVID-19 data on the USF campuses. We do not take ownership of the data as it was acquired from the USF Coronavirus website.",
        id="alert",
        dismissable=True,
        is_open=True,
        className='shadow'
    )
)

# Collapses
collapse = html.Div(
    [
        dbc.Button(
            "What does this Graph mean?",
            id="collapse-button",
            className="mb-3",
            color="primary",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(
            ), id='collapse-text', style=dict(background=const.COLORS.LIGHT_GREY, padding='1rem')),
            id="collapse", style=dict(textAlign='left')
        ),
    ],
)

# Other Graph Layouts
employee_student_graph = html.Div([
    dcc.Graph(id='employee-student-pie',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    dcc.Graph(id='employee-student-total-graph',
              config=dict(displaylogo=False,
                          displayModeBar=False,
                          scrollZoom=False)),
    dcc.Graph(id='employee-student-daily-graph',
              config=dict(
                  doubleClickDelay=1,
                  displaylogo=False,
                  displayModeBar=False,
                  scrollZoom=False)),
    html.Div(
        [
            dcc.Graph(id='employee-student-box',
                      config=dict(displaylogo=False,
                                  displayModeBar=False,
                                  scrollZoom=False)),
            collapse,
        ], style=dict(textAlign='center')
    ),
])

# Jumbotrons
general_jumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [
                html.H2("Summary", className="display-5", style=dict(color=const.COLORS.DARK_GREEN)),
                html.Hr(className="my-2"),
                html.Br(),
                html.Ul([
                    html.Li(html.H4('', id='general-overview')),
                    html.Li(html.H4('', id='general-daily-average')),
                ]),
            ],
            fluid=True,
        )
    ],
    fluid=True,
    className='shadow'
)

# Tabs
general_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="USF Tampa", tab_id="Tampa"),
                dbc.Tab(label="USF St. Petersburg", tab_id="St. Pete"),
                dbc.Tab(label="USF Health", tab_id="Health"),
                # dbc.Tab(label="USF Sarasota-Manatee", tab_id="sarasota-manatee"),
            ],
            id="general-tabs",
            card=True,
            active_tab="Tampa",
        ),
        dbc.CardBody(
            html.Div([
                general_jumbotron,
                employee_student_graph
            ], className="card-text mt-3")
        ),
    ]
)

# Table Layout
table = html.Div([
    html.H1('Data Table', id='table_header', style=dict(color=const.COLORS.DARK_GREEN, padding='2rem')),
    dash_table.DataTable(
        id='table',
        style_cell=dict(textAlign='center'),
        style_header={'backgroundColor': const.COLORS.LIGHT_GREY, 'fontWeight': 'bold', 'fontSize': '1rem',
                      'color': const.COLORS.DARK_GREEN},
    )
], className='container-fluid w-50', style=dict(textAlign='center'))

# Footer Layout
footer = html.Footer([
    html.H5('Made by'),
    html.Div([
        html.A('Adheesh Shenoy', href='https://www.linkedin.com/in/adheeshenoy/', target='__blank'),
        html.Img(src='/assets/LI-In-Bug.png'),
    ]),
    html.Div([
        html.A('Rafael Flores Souza', href='https://www.linkedin.com/in/rafael-flores-souza/', target='__blank'),
        html.Img(src='/assets/LI-In-Bug.png'),
    ]),
], id='footer', style=dict(borderTop="solid 1px white"))

# WEBSITE LAYOUT ~ Contains all components
USF_layout = html.Div([
    # predict,
    alert_dialog,
    html.Div([
        cards,
    ], className='container-fluid'),
    html.Div([
        html.Div([

            dbc.RadioItems( # Used to select between actual and prediction graphs.
                options=[
                    {"label": "Actual", "value": 'actual'},
                    {"label": "Prediction", "value": 'prediction'},
                ],
                value='actual',
                id="graph_type",
                inline=True,
                style=dict(marginLeft='4rem', marginTop='1rem'),
            ),
            total_scatter_graph,
            daily_bar_graph,
        ])
    ]),
    html.Div([
        general_tabs,
    ], style=dict(background='white')),
])
