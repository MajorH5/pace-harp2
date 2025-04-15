from .map_callbacks import register_map_callbacks
from .ui_callbacks import register_ui_callbacks


def register_callbacks(app, tc_url):
    """
    Registers all callbacks for the Dash app.
    """
    register_map_callbacks(app, tc_url)
    register_ui_callbacks(app)
