import numpy as np
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func , inspect

from flask import Flask, jsonify

###################################################
#Database Setup
###################################################

#create engine
engine=create_engine("sqlite:///hawaii.sqlite")

#automap base
Base =automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

###################################################
# Flask Setup
###################################################
app=Flask(__name__)

###################################################
#Flask Routes
###################################################
@app.route("/")
def welcome():
    """Route link: List all the available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Create a query  from the measurement data. 
    To find the start and end date to get the precipation value.
    To get the data in the list using the for loop."""
    session = Session(engine)
    #query to pull the start and end date 
    startdt=session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    query_startdate=dt.datetime.strptime(startdt,"%Y-%m-%d").date()
    query_enddate=query_startdate-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    one_year_perc = session.query(measurement.date, measurement.prcp)\
    .filter(measurement.date<query_startdate)\
    .filter(measurement.date>query_enddate).order_by(measurement.date).all()
    session.close()

    #for loop to get the date and the precipitation and append it to a list
    precipitation=[]
    for date,prcp in one_year_perc:
        prcp_dict={}
        prcp_dict["Date"]=date
        prcp_dict["Precipitation"]=prcp
        precipitation.append(prcp_dict)

    #return the result in json
    return  jsonify(precipitation)  

@app.route('/api/v1.0/stations')
def stations():
    """Create a query to pull the data from station.
    To get the data in the list using the for loop."""
    session=Session(engine)
    query_station=session.query(station.id,station.station,station.name,station.latitude,station.longitude,station.elevation).all
    session.close()

    #for loop to get the date and the precipitation and append it to a list 
    stations=[]
    for id,stat,name,lat,lon,ele in query_station:
        station_dict={}
        station_dict["ID"] = id
        station_dict["Station"] = stat
        station_dict["Name"] = name
        station_dict["Latitude"] = lat
        station_dict["Longitude"] = lon
        station_dict["Elevation"] = ele
        stations.append(station_dict)

    #return the result in json    
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    """Create a query to pull the date and tobs data from measurement.
    To get the data in the list using the for loop."""
    session=Session(engine)
    # Using the most active station id
    # Query to get the start and end date
    startdt=session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    query_startdate=dt.datetime.strptime(startdt,"%Y-%m-%d").date()
    query_enddate=query_startdate-dt.timedelta(days=365)

    #query to get the most active station
    station_active = session.query(measurement.station, func.count(measurement.id)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.id).desc()).first()[0]

    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    
    tobs_data_station=session.query(measurement.station, measurement.tobs).\
             filter(measurement.date<query_startdate).\
             filter(measurement.date>query_enddate).\
             filter(measurement.station==station_active).order_by(measurement.date).all()
    session.close()

    #for loop to get the date and the precipitation and append it to a list 
    tobs=[]
    for stat, temp in tobs_data_station:
        tobs_dict={}
        tobs_dict["Station"] = stat
        tobs_dict["TOBs"] = temp
        tobs.append(tobs_dict)

    #return the result in json 
    return jsonify(tobs)

    
