# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>" 
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2010-01-01<br/>"
        f"/api/v1.0/2010-01-01/2017-08-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def get_precipitation():
    """this endpoint retrieves only the last 12 months of precipitation data"""
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    date = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    year_ago = date - dt.timedelta(days=365)
    result = session.query(measurement.date, measurement.prcp).filter(measurement.date>=year_ago).order_by(measurement.date).all()
    formatted_results = [{'date': row.date, 'prcp': row.prcp} for row in result]
    return jsonify(formatted_results)


@app.route("/api/v1.0/stations")
def get_stations():
    data = session.query(station).all();
    formatted_data = [ {'id': row.id, 'station': row.station, 'name': row.name} for row in data]
    return jsonify(formatted_data)


@app.route("/api/v1.0/tobs")
def get_tobs():
    """this endpoint retrieves only the last 12 months of temperature observations for the most active station"""
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    date = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    year_ago = date - dt.timedelta(days=365)
    most_active_station = session.query(measurement.station).group_by(measurement.station).order_by(func.count().desc()).first()[0]
    data = session.query(measurement.date, measurement.tobs).filter(measurement.station==most_active_station).filter(measurement.date>=year_ago).all()
    formatted_data = [{'date': row.date, 'tobs':row.tobs} for row in data]
    return jsonify(formatted_data)


@app.route("/api/v1.0/<start>")
def get_stats_with_start_date(start):
    """This returns list of the minimum temperature, the average 
    temperature, and the maximum temperature for all the dates 
    greater than or equal to the start date"""
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
        data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date>=start_date).all()[0]
        return jsonify({'min': data[0], 'average': data[1], 'max': data[2]})
    except:
        return jsonify({"error": "Invalid start date. Please enter valid date with format yyyy-mm-dd."}), 404


@app.route("/api/v1.0/<start>/<end>")
def get_stats_with_start_and_end_date(start, end):
    """This returns list of the minimum temperature, the average 
    temperature, and the maximum temperature for
    the dates from the start date to the end date, inclusive."""
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
        data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date>=start_date).filter(measurement.date<=end_date).all()[0]
        return jsonify({'min': data[0], 'average': data[1], 'max': data[2]})
    except:
        return jsonify({"error": "Invalid start or end date. Please enter valid date with format yyyy-mm-dd."}), 404



if __name__ == "__main__":
    app.run(debug=False)







    
