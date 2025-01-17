
import dash
from flask import Flask

from callbacks import register_callbacks
from layouts import apply_layout

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

apply_layout(app)  # create client UI
register_callbacks(app)  # enable ui interactions (server->client callbacks)

if __name__ == '__main__':
    app.run_server(port=8050, debug=True)
