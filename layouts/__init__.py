from .root import create_root


def apply_layout(app):
    """
    Setups the root layout component on the app
    """
    app.title = "UMBC | Geospatial Data Explorer"
    app.layout = create_root()
