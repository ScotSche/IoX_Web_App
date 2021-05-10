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

def matchStatusWithSelection(overViewData, statusData):
    status_selection = []
    for data in overViewData:
        for status in statusData:
            if data[1] in status:
                status_selection.append(status)
                break
    return status_selection

def prepareDataForOverviewGraph(dataSet):
    values = [0, 0, 0, 0]
    print(dataSet)
    for data in dataSet:
        if data[2] == "0x00":
            values[0] += 1
        if data[2] == "0x01":
            values[1] += 1
        if data[2] == "0x10":
            values[2] += 1
        if data[2] == "0x11":
            values[3] += 1
    return values


def createOverviewGraph(values):

    labels = ['Working','Maintenance','Failure','Not Connected']
    colors = ['lightgreen', 'orange', 'red', 'gray']

    fig =  go.Figure(data=[go.Pie(values=values, labels=labels, hole=.6)])
    fig.update_traces(marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)))
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, title_text='Werk 1 / Anlage 1 – Übersicht Gerätestatus', title_y=1.0)

    return plot(fig, output_type='div')

def createEnvelopeGraph(data, element_description):
    data_range = []

    if element_description == 'envelope_curve':
        for i in range(-80, 620):
            data_range.append(i)

        data_values = data[-1].replace("[", "").replace("]", "").split(",")

        float_Data = []
        for value in data_values:
            float_Data.append(float(value))
        
        fig =  go.Figure(data=[Scatter(x=data_range, y=float_Data)])
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, plot_bgcolor='#d9e5ec')

    if element_description == 'level_curve':
        levelData = []
        range_counter = 0
        for measurement in data:
            data_range.append(range_counter)
            newData = measurement[5]
            levelData.append(float(newData))
            range_counter += 1

        fig =  go.Figure(data=[Scatter(x=data_range, y=levelData)])
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, plot_bgcolor='#d9e5ec')

    return plot(fig, output_type='div')

@app.route('/')
@app.route('/dashboard')
def index():
    transferredData = [];

    with app.app_context():
        data = query_db('select * from devices')
        status_data = query_db('select * from device_status')

    status_selection = matchStatusWithSelection(data, status_data)
    overview_values = prepareDataForOverviewGraph(status_selection)  

    overview_plot = createOverviewGraph(overview_values)

    for row in data:
        image_path = "resources/" + row[5].replace("/", "") + ".png"
        transferredData.append((image_path, row[2], row[3], row[1], row[9], row[10], row[11], "Status"))

    return render_template('dashboard.html', transferredData=transferredData, overview_plot=Markup(overview_plot));

@app.route('/dashboard/<path:subpath>', methods = ['GET', 'POST'])
def specificDashboard(subpath):

    finalElement = subpath.split("/")
    finalElement = finalElement[-1]

    column_specification = ""
    if "P" in finalElement:
        column_specification = "plant"
    if "F" in finalElement:
        column_specification = "facility"

    with app.app_context():

        status_data = query_db('select * from device_status')

        if not column_specification:
            data = query_db('select * from devices')
        else:
            data = query_db('select * from devices where ' + column_specification + ' = ?', [finalElement])

    status_selection = matchStatusWithSelection(data, status_data)
    overview_values = prepareDataForOverviewGraph(status_selection)   
    overview_plot = createOverviewGraph(overview_values)

    transferredData = [];
    for row in data:
        image_path = "resources/" + row[5].replace("/", "") + ".png"
        transferredData.append((image_path, row[2], row[3], row[1], row[9], row[10], row[11], "Status"))

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

        if request.method == 'POST':
            post_element = request.form['element']
        else:
            post_element = 'envelope_curve'

        if len(measurementData) != 0:
            if post_element == 'envelope_curve':
                envelope_plot = createEnvelopeGraph(measurementData[-1], post_element)
            if post_element == 'level_curve':
                envelope_plot = createEnvelopeGraph(measurementData, post_element)
            if post_element == 'comp_envelope_curve':
                envelope_plot = None
            if post_element == 'latest_envelope_curve':
                envelope_plot = None
            if post_element == 'first_envelope_curve':
                envelope_plot = None
            if post_element == 'older_envelope_curve':
                envelope_plot = None
            if post_element == 'newer_envelope_curve':
                envelope_plot = None
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