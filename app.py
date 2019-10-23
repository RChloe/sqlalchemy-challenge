from flask import Flask, jsonify

import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

measurements = pd.read_csv("Resources/hawaii_measurements.csv")
stations = pd.read_csv("Resources/hawaii_stations.csv")

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    return (
        f"Welcome to the Honolulu Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    measurements.dropna(inplace=True)
    measurements_df = pd.DataFrame(measurements,columns=['date','prcp'])
    measurements_dict=measurements_df.set_index('date').T.to_dict('list')

    return (
        jsonify(measurements_dict)
    )

@app.route("/api/v1.0/stations")
def station():
    stations_df = pd.DataFrame(stations,columns=['station'])
    stations_dict = stations_df.to_dict('list')

    return (
        jsonify(stations_dict)
    )

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date))
    last_date_list=[date[0] for date in last_date]
    last_date_date=dt.datetime.strptime(last_date_list[0],'%Y-%m-%d')
    twelve_months_ago=last_date_date-dt.timedelta(days=365)
    twelve_months_ago_string=twelve_months_ago.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and tobs scores
    tobs_scores = session.query(Measurement.tobs,Measurement.date).filter(Measurement.date>twelve_months_ago_string)
    tobs_last_12 = pd.DataFrame(tobs_scores)

    tobs_df = pd.DataFrame(tobs_last_12,columns=['date','tobs'])
    tobs_dict=tobs_df.set_index('date').T.to_dict('list')

    return (
        jsonify(tobs_dict)
    )

@app.route("/api/v1.0/<start_date>")
# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date=None):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    last_date = session.query(func.max(Measurement.date))
    if end_date is None:
        end_date = last_date
    return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all())

@app.route("/api/v1.0/<start_date>/<end_date>")
# This function called `calc_temps2` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps2(start_date, end_date=None):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    last_date = session.query(func.max(Measurement.date))
    if end_date is None:
        end_date = last_date
    return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all())


if __name__ == "__main__":
    app.run(debug=True)
