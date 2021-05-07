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
DATABASE = 'iox.db'
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

    fig.update_layout(title_text='Werk 1 / Anlage 1 – Übersicht Gerätestatus', title_y=1.0)

    return plot(fig, output_type='div')

def createEnvelopeGraph():
    return plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])], output_type='div')

@app.route('/')
def index():
    transferredData = [];

    with app.app_context():
        data = query_db('select * from Dashboard')

    for row in data:
        transferredData.append((row[1], row[2], row[3], row[4], row[5]))

    return render_template('dashboard.html', transferredData=transferredData, specificDate="");

@app.route('/dashboard/', methods = ['POST'])
def dashboard():

    tag = request.form['tag']

    with app.app_context():
        data = query_db('select * from Dashboard')

    with app.app_context():
        specificData = query_db('select * from Dashboard where Tag = ?', [tag])

    transferredData = [];
    for row in data:
        transferredData.append((row[1], row[2], row[3], row[4], row[5]))

    print(specificData)

    overview_plot = createOverviewGraph()
    envelope_plot = createEnvelopeGraph()

    return render_template('dashboard.html', transferredData=transferredData, 
                           overview_plot=Markup(overview_plot), specificData=specificData, envelope_plot=Markup(envelope_plot))


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)