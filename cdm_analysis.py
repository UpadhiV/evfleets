#!/usr/bin/env python
# coding: utf-8

# In[45]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from sklearn.linear_model import LinearRegression
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import statsmodels.api as sm
import matplotlib.mlab as mlab
from sklearn.feature_selection import RFECV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import math


# In[46]:


from sklearn import datasets
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import ElasticNet


# In[47]:


#connecting to database server
engine1 = sqlalchemy.create_engine('mysql+mysqlconnector://root:123456@localhost/mydb', pool_size=25, max_overflow=10, pool_timeout=60,pool_recycle=3600) 


# In[48]:


#connecting to database server
engine = sqlalchemy.create_engine('mysql+mysqlconnector://root:123456@localhost/mdb', pool_size=25, max_overflow=10, pool_timeout=60,pool_recycle=3600) 


# Importing simulated data and bus library

# In[49]:


query = "SELECT * FROM bus_library ;"
bus_lib = pd.read_sql(query, engine).drop(columns = "index")
bus_lib


# In[50]:


query = "SELECT * FROM simu_data"
ener = pd.read_sql(query, engine1).drop(columns = "index")
ener = ener.rename(columns={'30_ft': '30ft','40_ft': '40ft','60_ft': '60ft' })
ener


# ## Fitting the polynomial regression model for different bus sizes and predicting energy consumption for different routes 

# In[51]:


#importing mass and auxillary power 
query = "SELECT * FROM cdm_route_data ;"
trip_data = pd.read_sql(query, engine)


# In[52]:


#import real data for Boston 
query = "SELECT * FROM cdm_datafinal ;"
df = pd.read_sql(query, engine)


# In[53]:


#writing the energy consumption equation

def ener_prediction(index):
    #Define constants
    g=9.81 #m/s^2
    bus_wt= bus_lib.loc[bus_lib.index == index,"empt_wt"].values[0] #kg (empty)
    m_pax=70 #kg
    C_rr=0.00697 #(without rain)
    #C_rr=0.00763 #(with rain)
    rho=1.2 #kg/m^3
    A=bus_lib.loc[bus_lib.index == index,"front_area"].values[0] #m^2
    C_d=0.65
    eta_m=0.85
    eta_bat = 0.95
    power= np.empty((0,1))

    riders = [5*x for x in np.arange(0,9,1)]
    masses = [] 
    p_aux = [] 

    #q_heat = 30000 #30kW
    p_auxx = 9000 #9 kW
    h_gain  =1.8 #W
    R_th = 0.0174 #K/W
    T_in = 21 #celcius 
    T_outside = [-20, -10,0, 10]
    C_p = 1.005 #KJ/KG.K
    rho = 1.2
    V_inf = 0
    V_hv = 1.13 #m^3/sec
    psi = 0.20 # 20%
    eta_cop = 2

    for rider in riders:
        masses.append(bus_wt+m_pax*rider)
        for T_out in T_outside:
            p_aux.append(abs((((((T_in-T_out)/R_th) - (rho*C_p*(T_in-T_out)*V_inf ) - (psi*V_hv* rho*C_p*(T_in-T_out)) + (h_gain*rider))/eta_cop)+ p_auxx)/eta_bat))


    #generate a possible sampling distrbution to select data from ????
    grades = np.arange(-0.1,0.1,0.005)
    time  = 0.1 #0.1 sec 
    p_max = bus_lib.loc[bus_lib.index == index,"max_power"].values[0] #90kw
    e_bat = bus_lib.loc[bus_lib.index == index,"battery_size"].values[0] #215 kwh
    data = np.empty((0,3))

    for grade in grades:
        for m_bus in masses: 
            for p_auxi in p_aux:
                data = np.append(data, np.array([[np.sin(grade), m_bus,p_auxi]]), axis=0)

    # Add a bias term to the dataset
    x = sm.add_constant(data)

    # Create polynomial features
    poly_feats = PolynomialFeatures(degree = 6)
    x = poly_feats.fit_transform(x)

    # Split into training and validation set
    x_train, x_val, y_train, y_val = train_test_split(x, ener[bus_lib.iloc[index]["type"]], test_size=0.2, random_state=0)


    # Fit the elastic net regression model
    my_reg = ElasticNet( alpha = 0.001, l1_ratio = 0.8, 
                        max_iter = 1e5).fit(x_train, y_train)

    # Make predictions
    val_preds = my_reg.predict(x_val)
    train_preds = my_reg.predict(x_train)
    val_mse = mean_squared_error(y_val, val_preds)
    train_mse = mean_squared_error(y_train, train_preds)
    print("Train MSE:", train_mse, "\n", "Valid MSE:", val_mse, "\n")
    
    energy = [] 
    for trip in trip_data.trip_id.values:
        data1 = np.empty((0,3))
        for i in range(0, df[df.trip_id ==  trip].shape[0]): 
            route  = trip_data[trip_data.trip_id == trip]["route_id"].values[0]
            data1 = np.append(data1, np.array([[np.sin(df[df.trip_id ==  trip][ "slope"].values[i]), trip_data[trip_data.route_id == route][bus_lib.iloc[index]["type"]+"_wt"].mean(),trip_data[trip_data.route_id == route]["p_ext"].mean()]]), axis =0 )
        # Add a bias term to the dataset
        x1 = sm.add_constant(data1, has_constant='add')
        # Create polynomial features
        poly_feats = PolynomialFeatures(degree = 6)
        x1 = poly_feats.fit_transform(x1)
        p = my_reg.predict(x1)
        energy.append(np.matmul(p,(df[df.trip_id == trip]["dist_m"].values/1000)))
    
    return energy


