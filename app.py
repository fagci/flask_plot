import json
import plotly
import psutil
import eventlet
import numpy as np
import pandas as pd
from plotly.graph_objs import Scatter, Layout
from collections import deque
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app)

N = 60
x = np.linspace(0, N, N)
y_mem = deque([0 for _ in range(0, N)], N)
y_cpu = deque([0 for _ in range(0, N)], N)


def update_plot():
    while True:
        json, data = create_plot()
        socketio.emit('plot', data)
        eventlet.sleep(1)


def create_plot():
    mem = psutil.virtual_memory().used
    mem_total = psutil.virtual_memory().total
    cpu = psutil.cpu_percent()
    cpu_count = psutil.cpu_count()

    y_mem.append(mem * 100 / mem_total)
    y_cpu.append(cpu)

    df1 = pd.DataFrame({'x': x, 'y': y_mem})
    df2 = pd.DataFrame({'x': x, 'y': y_cpu})

    data = [
            Scatter(x=df1['x'], y=df1['y'], name='RAM'),
            Scatter(x=df2['x'], y=df2['y'], name='CPU')
            ]

    layout = Layout(yaxis=dict(range=[0, 100]))

    graphJSON = json.dumps(dict(data=data,layout=layout), cls=plotly.utils.PlotlyJSONEncoder)

    return (graphJSON, json.loads(graphJSON))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    eventlet.spawn(update_plot)
    socketio.run(app)
