
import dash
from flask import Flask

from callbacks import register_callbacks
from layouts import apply_layout

from config import DASH_DEFAULT_PORT, TC_DEFAULT_URL
import argparse

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tc-url', type=str, default=TC_DEFAULT_URL)
    parser.add_argument('--dash-port', type=int, default=DASH_DEFAULT_PORT)
    args = parser.parse_args()

    apply_layout(app)  # create client UI
    register_callbacks(app, args.tc_url)  # enable ui interactions (server->client callbacks)

    app.run_server(port=args.dash_port, debug=True)
