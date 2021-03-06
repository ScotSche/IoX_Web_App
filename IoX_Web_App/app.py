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

def update_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    cur.close()
    get_db().commit()

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
    for data in dataSet:
        if data[2] == "0x00":
            values[0] += 1
        if data[2] == "0x10":
            values[1] += 1
        if data[2] == "0x01":
            values[2] += 1
        if data[2] == "0x11":
            values[3] += 1
    return values


def createOverviewGraph(title, values):

    labels = ['Working','Maintenance','Failure','Not Connected']
    colors = ['#72B54F', '#E29D00', '#C00000', '#A0A0A0']

    fig =  go.Figure(data=[go.Pie(values=values, labels=labels, hole=.6)])
    fig.update_traces(marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)))
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, title_text=title, title_y=1.0)
    return plot(fig, output_type='div')

def createEnvelopeGraph(data):
    data_range = []
    fig = go.Figure()
  
    for i in range(-80, 620):
        data_range.append(i)

    counter = 0
    for measurement in data:
        tmpData = measurement[-1].replace("[", "").replace("]", "").split(",")

        float_Data = []
        for value in tmpData:
            float_Data.append(float(value))
        if len(data) > 1:
            if counter < 1:
                fig.add_trace(Scatter(x=data_range, y=float_Data, name='First', line=dict(color='#009b91', width=3)))
            else:
                fig.add_trace(Scatter(x=data_range, y=float_Data, name='Current', line=dict(color='#334152', width=3)))
            counter += 1
        else:
            fig.add_trace(Scatter(x=data_range, y=float_Data, line=dict(color='#009b91', width=3)))

    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, plot_bgcolor='#d9e5ec')
    fig.update_xaxes(title_text='Distance [cm]')
    fig.update_yaxes(title_text='Echso Signal Value [dB]')

    return plot(fig, output_type='div')

def createLevelGraph(data):
    levelData = []
    data_range = []
    range_counter = 0
    for measurement in data:
        data_range.append(range_counter)
        newData = measurement[5]
        levelData.append(float(newData))
        range_counter += 1

    fig =  go.Figure(data=[Scatter(x=data_range, y=levelData, line=dict(color='#009b91', width=3))])
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, plot_bgcolor='#d9e5ec')
    fig.update_xaxes(title_text='Measurements')
    fig.update_yaxes(title_text='Relative Level [%]')

    return plot(fig, output_type='div')

def calculateStatus(measurement):

    last_envelope_curve = measurement[0][-1].replace("[", "").replace("]", "").split(",")
    float_Data = []
    for value in last_envelope_curve:
        float_Data.append(float(value))
    last_envelope_curve = float_Data

    sum_last = 0

    for i in range(80, 201):
        sum_last += last_envelope_curve[i]

    percentage = (25/462) * sum_last - (13700/213)

    if percentage < 50.0:
        return "0x00"
    if percentage < 80.0:
        return "0x10"
    else:
        return "0x11"

def getStatusResource(status):
    if status == "0x00":
        return 'resources/Symbol_W.png'
    if status == "0x01":
        return 'resources/Symbol_N.png'
    if status == "0x10":
        return 'resources/Symbol_M.png'
    if status == "0x11":
        return 'resources/Symbol_F.png'

