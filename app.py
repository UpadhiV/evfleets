#!/usr/bin/env python
# coding: utf-8


import flask
from flask import request
from flask_cors import CORS

from calculator import cities, dynamic_control, graph_plot

#create a Flask server 
app = flask.Flask(__name__)
CORS(app)


@app.route('/cities')
def getcities():
    return dict(cities = [{'label': i,"value": i } for i in cities.City.unique()])

@app.route("/routes/<city>")
def update_routes(city):
    return dynamic_control(city)

#callback for doing TCO inputs and output graph
@app.route("/tabledata", methods=["POST"])
def tabledata():
    
    bus_cost = float(request.json["bus_cost"] or 0)
    utility = float(request.json["utility"] or 0)
    fuel_price = float(request.json["fuel_price"] or 0)
    dc_efficiency = float(request.json["dc_efficiency"] or 0.92)
    l2_efficiency = float(request.json["l2_efficiency"] or 0)
    demand_charge = float(request.json["demand_charge"] or 0)

    print(request.json)
    d = graph_plot(bus_cost, utility, fuel_price, dc_efficiency, l2_efficiency, demand_charge)
    print(d[1])
    return {"data": d}

