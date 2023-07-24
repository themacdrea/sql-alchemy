# Import the dependencies.
import sqlalchemy
from flask import Flask, jsonify
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect



#################################################
# Database Setup
#################################################
database_path = r"C:\Users\dreas\OneDrive\Documents\BOOTCAMP\Module 10 Challenge\Starter_Code\Surfs Up\Resources\hawaii.sqlite"

engine = create_engine(f"sqlite:///{database_path}")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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
@app.route('/')
def home():
    return (
        "<h1>Welcome to the Climate App</h1><br/>"
        "<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Retrieve only the last 12 months of data
    last_date = session.query(func.max(measurement.date)).scalar()
    last_12_months_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= last_12_months_date).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    # Query the list of unique station names
    results = session.query(station.station).distinct().all()

    # Convert the query results to a list of station names
    station_list = [result[0] for result in results]

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Query the most active station (station with the most temperature observations)
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()[0]

    # Query the temperature observations for the previous year from the most active station
    last_date = session.query(func.max(measurement.date)).filter(measurement.station == most_active_station).scalar()
    last_12_months_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    results = session.query(measurement.tobs).\
        filter(measurement.station == most_active_station, measurement.date >= last_12_months_date).all()

    # Convert the query results to a list of temperature observations
    temp_data = [result[0] for result in results]

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(port=8080)
