import os
import json
import plotly
import eventlet
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from collections import deque
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app)

N = 100
x = np.linspace(0, 1, N)
y = deque([0 for _ in range(0, N)], N)


def update_plot():
    while True:
        json, data = create_plot()
        socketio.emit('plot', data)
        eventlet.sleep(1)


def create_plot():
    info = os.popen('free -t -m').readlines()[1].split()[1:4]
    tot_m, used_m, free_m = map(int, info)

    df = pd.DataFrame({'x': x, 'y': y})

    y.append(used_m)

    data = [go.Scatter(x=df['x'], y=df['y'])]

    layout = go.Layout(yaxis=dict(range=[0, tot_m]))

    graphJSON = json.dumps(dict(data=data,layout=layout), cls=plotly.utils.PlotlyJSONEncoder)

    return (graphJSON, json.loads(graphJSON))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    eventlet.spawn(update_plot)
    socketio.run(app)
