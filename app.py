import os

import dash
from flask import Flask

from callbacks import register_callbacks
from layouts import apply_layout

from config import DASH_DEFAULT_PORT, TC_DEFAULT_URL
import argparse
from dotenv import load_dotenv

load_dotenv()

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

if __name__ == '__main__':
    tc_url = os.getenv("TC_URL")
    dash_port = os.getenv("DASH_PORT")

    apply_layout(app)  # create client UI
    register_callbacks(app, tc_url)  # enable ui interactions (server->client callbacks)

    app.run_server(port=dash_port)
