import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify



# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session=Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")

def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>(yyyy-mm-dd)<br/>"
        f"/api/v1.0/<start>(yyyy-mm-dd/<end>yyyy-mm-dd)<br/>"
    )

#Convert the query results to a dictionary using date as the key and prcp as the value, return JSON of dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    precip_query=session.query(Measurement.date, Measurement.prcp).all()
    

    precip_results=[]
    for (date, precipitation) in precip_query:
        Measurement_dict={}
        Measurement_dict["date"]= date
        Measurement_dict["prcp"]= precipitation
        precip_results.append(Measurement_dict)

    return jsonify(precip_results)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    
    station_results=session.query(Station.station).all()

    stations=list(np.ravel(station_results))

    return jsonify(stations)

#Query the dates and temperature observations of the most active station for the last year of data, Return a JSON list of temperature observations (TOBS) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    previous_yr=dt.date(2017,8,23)-dt.timedelta(days=365)
    most_active_one_year = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>=previous_yr, Measurement.station=='USC00519281').all() 

    tobs_results=[]
    for (date,temperature) in most_active_one_year:
        Temp_dict={}
        Temp_dict["date"]= date
        Temp_dict["tobs"]= temperature
        tobs_results.append(Temp_dict)
    
    return jsonify(tobs_results)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start, 
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route("/api/v1.0/<start>")
def start(start):
    
    start_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    start_list = []
    for result in start_results:
        start_dict = {}
        start_dict["TEMP_MIN"] = result[0]
        start_dict["TEMP_MAX"] = result[1]
        start_dict["TEMP_AVG"] = result[2]
        start_list.append(start_dict)

    
    return jsonify(start_list)


#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
@app.route("/api/v1.0/<start>/<end>")
def start_end (start,end):

    start_end_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date<= end).all()
    session.close()

    start_end_list = []
    for result in start_end_results:
        start_end = {}
        start_end["TEMP_MIN"] = result[0]
        start_end["TEMP_MAX"] = result[1]
        start_end["TEMP_AVG"] = result[2]
        start_end_list.append(start_end)

    
    return jsonify(start_end_list)


if __name__=='__main__':
    app.run(debug=True)


