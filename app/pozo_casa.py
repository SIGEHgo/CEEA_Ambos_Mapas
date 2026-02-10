import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_ag_grid as dag
from dash import html, dcc, Input, Output, State, no_update
from dash import Dash
from dash_extensions.javascript import assign
import geopandas as gpd
import pandas as pd
import json
import os
import math # Necesario para calculos simples si fuera python, pero lo haremos en JS

# --- Configuración Inicial ---
app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

# Definición de función JS para el tooltip
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

# Carga de datos
geojson_path = "assets/Pozos.geojson"

if os.path.exists(geojson_path):
    df_geo = gpd.read_file(geojson_path)
    geojson = dl.GeoJSON(
        url=geojson_path,
        zoomToBounds=True,
        onEachFeature=on_each_feature,
        id="geojson-pozos",
        n_clicks=0
    )
    df_base = pd.DataFrame(df_geo.drop(columns="geometry"))
else:
    print("ADVERTENCIA: No se encontró assets/Pozos.geojson (Usando datos dummy)")
    # Datos dummy para que el ejemplo funcione si copias y pegas
    df_base = pd.DataFrame({
        "ID": range(1, 50), # 50 filas para probar la paginación
        "NOM_MUN": ["Municipio A"] * 49,
        "NOM_LOC": ["Localidad B"] * 49,
        "Fuente de abastecimiento": ["Pozo"] * 49,
        "Caudal": [10.5] * 49,
        "Profundidad": [100] * 49,
        "Estado": ["Activo"] * 49
    })
    # Creamos un geojson vacío dummy para que no falle el mapa
    geojson = dl.GeoJSON(id="geojson-pozos")

# --- Componentes del Layout ---

# Almacén de datos para impresión (Invisible)
store_print_data = dcc.Store(id="store-print-data")

# Componentes para el MODAL
modal_titulo = dbc.ModalTitle(id="modal-titulo")
modal_municipio = html.P(id="modal-municipio")
modal_localidad = html.P(id="modal-localidad")

grid = dag.AgGrid(
    id="grid-regular-layout",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "300px", "width": "100%"},
)

