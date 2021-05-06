"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template
import sqlite3
import json
import plotly
import plotly.graph_objs as go

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


def createOverviewGraph():
    labels = ["Working", "Maintainance", "Failure", "Not Connected"]
    values = [80, 12, 2, 6]

    #   Create Donut Pie Graph
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

    # Create subplots: use 'domain' type for Pie subplot
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/')
@app.route('/dashboard')
def dasboard():
    """Renders a sample page."""
    connection = sqlite3.connect("iox.db")
    mycursor =connection.cursor()
    mycursor.execute("SELECT * FROM Dashboard")
    data = mycursor.fetchall()
    connection.close()

    transferredData = [];
    for row in data:
        transferredData.append((row[1], row[2], row[3], row[4], row[5]))

    #overview_plot = plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])], output_type='div')
    overview_plot = createOverviewGraph()
    return render_template('dashboard.html', transferredData=transferredData, overview_plot=overview_plot)

@app.route('/hello')
def hello():
    """Renders a sample page."""
    return render_template('index.html')

@app.route('/bye')
def bye():
    """Renders a sample page."""
    return "Bye World!"

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)