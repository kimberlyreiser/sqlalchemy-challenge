



import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def index():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>" 
        f"Stations: /api/v1.0/stations<br/>" 
        f"Temperature: /api/v1.0/tobs<br/>" 
        f"Enter Start Date: /api/v1.0/[start_date format:yyyy-mm-dd]<br/>" 
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    
    queryresult = session.query(*sel).all()
    
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    
    queryresult = session.query(*sel).all()
    
    session.close()

    the_stations = []
    for station,name,latitude,longitude,elevation in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        the_stations.append(station_dict)

    return jsonify(the_stations)

@app.route('/api/v1.0/tobs')
def temperature():
    session = Session(engine)
    sel = [Measurement.date,Measurement.tobs]

    active_stations = session.query(Measurement.station,func.count(Measurement.id)).\
    group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()

    most_active_station_name = active_stations[0][0]

    most_active_station = session.query(*sel).filter(Measurement.station == most_active_station_name).all()
    
    session.close()

    temperature = []
    for date, tobs in most_active_station:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        temperature.append(temp_dict)

    return jsonify(temperature)

@app.route('/api/v1.0/<start_date>')
def entered_start(start_date):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    
    #queryresult = session.query(*sel).filter(Measurement.date >= start_date).all()
    queryresult = session.query(*sel).filter(Measurement.date >= "2017-01-01").all()
    
    session.close()

    results = []
    for min, max, avg in queryresult:
        start_date_dict = {}
        start_date_dict["Minimum"] = min
        start_date_dict["Maximum"] = max
        start_date_dict["Average"] = avg      
        results.append(start_date_dict)

    return jsonify(results)



if __name__ == '__main__':
    app.run(debug=True)