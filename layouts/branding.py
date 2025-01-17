from dash import html


def create_branding():
    """
    Creates the stylized branding floating logos
    """

    return html.Div(
        id="branding-container",
        style={
            "position": "absolute",
            "top": "10px",
            "left": "60px",
            "backgroundColor": "rgba(255, 255, 255, 0.9)",
            "borderRadius": "10px",
            "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.2)",
            "padding": "10px 20px",
            "display": "flex",
            "alignItems": "center",
            "zIndex": "1000",
        },
        children=[
            html.A(
                href="https://www.nasa.gov/",
                target="_blank",
                children=[
                    html.Img(
                        src="/assets/images/nasa_logo.png",
                        style={"height": "40px", "marginRight": "10px"},
                        alt="NASA Logo",
                    )
                ]
            ),
            html.Div(style={"margin-left": "10px", "margin-right": "10px", "width": "2px",
                     "height": "30px", "background-color": "rgba(0, 0, 0, 0.15)"}),
            html.A(
                href="https://pace.oceansciences.org/harp2.htm",
                target="_blank",
                children=[
                    html.Img(
                        src="/assets/images/nasa_pace_logo.png",
                        style={"height": "40px", "marginRight": "10px"},
                        alt="PACE HARP2 Logo",
                    )
                ]
            ),
            html.Div(style={"margin-left": "10px", "margin-right": "10px", "width": "2px",
                     "height": "30px", "background-color": "rgba(0, 0, 0, 0.15)"}),
            html.A(
                href="https://esi.umbc.edu/",
                target="_blank",
                children=[
                    html.Img(
                        src="/assets/images/umbc_esi_logo.jpg",
                        style={"height": "40px"},
                        alt="UMBC Logo",
                    ),
                ]
            )
        ],
    )
