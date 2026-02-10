import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_ag_grid as dag
from dash import html, dcc, Input, Output, State, no_update
from dash import Dash
from dash import ctx
from dash_extensions.javascript import assign
import geopandas as gpd
import pandas as pd


on_each_feature = assign(
    """
    function(feature, layer, context){
        layer.bindTooltip(
            `
            <p><b>Municipio:</b> ${feature.properties.NOM_MUN}</p>
            `
        );
    }
    """
)

geojson = dl.GeoJSON(
    url="assets/Pozos.geojson",
    zoomToBounds=True,  
    onEachFeature=on_each_feature,
    id="geojson-pozos",  
    n_clicks=0
)


df_base = pd.DataFrame(gpd.read_file("assets/Pozos.geojson").drop(columns="geometry"))

impresion_datos = dcc.Store(id="impresion_datos")

fuente_abastecimiento = dbc.ModalTitle(id="modal-titulo")
municipio = html.P(id="modal-municipio")
localidad = html.P(id="modal-localidad")

grid = dag.AgGrid(
    id="impresion_tabla",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "300px", "width": "100%"},
)

modal_popup = dbc.Modal(
    [
        dbc.ModalHeader(fuente_abastecimiento),
        dbc.ModalBody(
            [
                municipio,
                localidad,
                grid,
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Descargar / Imprimir",
                    id="download-modal",
                    color="primary",
                    className="ms-auto",
                ),
                dbc.Button(
                    "Cerrar",
                    id="close-modal",
                    className="ms-2",
                ),
            ]
        ),
    ],
    id="modal",
    is_open=False,
    size="xl",
)

app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)


app.layout = html.Div(
    [
        impresion_datos, 
        dl.Map(
            children=[dl.TileLayer(), geojson],
            style={"height": "100vh"},
            center=[20, -98],
            zoom=6,
        ),
        modal_popup,
        html.Div(id="dummy-print"), 
    ],
    style={"height": "100vh"},
)


@app.callback(
    Output("modal", "is_open"),
    Output("modal-titulo", "children"),
    Output("modal-municipio", "children"),
    Output("modal-localidad", "children"),
    Output("impresion_tabla", "rowData"),
    Output("impresion_tabla", "columnDefs"),
    Output("impresion_datos", "data"),
    Input("geojson-pozos", "clickData"),
    Input("close-modal", "n_clicks"),
    State("modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_modal(feature, close_clicks, is_open):
    # Quien disparó el callback
    trigger_id = ctx.triggered_id


    if trigger_id == "geojson-pozos" and feature:
        properties = feature["properties"]
        pozo_id = properties.get("ID")
        

        municipio = properties.get("NOM_MUN", "N/A")
        localidad = properties.get("NOM_LOC", "N/A")

        df_filtro = df_base[df_base["ID"] == pozo_id]

        columnas_eliminar = ["CVEGEO_LOC", "ID", "NOM_MUN", "NOM_LOC", "Fuente de abastecimiento"]
        df_filtro = df_filtro.drop(columns=columnas_eliminar, errors='ignore')

       
        df_filtro = df_filtro.melt(var_name="Concepto", value_name="Detalle")
        
        
        row_datos = df_filtro.to_dict("records")
        columnas = [{"field": i} for i in df_filtro.columns]

        entorno_impresion = {
            "Titulo": f"Fuente de abastecimiento {pozo_id}",
            "Municipio": f"Municipio: {municipio}",
            "Localidad": f"Localidad: {localidad}",
            "Datos": row_datos,
            "Columnas": columnas
        }


        return (
            True,                         
            f"Fuente de abastecimiento {pozo_id}", 
            f"Municipio: {municipio}",      
            f"Localidad: {localidad}",      
            row_datos,                     
            columnas,                      
            entorno_impresion                      
        )


    elif trigger_id == "close-modal":
        
        return False, "", "", "", [], [], None

    return no_update

app.clientside_callback(
    """
    var printContents = document.getElementById('grid-print-area').innerHTML;
         var originalContents = document.body.innerHTML;

         document.body.innerHTML = printContents;

         window.print();

         document.body.innerHTML = originalContents;
         location.reload()

        return window.dash_clientside.no_update
    }
    """,
    Output("dummy-print", "children"),
    Input("download-modal", "n_clicks"),
    prevent_initial_call=True
)

if __name__ == "__main__":
    app.run(debug=True)
