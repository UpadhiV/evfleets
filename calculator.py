import sqlalchemy
import pandas as pd

db_uri = 'mysql+mysqlconnector://root:vibhor@localhost:3306/mydb'


#create connection to database 
engine = sqlalchemy.create_engine(db_uri, pool_size=25, max_overflow=10, pool_timeout=60,pool_recycle=3600)


#Import cities data
query = "SELECT * FROM cities ;"
cities = pd.read_sql(query, engine)
cities.head()

#load cost library 
query = "SELECT * FROM cost_library;"
cost_lib = pd.read_sql(query, engine)

#load calculator library 
query = "SELECT * FROM calc_library;"
calc_lib = pd.read_sql(query, engine)

#load bus library 
query = "SELECT * FROM bus_library;"
bus_lib = pd.read_sql(query, engine)

#load route data 
query = "SELECT * FROM mbta_e_data;"
energy_data = pd.read_sql(query, engine)

#loading trip cluster information from the database 
query = "SELECT * FROM mbta_route_data;"
trip_data = pd.read_sql(query, engine)

#layout for the user input form 
city = [{'label': i,"value": i } for i in cities.City.unique()]
bustype = [{'label':'30 Feet','value':'30ft'},{'label':'40 Feet','value':'40ft'},{'label':'60 Feet','value':'60ft'}]


#generate dynamic checkboxes based on city selected
def generate_control_id(value):
    return 'Control {}'.format(value)

def dynamic_control (city):
    return dict(id = generate_control_id(city), options = [{'label': str(x) , 'value': x} 
                                              for x in list(cities.loc[cities['City']== city, "route_id"] )])

def graph_plot( bus_cost, utility, fuel_price, dc_efficiency, l2_efficiency, demand_charge):
    #capital costs
    capital_cost_e = bus_cost *  energy_data.num_buses #+ calc_lib["num_chargers"][0]*(cost_lib["charger_costs"][0]+cost_lib["instal_costs"][0])
    capital_cost_d = cost_lib["diesel_bus_cost"][0] * energy_data.num_buses 
    #operating costs 
    vehicle_maint_cost_e = cost_lib["vehicle_main_e"][0]* energy_data.route_length * 0.000621371
    vehicle_maint_cost_d = cost_lib["vehicle_ main_d"][0]* energy_data.route_length * 0.000621371
    #charging costs 
    fuel_costs_e = (((energy_data["MBTA_energy_30ft"]*energy_data.route_length)/dc_efficiency )*4.35*utility + (calc_lib["num_chargers"][0]*calc_lib["charge_power_dc"][0]* demand_charge)*12)
    fuel_costs_d = fuel_price * (energy_data["route_length"] /energy_data["fuel_economy"])
    #bus["powertrain" == "electric"]["replace_cost"] = ev_lib["Battery_size"]*ev_lib["battery_replace_cost"]*ev_lib["num_buses"]
    #infra_onm_e = cost_lib["charging _onm"][0] * cost_lib["num_chargers"][0]
    infra_onm_d = cost_lib["fuel_infra_costs"][0] * (energy_data["route_length"] /energy_data["fuel_economy"])

    cities["TCO per route - D"]  = capital_cost_d+vehicle_maint_cost_d+fuel_costs_d+infra_onm_d 
    cities["TCO per route - E"]  = capital_cost_e+vehicle_maint_cost_e+fuel_costs_e#+infra_onm_e
    cities["No of buses per route"] = energy_data.num_buses
    cities["Emissions -D"] = energy_data.MBTA_d_emi
#     cities_columns = ["Route","No of buses per route","TCO per route - D", "Level of Serice -D","Emissions -D" ,
#                       "Health impact-D", "TCO per route - E", "Level of Serice -E","Emissions -E" ,"Health impact -E"]
    
#     graph = analysis(Transit, bus_cost, utility, fuel_price,dc_efficiency,l2_efficiency, demand_charge)
    
    return cities.to_dict('records')