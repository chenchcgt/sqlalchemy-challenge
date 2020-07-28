import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

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
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-19<br/>"
        f"/api/v1.0/'start_date'/'end_date'<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prec_data = session.query(Measurement.date, Measurement.prcp).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()

    session.close()

    all_precipitation = list(np.ravel(prec_data))

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)

    stations_data = session.query(Measurement.station).\
    group_by(Measurement.station).\
    order_by(Measurement.station).all()

    session.close()

    all_stations = list(np.ravel(stations_data))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)

    tobs_data = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >'2016-08-18').\
    filter(Measurement.station=='USC00519281').\
    order_by(Measurement.date.desc()).all()

    session.close()

    all_tobs = list(np.ravel(tobs_data))

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start_date>")
def start(start_date):
    session=Session(engine)

    # date_data = session.query(Measurement.date,Measurement.tobs).all()
    min_data = session.query(Measurement.date,func.min(Measurement.tobs)).\
        filter(Measurement.date>=start_date).first()
    
    avg_data = session.query(Measurement.date,func.avg(Measurement.tobs)).\
        filter(Measurement.date>=start_date).first()

    max_data = session.query(Measurement.date,func.max(Measurement.tobs)).\
        filter(Measurement.date>=start_date).first()   
    session.close()

    min_data = list(np.ravel(min_data))
    avg_data = list(np.ravel(avg_data))
    max_data = list(np.ravel(max_data))


    # for date in all_data:
    #     print(date)
    #     min_data = session.query(Measurement.date,func.min(Measurement.tobs)).\
    #     filter(Measurement.date>=("start_date")).first()

        # min_data = session.query(Measurement.date,func.min(Measurement.tobs)).\
        # filter(Measurement.date>=date["start_date"]).first()

    # return jsonify(min_data)
    return jsonify(min_data, avg_data, max_data)



   

if __name__ == '__main__':
    app.run(debug=True)