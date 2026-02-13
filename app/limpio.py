import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_ag_grid as dag

from dash import html, dcc, Input, Output, State, no_update, ctx
from dash_extensions.enrich import DashProxy
from dash_extensions.javascript import assign

import geopandas as gpd
import pandas as pd

on_each_feature = assign("""function(feature, layer, context){
    layer.bindTooltip(`<p><b>Municipio:</b> ${feature.properties.NOM_MUN}</p>`);
}""")

geojson = dl.GeoJSON(
    url="assets/Pozos.geojson",
    zoomToBounds=True,  
    onEachFeature=on_each_feature,
    id="geojson-pozos",  
    n_clicks=0
)


df_base = pd.DataFrame(gpd.read_file("assets/Pozos.geojson").drop(columns="geometry"))


modal_fuente = html.P(id="modal_abastecimiento")
modal_municipio = html.P(id="modal_municipio")
modal_localidad = html.P(id="modal_localidad")


print_fuente = html.P(id="print_abastecimiento")
print_municipio = html.P(id="print_municipio")
print_localidad = html.P(id="print_localidad")

modal_tabla = dag.AgGrid(
    id="modal_tabla",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "50vh", "width": "100%"},
)

impresion_tabla = dag.AgGrid(
    id="impresion_tabla",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},        
    style={"height": "", "width": ""},
    dashGridOptions={"domLayout": "print"}
)

entorno_impresion = html.Div(
    [
        dbc.ModalBody(
            [
                print_fuente,    
                print_localidad,
                print_municipio,
                impresion_tabla,
            ],
        ),
    ],
    id="entorno_impresion",
    style={'display': 'none'} 
)

modal_popup = dbc.Modal(
    [
        dbc.ModalHeader(modal_fuente), 
        dbc.ModalBody(
            [
                modal_municipio,
                modal_localidad,
                modal_tabla,
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Button("Descargar / Imprimir", id="download-modal", color="primary", className="ms-auto"),
                dbc.Button("Cerrar", id="close-modal", className="ms-2"),
            ]
        ),
    ],
    id="modal_popup",
    is_open=False,
    size="xl",
)

app = DashProxy(
    prevent_initial_callbacks=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

app.layout = html.Div(
    [
        dl.Map(
            children=[dl.TileLayer(), geojson],
            style={"height": "100vh"},
            center=[20, -98],
            zoom=6,
        ),
        modal_popup,
        entorno_impresion,
        html.Div(id="dummy-print"),  
    ],
)

@app.callback(
    Output("modal_popup", "is_open"),

    Output("modal_abastecimiento", "children"),
    Output("modal_municipio", "children"),
    Output("modal_localidad", "children"),
    Output("modal_tabla", "rowData"),
    Output("modal_tabla", "columnDefs"),

    Output("impresion_tabla", "rowData"),
    Output("impresion_tabla", "columnDefs"),
    Output("print_abastecimiento", "children"),
    Output("print_municipio", "children"),
    Output("print_localidad", "children"),
    
    Input("geojson-pozos", "clickData"),
    Input("close-modal", "n_clicks"),
    Input("geojson-pozos", "n_clicks"),
    State("modal_popup", "is_open"),
)
def toggle_modal(feature, close_clicks, n_clicks, is_open):

    trigger_id = ctx.triggered_id 
    
    if trigger_id == "geojson-pozos" and feature:
        properties = feature["properties"]
        pozo_id = properties.get("ID")
        
        abastecimiento = properties.get("Fuente de abastecimiento", "N/A")
        nom_municipio = properties.get("NOM_MUN", "N/A")
        nom_localidad = properties.get("NOM_LOC", "N/A")

        # Filtrado
        df_filtro = df_base[df_base["ID"] == pozo_id]
        columnas_eliminar = ["CVEGEO_LOC", "ID", "NOM_MUN", "NOM_LOC", "Fuente de abastecimiento"]
        df_filtro = df_filtro.drop(columns=columnas_eliminar, errors='ignore')

        df_filtro = df_filtro.T.reset_index()
        df_filtro.columns = df_filtro.iloc[0]
        df_filtro = df_filtro.iloc[1:]
        
        row_datos = df_filtro.to_dict("records")
        columnas = [{"field": i} for i in df_filtro.columns]

        txt_abs = f"Fuente de Abastecimiento: {abastecimiento}"
        txt_mun = f"Municipio: {nom_municipio}"
        txt_loc = f"Localidad: {nom_localidad}"

        return (
            True,     

            txt_abs,        
            txt_mun,
            txt_loc,
            row_datos,      
            columnas,
            
            row_datos,     
            columnas,
            txt_abs,        
            txt_mun,
            txt_loc
        )
    elif trigger_id == "close-modal":
        return (
            False, 
            no_update, no_update, no_update, no_update, no_update,
            no_update, no_update, no_update, no_update, no_update
        )
    

app.clientside_callback(
    """
    function(){
        var printContents = document.getElementById('entorno_impresion').innerHTML;
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
    prevent_initial_call=True,
)

