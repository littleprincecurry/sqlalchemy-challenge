import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

from flask import Flask, jsonify

import datetime as dt


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)


@app.route('/')
def home():
    return (
        f'Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/startdate<br/>'
        f'/api/v1.0/startdate/enddate<br/>'
    )


@app.route('/api/v1.0/precipitation')
def rain():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['prcp'] = prcp
        precip.append(precip_dict)

    return jsonify(precip)


@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    stations = session.query(Station.station).all()

    session.close()

    return jsonify(stations)


@app.route('/api/v1.0/tobs')
def temp():
    session = Session(engine)
    x = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(x.date, '%Y-%m-%d').date()
    year_ago = last_date - dt.timedelta(days=365)
    active = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(desc(func.count((Measurement.station)))).all()
    highest = active[0][0]
    tobs = session.query(Measurement.date, Measurement.tobs, Measurement.station).filter(
        Measurement.date >= year_ago).filter(Measurement.station == highest).all()
    session.close()

    return jsonify(tobs)


@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    summary = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date == start).all()
    session.close()
    return jsonify(summary)


@app.route('/api/v1.0/<start>/<end>')
def end(start, end):
    session = Session(engine)
    summaries = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    return jsonify(summaries)


if __name__ == '__main__':
    app.run(debug=True)
