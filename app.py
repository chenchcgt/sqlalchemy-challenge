# import libraries
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# call database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Setup Flask
app = Flask(__name__)

# Flask routes
# main page
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'start_date'<br/>"
        f"/api/v1.0/'start_date'/'end_date'<br/>"
    )

# precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # query precipitation data
    prec_data = session.query(Measurement.date, Measurement.prcp).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()

    session.close()

    all_precipitation = list(np.ravel(prec_data))

    return jsonify(all_precipitation)

# stations available
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    # query station data
    stations_data = session.query(Measurement.station).\
    group_by(Measurement.station).\
    order_by(Measurement.station).all()

    session.close()

    all_stations = list(np.ravel(stations_data))

    return jsonify(all_stations)

# temperature observation
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    count_station = session.query(Measurement.station,(func.count(Measurement.station))).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # unpack tuple
    unpack = [station for station,count in count_station]
    
    # get the most active station
    most_active_station = unpack[0]
    
    # find the last date available in dataset for the most active station
    last_date = session.query(Measurement.date).\
    filter(Measurement.station==most_active_station).\
    order_by(Measurement.date.desc()).first() 

    # get date to format and calculate last year
    dateparts = last_date[0].split('-')
    previousyear = dt.date(int(dateparts[0]),int(dateparts[1]),int(dateparts[2]))- dt.timedelta(days=365)

    # find temperature list for previous year for the most active station
    tobs_data = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date > previousyear).\
    filter(Measurement.station==most_active_station).\
    order_by(Measurement.date.desc()).all()

    session.close()

    all_tobs = list(np.ravel(tobs_data))

    return jsonify(all_tobs)

# get MIN,AVG,MAX greater and equal to start date
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    """Data displayed as MIN, AVG, MAX temperatures"""
    session=Session(engine)

    # get data based on start date entered
    start_data = session.query(func.min(Measurement.tobs),\
    func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date>=start_date).all()
     
    session.close()

    result = list(np.ravel(start_data))

    return jsonify(result)


# get MIN,AVG,MAX between start date and end date, inclusive
@app.route("/api/v1.0/<start_date>/<end_date>")
def startend(start_date,end_date):
    """Data displayed as MIN, AVG, MAX temperatures for the interval"""
    session=Session(engine)

    # get data based on interval dates entered
    start_end_data = session.query(func.min(Measurement.tobs),\
    func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date>=start_date).\
    filter(Measurement.date<=end_date).all()
     
    session.close()

    result1 = list(np.ravel(start_end_data))

    return jsonify(result1)
   

if __name__ == '__main__':
    app.run(debug=True)