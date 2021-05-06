"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, request, g
import sqlite3
import json
import plotly
import plotly.graph_objs as go
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
    labels = ["Working", "Maintainance", "Failure", "Not Connected"]
    values = [80, 12, 2, 6]

    #   Create Donut Pie Graph
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

    # Create subplots: use 'domain' type for Pie subplot
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/')
def index():
    transferredData = [];

    with app.app_context():
        data = query_db('select * from Dashboard')

    for row in data:
        transferredData.append((row[1], row[2], row[3], row[4], row[5]))

    #overview_plot = plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])], output_type='div')
    overview_plot = createOverviewGraph()
    return render_template('dashboard.html', transferredData=transferredData);

@app.route('/dashboard/', methods = ['POST'])
def dashboard():

    with app.app_context():
        data = query_db('select * from Dashboard')

    transferredData = [];
    for row in data:
        transferredData.append((row[1], row[2], row[3], row[4], row[5]))

    with app.app_context():
        specificData = query_db('select * from Dashboard where Tag = ?', [request.form['tag']])

    print(specificData)

    #overview_plot = plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])], output_type='div')
    overview_plot = createOverviewGraph()
    return render_template('dashboard.html', transferredData=transferredData, overview_plot=overview_plot)


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)