import dash
from dash import dcc , Dash, html , Input, Output , State
import dash_bootstrap_components as dbc
from dash import dcc
import pandas as pd
import plotly.tools as tls
import sqlite3
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px


conn = sqlite3.connect('tonekabon.db')

plans_df = pd.read_sql_query("SELECT * from plans", conn)
pop_df = pd.read_sql_query("SELECT * from population", conn)
data = pd.read_sql_query("SELECT * from data", conn)

jdate_range = ['1402-1-1','1402-12-29']

#start_date = datetime.date(1400, 1, 1) # replace with actual start date
parents = pop_df["Parent"].unique().tolist()
homes = pop_df["Name"].unique().tolist()
units = plans_df["Unit"].unique().tolist()
groups = plans_df["AgeGroup"].unique().tolist()
plans = plans_df["Plan"].unique().tolist()
# create a Dash application
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])

server = app.server


# define the options for your dropdowns
year_options = ["1400","1401",'1402','1403','1404','1405']
month_options = ['01','02','03','04','05','06','07','08','09','10','11','12']
day_options = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']

global fig ,ax
fig , ax = plt.subplots()
global fig_n
fig_n = 1


# define the layout of your application
app.layout = html.Div([
    # Title
    html.Div([
        # add a title with your desired text
        html.H1('پنل مدیریتی شاخص های بهداشتی')
    ], className='row'),

    # Show Option
    html.Div([
        # create a Bootstrap container
        dbc.Container(
            children=[
                # create a row inside the container
                dbc.Row([
                    # add 5 dropdowns beside each other
                    dbc.Col(dbc.Select(options=parents, id='center_drop')),
                    dbc.Col(dbc.Select(options=homes, id='home_drop')),
                    dbc.Col(dbc.Select(options=units, id='units_drop')),
                    dbc.Col(dbc.Select(options=plans, id='plans_drop')),
                    dbc.Col(dbc.Select(options=groups, id='groups_drop')),
                ], className='pb-3'),

                dbc.Row([
                    # create the "از تاریخ" label
                    dbc.Col(html.Label('بازه زمانی', className='pb-3')),
                    dbc.Col(dcc.DatePickerRange(
                            id='daterangepicker',
                            month_format='Y-M-D',
                            end_date_placeholder_text='Y-M-D',
                            min_date_allowed=jdate_range[0],
                            with_portal=True,
                            max_date_allowed=jdate_range[-1],
                            start_date=jdate_range[0],
                            end_date=jdate_range[-1],
                            display_format='Y-M-D',
                            persistence=True,
                            is_RTL=True,
                            persistence_type='session',
                        )),
                    dbc.Col(dbc.Button(["اضافه کردن نمودار"], id="btn-show" ,color="primary")),
                    dbc.Col(dbc.Button(["پاک کردن نمودار"], id="btn-clear" ,color="primary"))
                ], className='pb-3')
            ],
            fluid=True
        )
    ], className='row'),

    # Insert Option
    html.Div([
        # create a Bootstrap container
        dbc.Container(
            children=[
                # create a row inside the container
                dbc.Row([
                    # create the "از تاریخ" label
                    dbc.Col(html.Label('در تاریخ', className='pb-3')),
                    # add 3 dropdowns for day, month and year of start date
                    dbc.Col(dcc.DatePickerSingle(
                        id = "datepicker",
                        month_format='Y-M-D',
                        placeholder='Y-M-D',
                        display_format='Y-M-D',
                        date=jdate_range[-1],
                        with_portal=True,
                        is_RTL=True
                        )),
                    # add a slash separator between the dropdowns
                    dbc.Col(html.Label('تعداد', className='pb-3')),
                    dbc.Col(dcc.Input(id="insert_value",type='number',placeholder='نفر')),
                    dbc.Col(html.Label('مراقبت', className='pb-3')),
                    dbc.Col(dbc.Button(["ثبت اطلاعات"], id="btn-save" ,color="primary"))
                ], className='pb-3')
            ],
            fluid=True
        )
    ], className='row'),

    # Chart
    html.Div([
        html.H1('نمودار'),
        html.Div(
            dcc.Graph(
                id='my-chart',
            )
        )
    ]),

    dcc.ConfirmDialog(
        id='confirm',
        message='اطلاعات ذخیره گردید',
    ),

] , dir='rtl')


