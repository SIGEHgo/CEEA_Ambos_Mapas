import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_bootstrap_components as dbc 
import dash_ag_grid as dag
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
    url="assets/Pozos.geojson",
    zoomToBounds=True,  
    onEachFeature=on_each_feature,
    id="geojson-pozos",  
    n_clicks=0
)

df = gpd.read_file("assets/Pozos.geojson")
df = pd.DataFrame(df.drop(columns="geometry"))

df_filtro = df[df['ID'] == 'San Salvador_Pacheco de Allende_Pozo Pacheco']
df_filtro = df_filtro.drop(columns=['CVEGEO_LOC', 'ID', 'NOM_MUN', 'NOM_LOC', 'Fuente de abastecimiento'])

df_filtro = df_filtro.T.reset_index()
df_filtro.columns = df_filtro.iloc[0]
df_filtro = df_filtro.iloc[1:]


grid = dag.AgGrid(
    id="grid-regular-layout",
    rowData= df_filtro.to_dict("records"),
    columnDefs=[{"field": i} for i in df_filtro.columns],
    dashGridOptions={"animateRows": False}
    )



modal_popup = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("", id="Titulo_modal")
        ),

        dbc.ModalBody(
            grid
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


if __name__ == "__main__":
    app.run(debug=True)