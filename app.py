#!/usr/bin/env python
# coding: utf-8

# In[177]:


import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_sqlalchemy import SQLAlchemy 
from  dash.dependencies import Output, Input, State
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_table
import import_ipynb 


# In[178]:


#create a Flask server 
server = flask.Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# In[179]:


#create connection to database 
engine = sqlalchemy.create_engine('mysql+mysqlconnector://root:123456@localhost/mydb', pool_size=25, max_overflow=10, pool_timeout=60,pool_recycle=3600)


# ## Creating a application using Dash
# Dash by plotly is a library for creating dashboard in python. It has a built-in Plotly.js java script module that receives JSON objects from  Plotly python and performs rendering for the browser. The library also contains syntax for HTML and CSS components for creating elements on the webpage. 

# In[180]:


#Create an app as a Dash object 
app = dash.Dash(__name__,
    server=server,
    routes_pathname_prefix='/ebus/',external_stylesheets=external_stylesheets)
app.title = 'Fleet Electrification'


# In[181]:


import dashboard 
#from dashboard import layout 


# In[182]:


#connect to a database 
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
server.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@localhost/mydb'
#db = SQLAlchemy(server)


# Creating a User input form constainting the following inputs 
# 1. City 2. Cost of Bus 3. Utility charges 4. Fuel Price 5. Demand charge 6. DC Charging efficiency 7. L2 Charging efficiency 

# In[183]:


#Import cities data
query = "SELECT * FROM cities ;"
cities = pd.read_sql(query, engine)
cities.head()


# In[184]:


city = {'label': "Boston", "value": "mbta" } 


#load cost library 
query = "SELECT * FROM cost_library;"
cost_lib = pd.read_sql(query, engine)

#load calculator library 
query = "SELECT * FROM calc_library;"
calc_lib = pd.read_sql(query, engine)

#load bus library 
query = "SELECT * FROM bus_library;"
bus_lib = pd.read_sql(query, engine)

#load final data 
query = "SELECT * FROM health_result;"
energy_data = pd.read_sql(query, engine).drop(columns = ["index"])


# In[185]:


energy_data


# In[186]:


cost_lib


# In[187]:


#loading trip cluster information from the database 
query = "SELECT * FROM mbta_route_data;"
trip_data = pd.read_sql(query, engine)


# In[188]:


#layout for the user input form 
city = [{'label': i,"value": i } for i in cities.City.unique()]
bustype = [{'label':'30 Feet','value':'30ft'},{'label':'40 Feet','value':'40ft'},{'label':'60 Feet','value':'60ft'}]
# def page_1():
app.layout = html.Div([ html.Label('Select City'),
                        html.Div(className = " row", 
                    #city dropdown 
                        children  = [ html.Div(
                        dcc.Dropdown(
                            id = 'Transit',
                            options = city, 
                            ), style = {"width": "15%"}
                        ),
                   #route selection 
                    html.Br(),
                    html.Label("Select routes to analyse"),
                    html.Div(
                        id = "route_ids"),            
                  #bus type
                    html.Br(),
                    html.Label("Select bus type"),
                        html.Div(
                        dcc.Dropdown( 
                            id = 'bus_type',
                            options = bustype, 
                            value = ''), style = {"width": "15%"}
                    ),

                #cost of bus 
                    html.Br(),
                    html.Label("Cost of Electric Bus ($)"),
                    
                        dcc.Input( id = 'bus_cost',
                        placeholder = " ",
                        type = 'number',inputMode = "numeric",
                        value = 0 ),
                    ],),
                    
                #Electricity price
                    html.Br(),
                    html.Label(" Utility charges ($/kWh)"),
                            html.Div(
                            dcc.Input( id = 'utility',
                            placeholder = " ",
                            type = 'number',inputMode = "numeric",
                            value = 0), ),
                    #Electricity price
                        html.Br(),
                        html.Label(" Fuel price ($/gallon eq)"),
                            html.Div( dcc.Input(id = 'fuel_price',
                            placeholder = " ",
                            type = 'number',
                            inputMode = "numeric",
                            value = 0),),
                            html.Br(),
                        html.Label(" Demand charge ($/kW-month)"),
                            html.Div( dcc.Input(id = 'demand_charge',
                            placeholder = " ",
                            type = 'number',
                            value = 0),),  
             #DC charging efficiency 
    
                    html.Br(),
                    html.Label(" DC Charging efficiency (%)"),
                    html.Div(className = "row", 
                        children  = [ 
                        html.Div(dcc.Input( id = 'dc_efficiency', placeholder = " value in decimal",
                        type = 'number', value = .92), className = "six columns"),]
                        ),
                    html.Br(),
                       html.Div(id = "tco_graph"),
                       dash_table.DataTable(
                           id='table', 
                           columns=[{"name": i, "id": i} for i in cities.columns],
         #                  data=cities.to_dict('records'),
                           ),                    
                    html.Br(),
#                    html.Button(type='Submit', id='submit-val', n_clicks=0),
                    ],)

#creating callbacks within page if a value is missing 


# In[189]:


#generate dynamic checkboxes based on city selected
def generate_control_id(value):
    return 'Control {}'.format(value)

def dynamic_control (city):
    return dcc.Checklist(id = generate_control_id(city), options = [{'label': '{}'.format(x) , 'value': x} 
                                              for x in list(cities.loc[cities['City']== city, "route_id"] )])

@app.callback(Output('route_ids', 'children'),
              [Input('Transit', 'value')])
def update_routes(city):
    new  = html.Div(dynamic_control(city))

    return new

#app.config.supress_callback_exceptions = True


