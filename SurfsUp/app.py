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
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end><br>"
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
    results = session.query(Station.station).all()

    session.close( )

    station_names = list(np.ravel(results))

    return jsonify(station_names)

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


if __name__ == '__main__':
    app.run(debug=True)
