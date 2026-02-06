import dash
from dash import html, Output, Input, State
import dash_leaflet as dl
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dl.Map(
        center=[51.505, -0.09],
        zoom=13,
        children=[
            dl.TileLayer(),
            dl.Marker(
                id="marker-1",
                position=[51.505, -0.09],
                children=dl.Popup("Click me for details")
            ),
        ],
        style={"width": "100%", "height": "60vh"},
    ),

    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Marker Details")),
            dbc.ModalBody("Here’s your rich content: charts, tables, text, whatever."),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal", className="ms-auto")
            ),
        ],
        id="modal",
        is_open=False,
    ),
])


@app.callback(
    Output("modal", "is_open"),
    [Input("marker-1", "n_clicks"),
     Input("close-modal", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(marker_clicks, close_clicks, is_open):
    if marker_clicks or close_clicks:
        return not is_open
    return is_open
if __name__ == "__main__":
    app.run(debug=True)