# Connecting the form (layout) with the relevant URL and performing redirection to a new page 

# Since TCO is an interactive calculator, the following code takes User Inputs from the form and The EV libraray dues the relevant calculations 

# In[190]:




#callback for doing TCO inputs and output graph
@app.callback([Output("table", "data" )],
 #              [Input("Transit", "value"),
               [Input("bus_cost", "value"),
               Input("utility", "value"),
               Input("fuel_price", "value"),
               Input("dc_efficiency", "value"),
               Input("demand_charge", "value"),
#               Input(generate_control_id(value1), "value"),
               Input('bus_type','value')])
def graph_plot( bus_cost, utility, fuel_price,dc_efficiency, demand_charge, bus_type):
    
    #estimating number of chargers 
    num_chargers  = np.ceil((energy_data["energy_"+ bus_type]/7)/(calc_lib["charge_power_dc"].values[0]* bus_lib[bus_lib.type == bus_type]["charging_time"].values[0]*dc_efficiency))
    
    #capital costs
    capital_cost_e = (bus_cost) *  energy_data.num_buses + num_chargers*(cost_lib["charger_costs"][0]+cost_lib["instal_costs"][0])
    capital_cost_d = cost_lib[bus_type+"_cost"][0] * energy_data.num_buses 
    
    #Vehicle maintainance costs 
    vmaint_cost_e = cost_lib["vehicle_main_e"][0]* energy_data.VKT * 0.621371*52 #coverting km to miles 
    vmaint_cost_d = cost_lib["vehicle_ main_d"][0]* energy_data.VKT * 0.621371*52
    
    #charging/fueling costs 
    fuel_costs_e = ((((energy_data["energy_" + bus_type]*4.35*utility)/dc_efficiency )*12*((1+calc_lib["elec_rate"][0])**12 -1)/((1+calc_lib["elec_rate"][0])-1)) + ((num_chargers*calc_lib["charge_power_dc"][0]* demand_charge)*12*(calc_lib["annuity_factor"].values[0]-1)/(calc_lib["discount_rate"].values[0]*calc_lib["annuity_factor"].values[0])))#(11.93422)
    fuel_costs_d = (fuel_price * (energy_data.VKT * 0.621371 /energy_data["fuel_economy"])*52)*(((1+calc_lib["fuel_rate"][0])**12 -1)/((1+calc_lib["fuel_rate"][0])-1))
    
    #infrastructure operations and maintainance cost 
    infra_onm_e = cost_lib["charging _onm"][0] * num_chargers 
    infra_onm_d = cost_lib["fuel_infra_costs"][0] * (energy_data.VKT * 0.621371 /energy_data["fuel_economy"])*52

    #salvage costs 
    sal_e = (bus_cost)* calc_lib["bus_salvage"][0]*energy_data.num_buses +cost_lib["charger_costs"][0]* calc_lib["char_salvage"][0]*num_chargers
    sal_d = cost_lib[bus_type+"_cost"][0]*calc_lib["bus_salvage"][0]*energy_data.num_buses

    Capital_d  = capital_cost_d/1000000
    Capital_e = capital_cost_e/1000000
    vmain_e = (vmaint_cost_e *(calc_lib["annuity_factor"].values[0]-1))/(calc_lib["discount_rate"].values[0]*calc_lib["annuity_factor"].values[0]*1000000)
    fuel_e = (fuel_costs_e/1000000)
    fuel_d = (fuel_costs_d/1000000)
    onm_d =  (infra_onm_d*(calc_lib["annuity_factor"].values[0]-1))/(calc_lib["discount_rate"].values[0]*calc_lib["annuity_factor"].values[0]*1000000)
    vmain_d = (vmaint_cost_d*(calc_lib["annuity_factor"].values[0]-1))/(calc_lib["discount_rate"].values[0]*calc_lib["annuity_factor"].values[0]*1000000)
    onm_e = (infra_onm_e*(calc_lib["annuity_factor"].values[0]-1))/(calc_lib["discount_rate"].values[0]*calc_lib["annuity_factor"].values[0]*1000000)
    sal_e = -sal_e/(calc_lib["annuity_factor"].values[0]*1000000)
    sal_d = -sal_d/(calc_lib["annuity_factor"].values[0]*1000000)
    tco_d = Capital_d+vmain_d+fuel_d+onm_d+sal_d
    tco_e = Capital_e+vmain_e+fuel_e+onm_e+sal_e

    
    cities["TCO per route - D"]  =  np.ceil(tco_d)
    cities["TCO per route - E"]  = np.ceil(tco_e)
    cities["No of buses"] = energy_data.num_buses
    cities["Emissions -E"] = np.ceil(energy_data["e_emi"+bus_type])
    cities["Emissions -D"] = np.ceil(energy_data.d_emi)
    cities["Health impact -D"] =  np.ceil(energy_data.e_impact)
    cities["Level of Service -E"] = energy_data[bus_type + "_LOS"]
    cities["Level of Service -D"] = energy_data["diesel_LOS"]
    cities["Health impact -E"]= [0] * energy_data.shape[0] 
    
    return (cities.to_dict('records'),)




# 

# In[191]:



@app.server.route('/analysis')
def analysis():
#     data = flask.request.form
#     print(data)
#flask.redirect('/analysis')
#    import dashboard
    
    return app.layout


# In[193]:


if __name__ == '__main__':
    app.run_server(port = 5000)


# Creating an app as collection of pages 

# Adding the graphs from energy consumption module to the dashboard.

# TCO Calculation (Example graph) 
# 

# In[ ]:





# In[ ]:




