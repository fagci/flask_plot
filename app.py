import json
import plotly
import psutil
import eventlet
import numpy as np
from plotly.graph_objs import Scattergl, Layout
from collections import deque
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

N = 60
x = np.linspace(0, N, N)
y_mem = deque([None for _ in range(0, N)], N)
y_cpu = deque([None for _ in range(0, N)], N)

cpu_count = psutil.cpu_count()
mem_total = psutil.virtual_memory().total

def update_plot():
    while True:
        plot = create_plot()
        socketio.emit('plot', plot)
        eventlet.sleep(1)


def create_plot():
    mem = psutil.virtual_memory().used
    cpu = psutil.cpu_percent()

    y_mem.append(mem * 100 / mem_total)
    y_cpu.append(cpu)

    data = [
            Scattergl(x=x, y=list(y_mem), name='RAM'),
            Scattergl(x=x, y=list(y_cpu), name='CPU')
            ]

    layout = Layout(yaxis=dict(range=[0, 100]))

    enc = plotly.utils.PlotlyJSONEncoder
    return json.loads(json.dumps(dict(data=data, layout=layout), cls=enc))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    eventlet.spawn(update_plot)
    socketio.run(app)