# In[54]:


for index in bus_lib.index: 
    globals()["CDM_energy_" + bus_lib.iloc[index]["type"]]  = ener_prediction(index)


# In[55]:


trip_data["energy_30ft"]= CDM_energy_30ft
trip_data["energy_40ft"]= CDM_energy_40ft
trip_data["energy_60ft"]= CDM_energy_60ft 


# In[56]:


#looking at tripwise energy consumption 
trip_data.drop(columns = ["level_0", "index"])


# Looking at the aggregated energy consumption for various routes 

# In[57]:


#importing the route data from the database 
query = "SELECT * FROM cdm_e_data ;"
route_data = pd.read_sql(query, engine)
route_data


# In[58]:


#estimating total energy consumed by different buses types on each route 
for route in route_data.route_id:
    ab = trip_data[trip_data.route_id == route]
    route_data.loc[route_data.route_id == route, "energy_30ft"] = (ab["trip_count"] * ab["energy_30ft"]).sum()
    route_data.loc[route_data.route_id == route, "energy_40ft"] = (ab["trip_count"] * ab["energy_40ft"]).sum()
    route_data.loc[route_data.route_id == route, "energy_60ft"] = (ab["trip_count"] * ab["energy_60ft"]).sum()

#storing estiamted data in database 
route_data.to_sql('cdm_e_data', con=engine, if_exists = 'replace')


# In[59]:


#Final energy consumption 
route_data


# ## Estimating level of service for electric buses 

# In[60]:


query = "SELECT * FROM bus_library ;"
bus_lib = pd.read_sql(query, engine)


# In[61]:


#for each route comparing energy required per night per bus 

for bus_type in bus_lib.type:
    for i in route_data.index:
        if (route_data["energy_" + bus_type].iloc[i]/(7*route_data.num_buses.iloc[i]))< bus_lib[bus_lib.type == bus_type]["battery_size"].values[0]:
            route_data.loc[route_data.index == i, bus_type + "_LOS"] = "no"
        else:
            route_data.loc[route_data.index == i, bus_type + "_LOS"] = "yes"


# In[62]:


route_data


# In[63]:


#storing estiamted data in database 
route_data.to_sql('cdm_e_data', con=engine, if_exists = 'replace')


# In[64]:


#importing mass and auxillary power 
query = "SELECT * FROM cdm_e_data ;"
route_data = pd.read_sql(query, engine)


# In[65]:


#calculating energy efficiency for 40-foot bus 
route_data["energy_eff"] = route_data["energy_40ft"]/route_data["VKT"]

#creating a figure
fig = plt.figure(figsize = (10, 6)) 
  
# creating the bar plot 
plt.bar(route_data.route_id, route_data.energy_eff, color ='blue',  
        width = 0.4) 
plt.xlabel("Routes", fontsize = 18) 
plt.yticks(fontsize=14)
plt.xticks(fontsize=14)
plt.ylabel("Average energy efficiency(kWh/km)", fontsize = 18) 
plt.title("Comparing energy efficiencies of 40-foot electric buses in Milan", fontsize = 18) 
plt.savefig("Milan_energy_eff")
plt.show()


# In[ ]:





# In[66]:


#importing the route data from the database 
query = "SELECT * FROM cdm_e_data ;"
route_data = pd.read_sql(query, engine).drop(columns = ["level_0", "index"])
route_data

