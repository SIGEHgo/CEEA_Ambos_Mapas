import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_ag_grid as dag

from dash import html, dcc, Input, Output, State, no_update
from dash_extensions.enrich import DashProxy
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


df = gpd.read_file("assets/Pozos.geojson")
df = pd.DataFrame(df.drop(columns="geometry"))

df_filtro = df[df["ID"] == "San Salvador_Pacheco de Allende_Pozo Pacheco"]
df_filtro = df_filtro.drop(
    columns=[
        "CVEGEO_LOC",
        "ID",
        "NOM_MUN",
        "NOM_LOC",
        "Fuente de abastecimiento",
    ]
)

df_filtro = df_filtro.T.reset_index()
df_filtro.columns = df_filtro.iloc[0]
df_filtro = df_filtro.iloc[1:]



grid = dag.AgGrid(
    id="grid-regular-layout",
    rowData=df_filtro.to_dict("records"),
    columnDefs=[{"field": i} for i in df_filtro.columns],
)

print_grid = dag.AgGrid(
    id="grid-print-layout",
    rowData=df_filtro.to_dict("records"),
    columnDefs=[{"field": i} for i in df_filtro.columns],
    style={"height": "", "width": ""},
    dashGridOptions={"domLayout": "print"},
)



fuente_abastecimiento = dbc.ModalTitle(id="Titulo_modal")
municipio = html.P(id="Municipio_modal")
localidad = html.P(id="Localidad_modal")

print_layout = html.Div(
    [
        dbc.ModalBody(
            [
                fuente_abastecimiento,
                municipio,
                localidad,
                print_grid,
            ],
            id="grid-print-area",
        ),
    ],
    id="print-layout",
)

modal_popup = dbc.Modal(
    [
       fuente_abastecimiento,
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
        print_layout,
        html.Div(id="dummy-print"),
    ],
    style={"height": "100vh"},
)


@app.callback(
    Output("modal", "is_open"),
    Output("Titulo_modal", "children"),
    Output("Municipio_modal", "children"),
    Output("Localidad_modal", "children"),
    Output("grid-regular-layout", "rowData"),
    Output("grid-regular-layout", "columnDefs"),
    Output("grid-print-layout", "rowData"),
    Output("grid-print-layout", "columnDefs"),
    Input("geojson-pozos", "clickData"),
    Input("close-modal", "n_clicks"),
    State("modal", "is_open"),
    prevent_initial_call=True,
)
def display_modal(feature, close_clicks, is_open):
    ctx = dash.callback_context
    trigger = ctx.triggered_id

    if trigger == "close-modal":
        return False, no_update, no_update, no_update, no_update, no_update

    if feature is None:
        return no_update, no_update, no_update, no_update, no_update, no_update

    df_filtro = df[df["ID"] == feature["properties"]["ID"]]
    df_filtro = df_filtro.drop(
        columns=[
            "CVEGEO_LOC",
            "ID",
            "NOM_MUN",
            "NOM_LOC",
            "Fuente de abastecimiento",
        ]
    )

    df_filtro = df_filtro.T.reset_index()
    df_filtro.columns = df_filtro.iloc[0]
    df_filtro = df_filtro.iloc[1:].astype(str)

    return (
        True,
        f"Fuente de abastecimiento: {feature['properties']['Fuente de abastecimiento']}",
        f"Municipio: {feature['properties']['NOM_MUN']}",
        f"Localidad: {feature['properties']['NOM_LOC']}",
        df_filtro.to_dict("records"),
        [{"field": i} for i in df_filtro.columns],
        df_filtro.to_dict("records"),
        [{"field": i} for i in df_filtro.columns]
    )


app.clientside_callback(
    """
    function () {
        var printContents = document.getElementById('print-layout').innerHTML;
        var originalContents = document.body.innerHTML;

        document.body.innerHTML = printContents;
        window.print();
        document.body.innerHTML = originalContents;
        location.reload();

        return window.dash_clientside.no_update;
    }
    """,
    Output("dummy-print", "children"),
    Input("download-modal", "n_clicks"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=True)
