import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

from flask import Flask, jsonify

#query date from part 1

query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#Database

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#ORM

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask 

app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start=YYYY-MM-DD<br>"
        f"/api/v1.0/start=YYYY-MM-DD/end=YYYY-MM-DD<br>"
    )

#Routes

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= query_date).\
    order_by(Measurement.date.desc()).all()

    session.close()

    precip_obs = []
    for date, prcp in results: 
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = prcp
        precip_obs.append(precip_dict)
    
    return jsonify(precip_obs)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station).all()

    station_list = []
    for result in results: 
        station_dict = {}
        station_dict["id"] = result.id
        station_dict["name"] = result.name
        station_dict["latitude"] = result.latitude
        station_dict["longitude"] = result.longitude
        station_dict["elevation"] = result.elevation
        station_list.append(station_dict)

    session.close( )

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    session = Session(engine)

    station = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()

    active_station = station.station
    
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.station == active_station).\
    order_by(Measurement.date.desc()).all()

    session.close()

    temp_data = []
    for date, tobs in results: 
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature"] = tobs 
        temp_data.append(temp_dict)

    return jsonify(temp_data)

@app.route("/api/v1.0/start=<start>")
def start_date(start): 
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()

    temp_data = []
    for tmin, tmax, tavg in results: 
        temp_dict = {}
        temp_dict["Temp Min"] = tmin
        temp_dict["Temp Max"] = tmax 
        temp_dict["Temp Avg"] = tavg
        temp_data.append(temp_dict)

        return jsonify(temp_data)

@app.route("/api/v1.0/start=<start>/end=<end>")
def dates(start, end): 
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    temp_data = []
    for tmin, tmax, tavg in results: 
        temp_dict = {}
        temp_dict["Temp Min"] = tmin
        temp_dict["Temp Max"] = tmax 
        temp_dict["Temp Avg"] = tavg
        temp_data.append(temp_dict)

        return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)
