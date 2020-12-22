import sqlalchemy
import pandas as pd
import numpy as np



cities = cost_lib = calc_lib = bus_lib = energy_data = trip_data = None

def changeCity(city):
    global cities, cost_lib, calc_lib, bus_lib, energy_data, trip_data
    
    db_uri = ""
    if city == "Boston":
        db_uri = 'sqlite:///mydb.db'
    elif city == "Milan":
        db_uri = 'sqlite:///mdb.db'
        
    #create connection to database 
    engine = sqlalchemy.create_engine(db_uri)


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
    query = "SELECT * FROM health_result;"
    energy_data = pd.read_sql(query, engine).drop(columns = ["index"])

    #loading trip cluster information from the database 
    query = "SELECT * FROM mbta_route_data;"
    trip_data = pd.read_sql(query, engine)

#generate dynamic checkboxes based on city selected
def generate_control_id(value):
    return 'Control {}'.format(value)

def dynamic_control (city):
    changeCity(city)
    return dict(id = generate_control_id(city), options = [{'label': str(x) , 'value': x} 
                                              for x in list(cities.loc[cities['City']== city, "route_id"] )])

def graph_plot( bus_cost, utility, fuel_price, dc_efficiency, demand_charge, bus_type):
    
    #estimating number of chargers 
    num_chargers  = np.ceil((energy_data["energy_"+ bus_type]/7)/(calc_lib["charge_power_dc"].values[0]* bus_lib[bus_lib.type == bus_type]["charging_time"].values[0]*dc_efficiency))
    
    #capital costs
    capital_cost_e = (bus_cost+cost_lib["batt_cost20"].values[0]* bus_lib[bus_lib.type == bus_type]["battery_size"].values[0]) *  energy_data.num_buses + num_chargers*(cost_lib["charger_costs"][0]+cost_lib["instal_costs"][0])
    capital_cost_d = cost_lib["diesel_bus_cost"][0] * energy_data.num_buses 
    
    #Vehicle maintainance costs 
    vmaint_cost_e = cost_lib["vehicle_main_e"][0]* energy_data.VKT * 0.621371 #coverting km to miles 
    vmaint_cost_d = cost_lib["vehicle_ main_d"][0]* energy_data.VKT * 0.621371
    
    #charging costs 
    fuel_costs_e = (((energy_data["energy_" + bus_type]*4.35*utility)/dc_efficiency ) + (num_chargers*calc_lib["charge_power_dc"][0]* demand_charge)*12)
    fuel_costs_d = fuel_price * (energy_data.VKT * 0.621371 /energy_data["fuel_economy"])*52
    
    #infrastructure operations and maintainance cost 
    infra_onm_e = cost_lib["charging _onm"][0] * num_chargers + cost_lib["batt_cost27"].values[0]* bus_lib[bus_lib.type == bus_type]["battery_size"].values[0]*  energy_data.num_buses
    infra_onm_d = cost_lib["fuel_infra_costs"][0] * (energy_data.VKT * 0.621371 /energy_data["fuel_economy"])*52

    cities["TCO per route - D"]  =  np.ceil((capital_cost_d/calc_lib["annuity_factor"].values[0])+vmaint_cost_d+fuel_costs_d+infra_onm_d )
    cities["TCO per route - E"]  = np.ceil((capital_cost_e/calc_lib["annuity_factor"].values[0])+vmaint_cost_e+fuel_costs_e+infra_onm_e)
    cities["No of buses"] = energy_data.num_buses
    cities["Emissions -E"] = np.ceil(energy_data["e_emi"+bus_type])
    cities["Emissions -D"] = np.ceil(energy_data.d_emi)
    cities["Health impact -D"] =  np.ceil(energy_data.e_impact)
    cities["Level of Service -E"] = energy_data[bus_type + "_LOS"]
    cities["Level of Service -D"] = energy_data["diesel_LOS"]
    cities["Health impact -E"]= [0] * energy_data.shape[0] 
    
    return (cities.to_dict('records'))