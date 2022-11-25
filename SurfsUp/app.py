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
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

#automap base
Base =automap_base()

#reflect the tables
Base.prepare(engine,reflect=True)
print(Base.classes.keys())
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
        f"Welcome to Climate API site!<br/>"
        f"Available Routes:<br/>"
        f"Percipitation Analysis to retrive last 12 months data frm 2017-08-23:  <b>/api/v1.0/precipitation</b><br/>"
        f"List of stations: <b>/api/v1.0/stations</b><br/>"
        f"Temperature observations(TOBs) at the most active station over the previous 12 months : <b>/api/v1.0/tobs</b><br/>"
        f"Enter start date (yyyy-mm-dd) to retrieve the minimum, maximum, and average temperatures for all dates after the specified date:<b>/api/v1.0/&lt;start&gt;</b><br/>"
        f"Enter start and end date (yyyy-mm-dd) to retrieve the minimum, maximum, and average temperatures for that date range: <b>/api/v1.0/&lt;start&gt;/&lt;end&gt</b>;"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Create a query  from the measurement data. 
    To find the start and end date to get the precipation value.
    To get the data in the list using the for loop."""
    session = Session(engine)
    #query to get the most recent date
    max_date = session.query(func.max(measurement.date)).first()[0]
    #query to pull the start and end date 
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    one_year_perc = session.query(measurement.date, measurement.prcp).filter(measurement.date<"2017-08-23")\
    .filter(measurement.date>"2016-08-23").order_by(measurement.date).all()
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
    query_station=session.query(station.id,station.station,station.name).all()
    session.close()

    #for loop to get the date and the precipitation and append it to a list 
    stations=[]
    for id,stat,name in query_station:
        station_dict={}
        station_dict["ID"] = id
        station_dict["Station"] = stat
        station_dict["Name"] = name
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
    
    tobs_data_station=session.query(measurement.date,measurement.station, measurement.tobs).\
             filter(measurement.date<query_startdate).\
             filter(measurement.date>query_enddate).\
             filter(measurement.station==station_active).order_by(measurement.date).all()
    session.close()

    #for loop to get the date and the precipitation and append it to a list 
    tobs=[]
    for dat,sta, temp in tobs_data_station:
        tobs_dict={}
        tobs_dict["Date"] = dat
        tobs_dict["Station"] = sta
        tobs_dict["TOBs"] = temp
        tobs.append(tobs_dict)

    #return the result in json 
    return jsonify(tobs)

@app.route('/api/v1.0/<start>')
def start(start):
    """Create a query to  using a start date to calculate min, max, average.
    To get the data in the list using the for loop."""
    session=Session(engine)
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    querytobs_calc = session.query(measurement.station,func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)).\
                 filter(measurement.date>=start).all()
    session.close()
    tob = []
    for sta,min,max,avg in querytobs_calc:
        tobs_dict={}
        tobs_dict["Station"] = sta
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg
        tob.append(tobs_dict)

    #return the result in json 
    return jsonify(tob)

@app.route('/api/v1.0/<start>/<end>')
def startstop(start,end):
     """Create a query to  using a start date to calculate min, max, average.
     To get the data in the list using the for loop."""
     session=Session(engine)
     querytobs_calc = session.query(func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)).\
                      filter(measurement.date >= start).\
                      filter(measurement.date <= end).all()
            
     session.close()
     startstop= []
     for min,max,avg in querytobs_calc:
        tobs_dict={}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg
        startstop.append(tobs_dict)

     #return the result in json 
     return jsonify(startstop)

if __name__ == "__main__":
    app.run(debug=True)
    
    



    

