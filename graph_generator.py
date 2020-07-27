import plotly.graph_objs as go
import constants as const
import helper_functions as hf


# Tracers
def generate_daily_bar_graph(location_list):
    '''Return tracers for daily bar graphs based on location'''
    tracer_list = []

    for location, color, name in zip(location_list, const.GENERAL_COLORS, const.CAMPUS_NAMES):
        tracer_list.append(
            (
                go.Bar(
                    x=location['dates'],
                    y=location['cases'],
                    name=name, marker_color=color)
            )
        )

    return tracer_list


def generate_total_scatter(selection, location_list, prediction_list):
    '''Return tracers for total scatter graphs based on location'''
    try:
        tracer_list = []
        if selection == 'actual':
            for location, color, name in zip(location_list, const.GENERAL_COLORS, const.CAMPUS_NAMES):
                location['cases'] = location['cases'].cumsum()
                tracer_list.append(go.Scatter(
                    x=location['dates'],
                    y=location['cases'],
                    name=name, mode='lines', line=dict(color=color, width=4)))
        elif selection == 'prediction':
            for location, color, name, col_name in zip(prediction_list, const.GENERAL_COLORS, const.CAMPUS_NAMES,
                                                       const.PREDICTION_COL_NAMES):
                tracer_list.append(go.Scatter(
                    x=location['DS'],
                    y=location[col_name],
                    name=name, mode='lines', line=dict(color=color, width=4)))

        return tracer_list
    except Exception as e:
        print(e)


def generate_employee_student_total_graph(occupation_list):
    '''Return tracers for total scatter graph based on occupation'''
    tracer_list = []
    for occupation, color, name in zip(occupation_list, const.OCCUPATION_COLORS, const.OCCUPATION_NAMES):
        occupation['cases'] = occupation['cases'].cumsum()
        tracer_list.append(go.Scatter(
            x=occupation['dates'],
            y=occupation['cases'],
            name=name, mode='lines', line=dict(color=color, width=4)))

    return tracer_list


def generate_employee_student_daily_graph(occupation_list):
    '''Return tracers for daily bar graph based on occupation'''
    tracer_list = []
    for occupation, color, name in zip(occupation_list, const.OCCUPATION_COLORS, const.OCCUPATION_NAMES):
        tracer_list.append(go.Bar(
            x=occupation['dates'],
            y=occupation['cases'],
            name=name, marker_color=color))

    return tracer_list


def generate_box_plot(occupation_list):
    '''Return tracer for box plot based on occupation'''
    tracer_list = []
    for occupation, color, name in zip(occupation_list, const.OCCUPATION_COLORS, const.OCCUPATION_NAMES):
        tracer_list.append(go.Box(
            y=occupation['cases'],
            name=name,
            boxpoints='all',
            boxmean=True,
            marker_color=color)
        ),

    return tracer_list


def generate_pie_plot(occupation_list):
    '''Return tracer for pie chart based on occupation'''
    values = []
    for occupation in occupation_list:
        values.append(occupation['cases'].sum())
    return [
        go.Pie(
            labels=const.OCCUPATION_NAMES,
            values=values,
            hole=0.3,
            marker=dict(
                colors=const.OCCUPATION_COLORS)
        )
    ]


def generate_prediction_scatter(df):
    return [
        go.Scatter(
            x=df['DS'],
            y=df['YHAT'],
            name='Tampa',
            mode='lines',
            line=dict(color=const.COLORS.DARK_GREEN, width=4))
    ]


# Layouts
def general_graph_layout(title):
    '''Returns a general layout for a graph'''
    return dict(title=dict(
        text=title,
        font=dict(
            size=22, color=const.COLORS.DARK_GREEN
        ),
    ),
        dragmode=False,
        legend=dict(bgcolor=const.COLORS.LIGHT_GREY, font=dict(size=14)),
        xaxis=dict(tickfont=dict(size=16), ),
        yaxis=dict(tickfont=dict(size=16),
                   title=dict(text='Number of Cases', font=dict(size=16))),
    )


def generate_bar_layout(title, barmode):
    '''Returns a layout for a bar graph with the barmode dependent on the input'''
    layout = dict(title=dict(
        text=title,
        font=dict(
            size=22,
            color=const.COLORS.DARK_GREEN
        ),
    ),
        dragmode=False,
        barmode=barmode,
        legend=dict(bgcolor=const.COLORS.LIGHT_GREY, font=dict(size=14)),
        xaxis=dict(tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=16),
                   title=dict(text='Number of Cases', font=dict(size=16))),
    )

    hf.add_range_selector(layout, default='1m')
    return layout
