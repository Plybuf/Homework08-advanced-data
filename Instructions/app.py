import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

# setting up the database.

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect database into a model
Base = automap_base()
#reflect the measure measurement table
Base.prepare(engine, reflect=True)

#save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create the session link from Python to the DB
session = Session(bind=engine)

#########################################################
# Now the fun begins... Flask

app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/tempdate/startdate<br/>"
        f"/api/v1.0/tempdate/startdate/enddate<br/>"
        f"Note: for startdate or enddate, enter the date you want to query in the path"
    )

@app.route("/api/v1.0/stations")
def stations():
    """return the list of all stations"""
    results = session.query(Station.station, Station.name).all()
    
    # convert to normal list that can be read
    all_names = list(np.ravel(results))
    
    return jsonify(all_names)
        
@app.route("/api/v1.0/precipitation")
def precip():
    """List of precip observations by station that includes date and actual number"""
    #query the weather station (not the name)
    results = session.query(Measurement).all()
    
    #create dictionary from the results
    all_precip = []
    for precip in results:
        precip_dict = {}
        precip_dict["station"] = precip.station
        precip_dict["date"] = precip.date
        precip_dict["precip"] = precip.prcp
        all_precip.append(precip_dict)
        
    return jsonify(all_precip)

@app.route("/api/v1.0/tobs")
def temp():
    """List of temperature observations by station that includes date and actual number (last 12 months)"""
    #query the weather station (not the name)
    previousyear = "2016-08-23"
    results2 = session.query(Measurement).filter(Measurement.date > previousyear).all()
    
    #create dictionary from the results
    all_temp = []
    for temp in results2:
        temp_dict = {}
        temp_dict["station"] = temp.station
        temp_dict["date"] = temp.date
        temp_dict["temperature"] = temp.tobs
        all_temp.append(temp_dict)
        
    return jsonify(all_temp)


@app.route("/api/v1.0/tempdate/<start>")
@app.route("/api/v1.0/tempdate/<start>/<end>")
def tempDate(start=None, end=None):
    """find the temp data after the start data in the path variable supplied by the user."""
    
    # do the [sel] like in the Notebook version of this work...
    sel = []
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    #query if the "end" part is not there
    if not end:
        #calc temp data after start
        results = session.query(*sel).filter(Measurement.date >= start).all()
        #unravel to get into list
        tempdata = list(np.ravel(results))
        return jsonify(tempdata)
    
    #calc temp data if start and end exists
    results = session.query(*sel).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    #unravel to get into list
    tempdata = list(np.ravel(results))
    return jsonify(tempdata)

#ending it all
if __name__ == '__main__':
    app.run(debug=True)