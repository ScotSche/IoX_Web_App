"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, request, Markup, g
import sqlite3
import json
import plotly
from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.graph_objects as go
import database as db

#   Create Flask application
app = Flask(__name__)

#   Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

#   Create database object
DATABASE = 'PID.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def createOverviewGraph():

    labels = ['Working','Maintenance','Failure','Not Connected']
    colors = ['lightgreen', 'orange', 'red', 'gray']
    values = [4500, 2500, 1053, 500]

    fig =  go.Figure(data=[go.Pie(values=values, labels=labels, hole=.6)])
    fig.update_traces(marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)))
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, title_text='Werk 1 / Anlage 1 – Übersicht Gerätestatus', title_y=1.0)

    return plot(fig, output_type='div')

def createEnvelopeGraph(data):
    data_range = []
    for i in range(-80, 620):
        data_range.append(i)

    data_values = data[-1].replace("[", "").replace("]", "").split(",")

    float_Data = []
    for value in data_values:
        float_Data.append(float(value))

    fig =  go.Figure(data=[Scatter(x=data_range, y=float_Data)])
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300)

    return plot(fig, output_type='div')

@app.route('/')
def index():
    transferredData = [];

    with app.app_context():
        data = query_db('select * from devices')

    for row in data:
        image_path = "resources/" + row[5].replace("/", "") + ".png"
        transferredData.append((image_path, row[2], row[3], row[1], row[9], row[10], row[11], "Status"))

    overview_plot = createOverviewGraph()

    return render_template('dashboard.html', transferredData=transferredData, overview_plot=Markup(overview_plot));

@app.route('/dashboard', methods = ['POST'])
def dashboard():

    tag = request.form['tag']
    
    with app.app_context():
        data = query_db('select * from devices')

    with app.app_context():
        specificData = query_db('select * from devices where tag = ?', [tag])

    with app.app_context():
        measurementData = query_db('select * from measurements where tag = ?', [tag])

    print(measurementData)

    for result in specificData:
        path = "resources/" + result[5].replace("/", "") + ".png"
        specifiedData = (result[2], path, result[1], result[9], result[10], result[11], result[3], result[4], 
                         result[5], result[6], result[7], result[8], result[12], result[13])

        newData = [specifiedData]
        print(newData)

    transferredData = [];
    for row in data:
        image_path = "resources/" + row[5].replace("/", "") + ".png"
        transferredData.append((image_path, row[2], row[3], row[1], row[9], row[10], row[11], "Status"))

    overview_plot = createOverviewGraph()
    envelope_plot = None
    if len(measurementData) != 0:
        envelope_plot = createEnvelopeGraph(measurementData[-1])

    return render_template('dashboard.html', transferredData=transferredData, 
                           overview_plot=Markup(overview_plot), specificData=newData, 
                           envelope_plot=Markup(envelope_plot))

@app.route('/dashboard/<path:subpath>', methods = ['GET'])
def specificDashboard(subpath):

    finalElement = subpath.split("/")
    finalElement = finalElement[-1]

    column_specification = ""
    if "P" in finalElement:
        column_specification = "plant"
    if "F" in finalElement:
        column_specification = "facility"

    with app.app_context():
        if not column_specification:
            data = query_db('select * from devices')
        else:
            data = query_db('select * from devices where ' + column_specification + ' = ?', [finalElement])

    transferredData = [];
    for row in data:
        image_path = "resources/" + row[5].replace("/", "") + ".png"
        transferredData.append((image_path, row[2], row[3], row[1], row[9], row[10], row[11], "Status"))

    overview_plot = createOverviewGraph()
    envelope_plot = None

    if not column_specification:
        with app.app_context():
            specificData = query_db('select * from devices where tag = ?', [finalElement])
            measurementData = query_db('select * from measurements where tag = ?', [finalElement])

        for result in specificData:
            path = "resources/" + result[5].replace("/", "") + ".png"
            specifiedData = (result[2], path, result[1], result[9], result[10], result[11], result[3], result[4], 
                             result[5], result[6], result[7], result[8], result[12], result[13])

        newData = [specifiedData]

        if len(measurementData) != 0:
            envelope_plot = createEnvelopeGraph(measurementData[-1])
    else:
        newData = []

    return render_template('dashboard.html', transferredData=transferredData, 
                           overview_plot=Markup(overview_plot), specificData=newData, 
                           envelope_plot=Markup(envelope_plot))


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)