@app.route('/')
@app.route('/dashboard')
def index():

    transferredData = [];
    with app.app_context():
        data = query_db('select * from devices')

        for device in data:
            measurements = query_db('select * from measurements where tag = ?', [device[1]])
            if len(measurements) > 0:
               status = calculateStatus([measurements[-1]])
               update_db('update device_status set status = ? where tag = ?', (status, device[1]))

        status_data = query_db('select * from device_status')

    status_selection = matchStatusWithSelection(data, status_data)
    overview_values = prepareDataForOverviewGraph(status_selection)  

    overview_plot = createOverviewGraph('Overview Device status', overview_values)

    for row in data:
        image_path = "resources/" + row[5].replace("/", "") + ".png"
        status_path = 'resources/Symbol_N.png'
        for status in status_selection:
            if row[1] in status:
                status_path = getStatusResource(status[2])
                break
        transferredData.append((image_path, row[2], row[3], row[1], row[9], row[10], row[11], status_path))

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

        if not column_specification:
            data = query_db('select * from devices')
        else:
            data = query_db('select * from devices where ' + column_specification + ' = ?', [finalElement])

        status_data = query_db('select * from device_status') 
        #print(status_data)

    status_selection = matchStatusWithSelection(data, status_data)
    overview_values = prepareDataForOverviewGraph(status_selection)  
    titles = subpath.split("/")
    for title in titles:
        if len(titles) == 1:
            header = 'Plant ' + title.split('-')[1] + ' - Overview Device Status'
        if len(titles) > 1:
            header = 'Plant ' + titles[0].split('-')[1] + ' / Facility ' + titles[1].split('-')[1] + ' - Overview Device Status'
    overview_plot = createOverviewGraph(header, overview_values)

    transferredData = [];
    for row in data:
        image_path = "resources/" + row[5].replace("/", "") + ".png"
        status_path = 'resources/Symbol_N.png'
        for status in status_selection:
            if row[1] in status:
                status_path = getStatusResource(status[2])
                break
        transferredData.append((image_path, row[2], row[3], row[1], row[9], row[10], row[11], status_path))

    envelope_plot = None

    if not column_specification:
        with app.app_context():
            specificData = query_db('select * from devices where tag = ?', [finalElement])
            measurementData = query_db('select * from measurements where tag = ?', [finalElement])
            specificStatus = query_db('select status from device_status where tag = ?', [finalElement])
      
        for status in specificStatus:
            if "0x00" in status:
                status_path = 'resources/Symbol_W.png'
            if "0x01" in status:
                status_path = 'resources/Symbol_N.png'
            if "0x10" in status:
                status_path = 'resources/Symbol_M.png'
            if "0x11" in status:
                status_path = 'resources/Symbol_F.png'

        if request.method == 'POST':
            post_element = request.form['element']
        else:
            post_element = 'envelope_curve'

        if len(measurementData) != 0:
            day_element = 0         
            if post_element == 'envelope_curve':
                day_element = (30 * 288) - 1
                envelope_plot = createEnvelopeGraph([measurementData[-1]])
            if post_element == 'level_curve':
                with app.app_context():
                    measurementData = query_db("select * from measurements where tag = ? and measuring like '%M-29/04%'", [finalElement])
                envelope_plot = createLevelGraph(measurementData)
            if post_element == 'comp_envelope_curve':
                measurement_element = int(request.form['measurement'])
                day_element = (int(request.form['day']) * 288 - (288 - measurement_element)) -1
                array_of_measurement_Data = []
                array_of_measurement_Data.append(measurementData[0])
                array_of_measurement_Data.append(measurementData[day_element])
                envelope_plot = createEnvelopeGraph(array_of_measurement_Data)
            if post_element == 'first_envelope_curve':
                day_element = 0
                envelope_plot = createEnvelopeGraph([measurementData[0]])              
            if post_element == 'latest_envelope_curve':
                day_element = (30 * 288) - 1
                envelope_plot = createEnvelopeGraph([measurementData[-1]])
            if post_element == 'previous_days':
                measurement_element = int(request.form['measurement'])
                day_element = ((int(request.form['day']) - 5) * 288 - (288 - measurement_element)) -1
                envelope_plot = createEnvelopeGraph([measurementData[day_element]])
            if post_element == 'previous_day':
                measurement_element = int(request.form['measurement'])
                day_element = ((int(request.form['day']) - 1) * 288 - (288 - measurement_element)) - 1
                envelope_plot = createEnvelopeGraph([measurementData[day_element]])
            if post_element == 'post_day':
                measurement_element = int(request.form['measurement'])
                day_element = ((int(request.form['day']) + 1) * 288 - (288 - measurement_element)) - 1
                envelope_plot = createEnvelopeGraph([measurementData[day_element]])
            if post_element == 'post_days':
                measurement_element = int(request.form['measurement'])
                day_element = ((int(request.form['day']) + 5) * 288 - (288 - measurement_element)) -1
                envelope_plot = createEnvelopeGraph([measurementData[day_element]])
            if post_element == 'previous_measures':
                measurement_element = int(request.form['measurement']) - 10
                day_element = (int(request.form['day']) * 288 - (288 - measurement_element)) - 1
                envelope_plot = createEnvelopeGraph([measurementData[day_element]])
            if post_element == 'previous_measure_one':
                measurement_element = int(request.form['measurement']) - 1
                day_element = (int(request.form['day']) * 288 - (288 - measurement_element)) - 1
                envelope_plot = createEnvelopeGraph([measurementData[day_element]])
            if post_element == 'post_measure_one':
                measurement_element = int(request.form['measurement']) + 1
                day_element = (int(request.form['day']) * 288 - (288 - measurement_element)) - 1
                envelope_plot = createEnvelopeGraph([measurementData[day_element]])
            if post_element == 'post_measures':                
                measurement_element = int(request.form['measurement']) + 10
                day_element = (int(request.form['day']) * 288 - (288 - measurement_element)) - 1
                envelope_plot = createEnvelopeGraph([measurementData[day_element]])

        for result in specificData:
            path = "resources/" + result[5].replace("/", "") + ".png"
            if len(measurementData) != 0:
                measureData = measurementData[day_element][2]
            else:
                measureData = ""
            specifiedData = (result[2], path, result[1], result[9], result[10], result[11], result[3], result[4], 
                             result[5], result[6], result[7], result[8], result[12], result[13], measureData, status_path)

        newData = [specifiedData]
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