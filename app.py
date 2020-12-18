#!/usr/bin/env python
# coding: utf-8


import flask
from flask import request
from flask_cors import CORS

from calculator import dynamic_control, graph_plot

#create a Flask server 
app = flask.Flask(__name__, static_folder='./evfleets_client/build', static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/cities')
def getcities():
    return dict(cities = [{'label': i,"value": i } for i in ["Milan", "Boston"]])

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
    demand_charge = float(request.json["demand_charge"] or 0)
    bus_type = str(request.json["bus_type"] or "30ft")

    d = graph_plot(bus_cost, utility, fuel_price, dc_efficiency, demand_charge, bus_type)
    return {"data": d}

if __name__ == '__main__':
    app.run(debug=True)