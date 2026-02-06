import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_bootstrap_components as dbc 
from dash import Dash, html, Output, Input, State, no_update,dcc
from dash_extensions.enrich import DashProxy, Input, Output, html
from dash_extensions.javascript import assign
from dash_extensions.javascript import arrow_function

import geopandas as gpd
import pandas as pd


on_each_feature = assign("""
                                          
function(feature, layer, context){
                         
    layer.bindTooltip(
        `
        <p><b>Municipio:</b> ${feature.properties.NOM_MUN}</p>
        `
    );                      
}
""")



geojson = dl.GeoJSON(
    url="assets/Acciones_de_desinfeccion_municipal.geojson",
    zoomToBounds=True,  
    onEachFeature=on_each_feature,
    id="geojson-pozos",  
    n_clicks=0
)







modal_popup = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("", id="Titulo_modal")
        ),

        dbc.ModalBody(
            html.Div(
                [
                    html.Strong("Cloro Residual Libre:"),
                    html.Ul(
                        [
                            html.Li("2020:", id="cloro_2020"),
                            html.Li("2021:", id="cloro_2021"),
                            html.Li("2022:", id="cloro_2022"),
                            html.Li("2023:", id="cloro_2023"),
                        ]
                    ),
                    html.P("Número de pozos en ese municipio: X"),
                    html.P("Número de dosificadores en ese municipio: X"),
                    html.P("Nombre de dosificadores: X"),
                    html.P("Localidad donde se encuentra el dosificador: X"),
                    html.P("Año de instalación de dosificadores: X"),
                ]
            )
        ),

        dbc.ModalFooter(
            [
                dbc.Button(
                    "Descargar",
                    id="download-modal",
                    className="ms-auto",
                ),
                dbc.Button(
                    "Cerrar",
                    id="close-modal",
                    className="ms-auto",
                ),
            ]
        ),
    ],
    id="modal",
    is_open=False,
    size="xl",
)


app = DashProxy(prevent_initial_callbacks=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dl.Map(
            children=[dl.TileLayer(), geojson],
            style={"height": "100vh"},
            center=[20, -98], 
            zoom=6
        ),
        modal_popup,
    ],
    style={"height": "100vh"}
)



@app.callback(
    Output("modal", "is_open"),
    [Input("geojson-pozos", "clickData"),
     Input("close-modal", "n_clicks"),
     Input("geojson-pozos", "n_clicks")],
    [dash.dependencies.State("modal", "is_open")],
)
def toggle_modal(feature, close_clicks, n_clicks, is_open):
    if feature or close_clicks:
        return not is_open
    return is_open

# @app.callback(Output("modal", "children"), [Input("geojson-pozos", "clickData")])
# def update_modal_content(feature):
#     if feature is not None:
#         properties = feature['properties']
#         content = [
#             html.H4(f"Fuente de abastecimiento: {properties['Fuente de abastecimiento']}"),
#             html.P(f"Municipio: {properties['NOM_MUN']}"),
#             html.P(f"Localidad: {properties['NOM_LOC']}"),
#         ]
#         return content
#     return "No data available"


@app.callback(
    [Output("Titulo_modal", "children"), Output("cloro_2020", "children"), Output("cloro_2021", "children"), Output("cloro_2022", "children"), Output("cloro_2023", "children")],
    [Input("geojson-pozos", "clickData")]
)
def update_modal_content(feature):
    if feature is not None:
        properties = feature['properties']
        title = f"{properties['NOM_MUN']}"
        content = [
            f"2020: {properties['CLORO_2020']}",
            f"2021: {properties['CLORO_2021']}",
            f"2022: {properties['CLORO_2022']}",
            f"2023: {properties['CLORO_2023']}",
        ]
        return title, content[0], content[1], content[2], content[3]
    return "No data available", "", "", "", ""

if __name__ == "__main__":
    app.run(debug=True)