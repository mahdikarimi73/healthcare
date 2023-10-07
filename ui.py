import dash
from dash import dcc , html , Dash, html , Input, Output , State
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc
import pandas as pd
import sqlite3
import arrow
from dateutil.relativedelta import relativedelta


conn = sqlite3.connect('tonekabon.db')

plans_df = pd.read_sql_query("SELECT * from plans", conn)
pop_df = pd.read_sql_query("SELECT * from population", conn)
data = pd.read_sql_query("SELECT * from data", conn)


#start_date = datetime.date(1400, 1, 1) # replace with actual start date
parents = pop_df["Parent"].unique().tolist()
homes = pop_df["Name"].unique().tolist()
units = plans_df["Unit"].unique().tolist()
groups = plans_df["AgeGroup"].unique().tolist()
plans = plans_df["Plan"].unique().tolist()
# create a Dash application
app =   dash.Dash(external_stylesheets=[dbc.themes.SOLAR])
server = app.server

# define the options for your dropdowns
year_options = ["1400","1401",'1402','1403','1404','1405']
month_options = ['01','02','03','04','05','06','07','08','09','10','11','12']
day_options = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']



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
                    dbc.Col(html.Label('از تاریخ', className='pb-3')),

                    # add 3 dropdowns for day, month and year of start date
                    dbc.Col(dbc.Select(options=day_options , id = "from_day"), className='pb-3'),

                    # add a slash separator between the dropdowns
                    dbc.Col('/', className='pb-3'),
                    dbc.Col(dbc.Select(options=month_options , id = "from_month"), className='pb-3'),
                    dbc.Col('/', className='pb-3'),
                    dbc.Col(dbc.Select(options=year_options, id = "from_year"), className='pb-3'),

                    # add the "تا تاریخ" label
                    dbc.Col(html.Label('تا تاریخ', className='pb-3')),

                    # add 3 dropdowns for day, month and year of end date
                    dbc.Col(dbc.Select(options=day_options, id = "to_day")),
                    dbc.Col('/', className='pb-3'),
                    dbc.Col(dbc.Select(options=month_options, id = "to_month")),
                    dbc.Col('/', className='pb-3'),
                    dbc.Col(dbc.Select(options=year_options, id = "to_year")),

                    # add a "نمایش جدول" button
                    dbc.Col(dbc.Button(["نمایش نمودار"], id="btn-show",color="primary"))
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
                    dbc.Col(dbc.Select(options=day_options, id="insert_day"), className='pb-3'),
                    # add a slash separator between the dropdowns
                    dbc.Col('/', className='pb-3'),
                    dbc.Col(dbc.Select(options=month_options, id="insert_month"), className='pb-3'),
                    dbc.Col('/', className='pb-3'),
                    dbc.Col(dbc.Select(options=year_options, id="insert_year"), className='pb-3'),
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
    )

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
     State('insert_year', 'value'),
     State('insert_month', 'value'),
     State('insert_day', 'value'),
     State("insert_value", 'value')],
    prevent_initial_call=True
)
def save_data_to_db(n_clicks, center , home , unit, plan, group, year, month , day, value ):
    # Create a cursor object to execute SQL queries
    conn = sqlite3.connect('tonekabon.db')

    cursor = conn.cursor()

    # Execute the SQL query to insert the new data into the table
    cursor.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   ("تنکابن", center, home, unit, plan, group, value, 10, year, month, day))
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
     State('from_year', 'value'),
     State('from_month', 'value'),
     State('from_day', 'value'),
     State('to_year', 'value'),
     State('to_month', 'value'),
     State('to_day', 'value')],
    prevent_initial_call=True
)
def show_chart(n_clicks, center , home , unit, plan, group, from_year, from_month , from_day , to_year, to_month , to_day ):

    start_date = arrow.get(from_year,from_month, from_day)
    end_date = arrow.get(to_year,to_month,to_day)
    # Create a cursor object to execute SQL queries
    conn = sqlite3.connect('tonekabon.db')
    df = pd.read_sql_query("SELECT * from data", conn)
    date_strings = df.apply(lambda row: f"{row['Year']}-{row['Month']}-{row['Day']}", axis=1)
    dates = [arrow.get(date_str, 'YYYY-MM-DD') for date_str in date_strings]

    dff = df[df["Center"] == center]
    dff = dff[dff["Home"] == home]
    dff = dff[dff["Unit"] == unit]
    dff = dff[dff["Plan"] == plan]
    dff = dff[dff["AgeGroup"] == group]
    dff['date'] = dates
    dff = dff[(dff['date'] >= start_date) & (dff['date'] <= end_date)]

    #dff = dff[(dff['Year'] >= from_year) & (dff['Year'] <= to_year)]
    fig = px.line(dff, x='date', y='Progress', title='شاخص')
    return fig

# run the application
if __name__ == '__main__':
    app.run_server(debug=True)