# callbacks

@app.callback(
    Output('home_drop', 'options'),
    Input('center_drop', 'value'))

def update_home_dropdown(value):
    dff = pop_df[pop_df['Parent'] == value]
    homes = dff['Name'].unique()
    return homes

@app.callback(
    Output('plans_drop', 'options'),
    Input('units_drop', 'value'))

def update_plan_dropdown(value):
    dff = plans_df[plans_df['Unit'] == value]
    plans = dff['Plan'].unique()
    return plans

@app.callback(
    Output('groups_drop', 'options'),
    Input('plans_drop', 'value'))

def update_group_dropdown(value):
    dff = plans_df[plans_df['Plan'] == value]
    groups = dff['AgeGroup'].unique()
    return groups

@app.callback(
    Output('confirm', 'displayed'),
    [Input('btn-save', 'n_clicks')],
    [State('center_drop', 'value'),
     State('home_drop', 'value'),
     State('units_drop', 'value'),
     State('plans_drop', 'value'),
     State('groups_drop', 'value'),
     State('insert_value', 'value'),
     State('datepicker', 'date')],
    prevent_initial_call=True
)
def save_data_to_db(n_clicks, center , home , unit, plan, group, value , date ):
    # Create a cursor object to execute SQL queries
    conn = sqlite3.connect('tonekabon.db')

    year_str, month_str, day_str = date.split('-')
    # Convert string values to integers
    """year = int(year_str)
    month = int(month_str)
    day = int(day_str)"""
    date = year_str + month_str + day_str

    cursor = conn.cursor()

    # Execute the SQL query to insert the new data into the table
    cursor.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? )",
                   ("تنکابن", center, home, unit, plan, group, value, 10, date))
    # Commit the changes to the database
    conn.commit()

    # Close the cursor
    cursor.close()

    return True

@app.callback(
    Output('my-chart', 'figure'),
    [Input('btn-show', 'n_clicks')],
    [State('center_drop', 'value'),
     State('home_drop', 'value'),
     State('units_drop', 'value'),
     State('plans_drop', 'value'),
     State('groups_drop', 'value'),
     State('daterangepicker', 'start_date'),
     State('daterangepicker', 'end_date')],
     prevent_initial_call=True
)
def show_chart(n_clicks, center , home , unit, plan, group, start , end ):

    # Create a cursor object to execute SQL queries
    conn = sqlite3.connect('tonekabon.db')
    df = pd.read_sql_query("SELECT * from data", conn)

    year_str, month_str, day_str = start.split('-')
    # Convert string values to integers
    """start_year = int(year_str)
    start_month = int(month_str)
    start_day = int(day_str)"""

    start = year_str +  month_str + day_str
    start = int(start)
    year_str, month_str, day_str = end.split('-')
    # Convert string values to integers
    """end_year = int(year_str)
    end_month = int(month_str)
    end_day = int(day_str)"""

    end = year_str + month_str + day_str
    end = int(end)

    df['I-Date'] = df['Date'].astype('int')

    dff = df[(df['I-Date'] >= start) & (df['I-Date'] <= end)]


    dff = dff[dff["Center"] == center]
    dff = dff[dff["Home"] == home]
    dff = dff[dff["Unit"] == unit]
    dff = dff[dff["Plan"] == plan]
    dff = dff[dff["AgeGroup"] == group]

    print(dff)


    #dff = dff[(dff['Year'] >= from_year) & (dff['Year'] <= to_year)]
    fig = px.line(dff, x='Date', y='Progress', title='شاخص')
    fig.update_layout(
        xaxis=dict(
            tickformat='%Y-%m-%d'
        )
    )
    """global fig, ax
    global fig_n
    if fig_n == 1:
        ax.plot(dff['Date'], dff['Progress'])
    else:
        fig.add_subplot(fig_n, 1, fig_n)
        plt.plot(dff['Date'],dff['Progress'])

    fig_n += 1
    # Convert the Matplotlib chart to a Plotly figure
    plotly_fig = tls.mpl_to_plotly(fig)"""

    return fig

# run the application
if __name__ == '__main__':
    app.run_server(debug=True)
