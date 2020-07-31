import ast
from datetime import datetime, timedelta
import pandas as pd
import dash_html_components as html
import re
from dateutil import relativedelta
import constants as const
from fbprophet import Prophet

def get_percent(df, days=14):
    '''Returns percentage of increase in cases in the specified number of days'''
    last_ten_days = df.groupby('dates', sort=False, as_index=False).sum()
    last_ten_days['cases'] = last_ten_days['cases'].cumsum()
    last_ten_days = last_ten_days.tail(days + 1)
    while True:
        day_limit = datetime.strftime(datetime.today() - timedelta(days=days), '%Y-%m-%d')
        if not last_ten_days[last_ten_days['dates'] == day_limit].empty:
            last_value = int(last_ten_days[last_ten_days['dates'] == day_limit]['cases'])
            break
        days += 1

    most_recent = int(last_ten_days['cases'].iloc[-1])
    result = ((most_recent - last_value) / last_value)
    status = 'increase'
    if result < 0:
        status = 'decrease'
        result *= -1

    return result, status, most_recent, last_value


def get_daily_average(df):
    '''Returns daily average for each occupation'''
    tmp = df.groupby('occupations').mean()
    return tmp['cases'][0], tmp['cases'][1]


def create_avg_string(employee_avg, student_avg, campus):
    '''Returns a string that specifies the daily cases -> students vs employees'''
    avg_ratio = student_avg / employee_avg
    return f'On average per day, {avg_ratio:.2} times the number of students have tested positive compared to USF {campus} employees.' if avg_ratio != 1 else f'On average per day, the same number of students have tested positive compared to USF {campus} employees.'


def string_to_df(string):
    '''Converts a strign int o a data frame.'''
    if isinstance(string, str):
        return pd.DataFrame(ast.literal_eval(string))


def get_df_by_location(df, locations=('Tampa', 'St. Pete', 'Health')):
    '''Divides a data frame containing multiple locations into separate data frames based on location.'''
    dfs = []
    for location in locations:
        dfs.append(df[df['locations'] == location])

    return dfs


def get_df_by_occupation(df, occupations=('Student', 'Employee')):
    '''Divides a data frame containing multiple occupations into separate data frames based on occupation.'''
    dfs = []
    for occupation in occupations:
        dfs.append(df[df['occupations'] == occupation])
    return dfs


def get_total_cases_by_location(dfs_by_location):
    '''Returns a list of total cases for each location data frame.'''
    total_cases = []
    for df in dfs_by_location:
        total_cases.append(df['cases'].sum())

    return total_cases


def get_prediction_by_location(prediction_df):
    '''Returns a list of prediction data frames based on locations.'''
    dfs = []
    prediction_df = prediction_df.reset_index()
    for col_name in const.PREDICTION_COL_NAMES:
        dfs.append(prediction_df[['DS', col_name]])
    return dfs


def get_daily_cases_by_location(dfs_by_location):
    '''Returns a list of daily-case data frames for each location'''
    daily_cases = []
    for df in dfs_by_location:
        daily_cases.append(df.groupby('dates', sort=False, as_index=False).sum())
    return daily_cases


def create_daily_cases_str(daily_cases_df):
    '''Returns a formatted string for a specific daily-case data frame'''
    return str(daily_cases_df['cases'].iloc[-1]) + str(
        ' cases (' if daily_cases_df['cases'].iloc[-1] > 1 else ' case (') + str(
        daily_cases_df['dates'].iloc[-1]) + ")"


def generate_data_table(df):
    '''Generates a table with all COVID19 data'''
    return ([{'name': i, 'id': i} for i in df.columns], df.to_dict('records'))


def generate_collapse(active_tab):
    '''Returns content for the collapse within respective tabs based on the active tab input.'''
    text = [
        html.H5('The plot represents the distribution of Covid-19 cases through their quartiles'),
        html.Ul([
            html.Li(html.H6(
                'The number of cases per day for an occupation is concentrated between the lower(Q1) and upper(Q3) quartiles.')),
            html.Li(html.H6('The mean represents the average number of daily reported cases for the occupation.')),
        ]), ]

    if active_tab == 'Tampa':
        text.append(html.H5('''The data suggests that students on the Tampa Campus have a higher mean and a more distributed box
                                plot. This could be due to a higher probability of students assembling in groups.'''))
    elif active_tab == 'St. Pete':
        pass
    elif active_tab == 'Health':
        text.append(html.H5('''The data suggests that the employees that working for USF Health have a higher mean and more distribution plot. 
                   This could be due to higher probability of exposure to infected pacients'''))
    return text


def get_prediction(df):
    '''Returns a data frame containing a prediction of the # of cases in the specified future period of time'''
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=50)
    forecast = m.predict(future)
    return forecast[['ds', 'yhat']]


def format_dfs_for_prediction(location_list):
    '''Return a list of formated dfs to pass them to the get_prediction fuction.'''
    dfs = []
    for df in location_list:
        df = df.groupby('dates', sort=False, as_index=False).sum()
        df['cases'] = df['cases'].cumsum()
        df['dates'] = df['dates'].apply(lambda date: datetime.strftime(datetime.strptime(date, '%B %d %Y'), '%Y-%m-%d'))

        r = pd.date_range(df.dates.min(), df.dates.max())
        df = df.set_index('dates')
        df.index = pd.DatetimeIndex(df.index)
        df = df.reindex(r).reset_index().fillna(method='ffill')
        df['cases'] = df['cases'].astype(int)
        df = df.rename(columns={'index': 'ds', 'cases': 'y'})
        dfs.append(df)
    return dfs


def add_range_selector(layout, axis_name='xaxis', ranges=None, default=None):
    """Add a rangeselector to the layout if it doesn't already have one.
    :param ranges: which ranges to add, e.g. ['3m', '1y', 'ytd']
    :param default_range: which range to choose as the default, e.g. '3m'

    Based on: https://github.com/danio/plotly_tools
    """
    axis = layout.setdefault(axis_name, dict())
    axis.setdefault('type', 'date')
    if ranges is None:
        # Make some nice defaults
        ranges = ['15d', '1m', 'all']
    re_split = re.compile('(\d+)')

    def range_split(range):
        split = re.split(re_split, range)
        assert len(split) == 3
        return (int(split[1]), split[2])

    # plotly understands m, but not d or y!
    step_map = dict(d='day', m='month', y='year')

    def make_button(range):
        label = None
        if (range == '15d'):
            label = '15 Days'
        elif (range == '1m'):
            label = '1 Month'
        elif (range == 'all'):
            label = 'All'

        if range == 'all':
            return dict(step='all', label=label)
        else:
            (count, step) = range_split(range)
            step = step_map.get(step, step)
            return dict(count=count,
                        label=label,
                        step=step,
                        stepmode='backward')

    axis.setdefault('rangeselector', dict(buttons=[make_button(r) for r in ranges]))
    if default is not None and default != 'all':
        end_date = datetime.today()
        if default.lower() == 'ytd':
            start_date = datetime.date(end_date.year, 1, 1)
        else:
            (count, step) = range_split(default)
            step = step_map[step] + 's'  # relativedelta needs plurals
            start_date = (end_date - relativedelta.relativedelta(**{step: count}))
        axis.setdefault('range', [start_date, end_date])