# Estructura del Modal
modal_popup = dbc.Modal(
    [
        dbc.ModalHeader(modal_titulo),
        dbc.ModalBody(
            [
                modal_municipio,
                modal_localidad,
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

# --- Layout Principal ---
app.layout = html.Div(
    [
        store_print_data, # Store añadido
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


# --- Callbacks ---

@app.callback(
    Output("modal", "is_open"),
    Output("modal-titulo", "children"),
    Output("modal-municipio", "children"),
    Output("modal-localidad", "children"),
    Output("grid-regular-layout", "rowData"),
    Output("grid-regular-layout", "columnDefs"),
    Output("store-print-data", "data"), # Guardamos datos para imprimir
    
    Input("geojson-pozos", "clickData"),
    Input("close-modal", "n_clicks"),
    State("modal", "is_open"),
    prevent_initial_call=True,
)
def display_modal(feature, close_clicks, is_open):
    ctx = dash.callback_context
    trigger = ctx.triggered_id

    if trigger == "close-modal":
        return False, no_update, no_update, no_update, no_update, no_update, no_update

    if feature is None:
        return no_update

    props = feature["properties"]
    
    # Lógica de filtrado (Adaptada para usar ID o índice si es dummy)
    target_id = props.get("ID")
    
    # Si usas datos reales:
    if "ID" in df_base.columns:
        df_filtro = df_base[df_base["ID"] == target_id].copy()
    else:
        # Fallback para datos dummy
        df_filtro = df_base.copy() 

    # Limpieza
    cols_to_drop = ["CVEGEO_LOC", "ID", "NOM_MUN", "NOM_LOC", "Fuente de abastecimiento", "geometry"]
    existing_cols_drop = [c for c in cols_to_drop if c in df_filtro.columns]
    df_filtro = df_filtro.drop(columns=existing_cols_drop)

    # Transposición
    if not df_filtro.empty:
        df_filtro = df_filtro.T.reset_index()
        df_filtro.columns = ["Atributo", "Valor"] 
    
    df_filtro = df_filtro.astype(str)
    
    data_dict = df_filtro.to_dict("records")
    col_defs = [{"field": i} for i in df_filtro.columns]

    txt_fuente = f"Fuente: {props.get('Fuente de abastecimiento', 'N/A')}"
    txt_mun = f"Municipio: {props.get('NOM_MUN', 'N/A')}"
    txt_loc = f"Localidad: {props.get('NOM_LOC', 'N/A')}"
    
    # Empaquetamos todo lo necesario para imprimir en el Store
    print_data_package = {
        "titulo": txt_fuente,
        "municipio": txt_mun,
        "localidad": txt_loc,
        "tabla": data_dict
    }

    return (
        True,
        txt_fuente,
        txt_mun,
        txt_loc,
        data_dict,
        col_defs,
        print_data_package # Enviamos al Store
    )


# --- Callback de impresión (Javascript Avanzado) ---
app.clientside_callback(
    """
    function (n_clicks, printData) {
        if (!n_clicks || !printData) {
            return window.dash_clientside.no_update;
        }

        // 1. Configuración
        const rowsPerPage = 15;
        const data = printData.tabla;
        const totalRows = data.length;
        let finalHtml = "";

        // Estilos CSS para la impresión
        const style = `
            <style>
                @media print {
                    @page { margin: 2cm; }
                    body { -webkit-print-color-adjust: exact; }
                }
                .print-page {
                    page-break-after: always;
                    position: relative;
                    height: 100vh; /* Opcional: define altura de página */
                    padding: 20px;
                    font-family: sans-serif;
                }
                .print-page:last-child {
                    page-break-after: auto;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                    font-size: 12px;
                }
                th {
                    background-color: #f2f2f2;
                    font-weight: bold;
                }
                .header-info {
                    margin-bottom: 10px;
                    border-bottom: 2px solid #333;
                    padding-bottom: 10px;
                }
            </style>
        `;

        finalHtml += style;

        // 2. Bucle para generar páginas
        for (let i = 0; i < totalRows; i += rowsPerPage) {
            // Obtener el bloque de 15 filas
            const chunk = data.slice(i, i + rowsPerPage);
            const pageNum = Math.floor(i / rowsPerPage) + 1;
            const totalPages = Math.ceil(totalRows / rowsPerPage);

            // Iniciar contenedor de página
            finalHtml += `<div class="print-page">`;

            // Encabezado (se repite en cada página)
            finalHtml += `
                <div class="header-info">
                    <h3>${printData.titulo}</h3>
                    <p><strong>${printData.municipio}</strong> | <strong>${printData.localidad}</strong></p>
                </div>
            `;

            // Construir tabla HTML estándar
            finalHtml += `<table>`;
            finalHtml += `<thead><tr><th>Atributo</th><th>Valor</th></tr></thead>`;
            finalHtml += `<tbody>`;
            
            chunk.forEach(row => {
                finalHtml += `
                    <tr>
                        <td>${row.Atributo}</td>
                        <td>${row.Valor}</td>
                    </tr>
                `;
            });

            finalHtml += `</tbody></table>`;

            // Pie de página (Número de página)
            finalHtml += `
                <div style="margin-top: 20px; font-size: 10px; text-align: right; border-top: 1px solid #ccc; padding-top:5px;">
                    Página ${pageNum} de ${totalPages}
                </div>
            `;

            // Cerrar contenedor de página
            finalHtml += `</div>`;
        }

        // 3. Reemplazar body, imprimir y recargar
        const originalContents = document.body.innerHTML;
        document.body.innerHTML = finalHtml;
        
        // Pequeño timeout para asegurar que el CSS cargue antes de imprimir
        setTimeout(() => {
            window.print();
            document.body.innerHTML = originalContents;
            location.reload(); 
        }, 100);

        return window.dash_clientside.no_update;
    }
    """,
    Output("dummy-print", "children"),
    Input("download-modal", "n_clicks"),
    State("store-print-data", "data"), # Leemos los datos desde el Store
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=True)