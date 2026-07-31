import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import geopandas as gpd
from app import anios_nh

import dash_bootstrap_components as dbc  # Importa Dash Bootstrap Components
from dash import Dash, html, Output, Input, State, no_update,dcc
import re
from dash_extensions.javascript import arrow_function, assign
import geopandas as gpd
import funciones_auxiliares
from funciones_auxiliares import generarMapApartirEleccion_Municipal, generarMapApartirEleccion_Regional, obtenerCentroides_Municipales, obtenerCentroides_Regionales, generarMap_dosificadores
from dash.exceptions import PreventUpdate
from flask import Flask
from app import *
from app import map_default_municipal
from app import map_default_regional
from app import map_dosificadores
from app import anios
from app import municipal_geo
from app import potabilizadoras
from app import purificadoras

import dash_ag_grid as dag

# Carga de datos y definición de variables
# shp_municipal = gpd.read_file("../assets/Datos/shp/Historicos_Acciones.shp")
# shp_regional = gpd.read_file("../assets/Datos/shp/Regional_.shp")
# shp_dosificadores = gpd.read_file("../assets/Datos/shp/Dosidicadores.shp")
# columns_list = shp_municipal.columns.tolist()
# opciones_cloro = [col for col in columns_list if 'CLORO' in col]
# anios = {i: re.sub(r"CLORO_", "", col) for i, col in enumerate(opciones_cloro)}

# map_default_municipal = funciones_auxiliares.generarMapApartirEleccion_Municipal(arhivo_sph=shp_municipal, lista_eleccion=opciones_cloro[-1])
# map_default_regional = funciones_auxiliares.generarMapApartirEleccion_Regional(arhivo_sph=shp_regional, lista_eleccion=opciones_cloro[-1])
# map_dosificadores = funciones_auxiliares.generarMap_dosificadores(arhivo_sph = shp_dosificadores)


#########################
### Paleta de colores ###
#########################

# Lógica de renderizado de GeoJSON en JavaScript
style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.hideout;
    const value = feature.properties[colorProp];
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];
        }
    }
    return style;
}""")


on_each_feature = assign("""function(feature, layer, context){
                        
                          
    const sesion = sessionStorage.getItem('current_map');
    const modo = JSON.parse(sesion);
    console.log("Mapa actual:", modo);  // Verificar el valor de modo en la consola

    if (modo === "municipal") {
        layer.bindTooltip(
         `
             <p> Municipio: <b>${feature.properties.NOM_MUN}</b> </p>
             <p> Cloro Residual Libre :<b> ${feature.properties["Valor-actual"] == -1 ? "No hay dato" : feature.properties["Valor-actual"]}</b> </p>
        `
        );
    }

    if (modo === "regional") {
        layer.bindTooltip(
         `
             <p> Region: <b>${feature.properties["Region"]}</b> </p>
             <p> Cloro Residual Libre :<b> ${feature.properties["Valor-actual"] == -1 ? "No hay dato" : feature.properties["Valor-actual"]}</b> </p>
        `
        );
    }

    if (modo === "pozo") {
        layer.bindTooltip(
         `
            <p> Fuente de Abastecimiento: <b> ${feature.properties["Fuente de abastecimiento"]} </b> </p>
            <p> Municipio :<b> ${feature.properties.NOM_MUN} </b> </p>
            <p> Localidad :<b> ${feature.properties.NOM_LOC} </b> </p> 
        `
        );
    }
}""")




on_each_feature_purificadoras = assign("""
    function(feature, layer){
        if (feature.properties){
            layer.bindTooltip(
            `
                <p> Municipio: <b> ${feature.properties.MUNICIPIO} </b> </p>
                <p> Localidad: <b> ${feature.properties.LOCALIDAD} </b> </p>
                <p> Fecha: <b> ${feature.properties.FECHA} </b> </p> 
            `
            );
            layer.bindPopup(
            `
                <p> Municipio: <b> ${feature.properties.MUNICIPIO} </b> </p>
                <p> Localidad: <b> ${feature.properties.LOCALIDAD} </b> </p>
                <p> Fecha: <b> ${feature.properties.FECHA} </b> </p> 
            `
            );
        }
    }
""")

on_each_feature_potabilizadoras = assign("""
    function(feature, layer){
        if (feature.properties){
            layer.bindTooltip(
            `
                <p> Municipio: <b> ${feature.properties.Municipio} </b> </p>
                <p> Localidad: <b> ${feature.properties.Localidad} </b> </p>
                <p> Fecha: <b> ${feature.properties.Fecha} </b> </p> 
            `
            );
                                         
            layer.bindPopup(
            `
                <p> Municipio: <b> ${feature.properties.Municipio} </b> </p>
                <p> Localidad: <b> ${feature.properties.Localidad} </b> </p>
                <p> Fecha: <b> ${feature.properties.Fecha} </b> </p> 
            `
            );
        }
    }
""")


# Clases para la paleta de colores
classes = [-2, -0.0000000001, 0.199999999999999999, 1.5]
CATEGORIAS_MUNICIPIO = [
    {"label": "No hay dato",        "color": "rgb(205,205,205)"},
    {"label": "CI < 0.2",           "color": "rgb(255,0,0)"},
    {"label": "0,2 <= CI <= 1.5",   "color": "rgb(112,173,71)"},
    {"label": "CI > 1.5",           "color": "rgb(255, 192, 0)"},
]
colorscale = ['rgb(205,205,205)', 'rgb(255,0,0)', 'rgb(112,173,71)', 'rgb(255, 192, 0)']
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

# Crea colorbar.
ctg = ["{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}+".format(classes[-1])]
colorbar = dlx.categorical_colorbar(
    categories=[cat["label"] for cat in CATEGORIAS_MUNICIPIO],  
    colorscale=colorscale,
    width=300,
    height=30,
    position="bottomleft",
    className="colorbar_custom"
)


#########################################
### Definimos parámetros interactivos ###
#########################################

# Creación de GeoJSON.
geojson = dl.GeoJSON(
    data=map_default_municipal,
    style=style_handle,
    onEachFeature=on_each_feature,
    zoomToBounds=False,
    zoomToBoundsOnClick=True,
    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
    hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="Valor-actual"),
    id="geojson"
)

CAPAS_PUNTUALES = [
    {
        "nombre": "Dosificadores de Cloro",
        "color": "yellow",
        "data": map_dosificadores,
        "on_each_feature": None,
        "checked": False,
    },
    {
        "nombre": "Purificadoras",
        "color": "red",
        "data": purificadoras,
        "on_each_feature": on_each_feature_purificadoras,
        "checked": False,
    },
    {
        "nombre": "Potabilizadores",
        "color": "blue",
        "data": potabilizadoras,
        "on_each_feature": on_each_feature_potabilizadoras,
        "checked": False,
    },
]

# Genera un dl.Overlay por cada capa registrada arriba.
overlays_puntuales = [
    dl.Overlay(
        children=[dl.GeoJSON(
            data=capa["data"],
            pointToLayer=funciones_auxiliares.crear_icono_color(capa["color"]),
            onEachFeature=capa["on_each_feature"],
        )],
        name=capa["nombre"],
        checked=capa["checked"],
    )
    for capa in CAPAS_PUNTUALES
]

############################################
### Definición de Componentes del Layout ###
############################################


encabezado = dbc.Row([
    dbc.Col(
        html.H2("Acciones de desinfección", style={'color': 'white', 'margin': '0', 'padding': '2vh 0 0 10px'}),
        width=6, xxl=6, xl=6, lg=6, md=6, sm=12, xs=12,
        style={'backgroundColor': 'rgb(157, 36, 73)', 'padding': '0', 'margin': '0'}
    ),
    dbc.Col(
        html.A(
            html.Img(src="./assets/Imagenes/Planeacion_dorado.png", style={'width': '100%', 'height': '60%', 'padding': '1vh 0 0 10px'}),
            href="http://sigeh.hidalgo.gob.mx/",
            target="_blank"
        ),
        width=3, xxl=3, xl=3, lg=3, md=3, sm=6, xs=6,
        style={'backgroundColor': 'rgb(157, 36, 73)', 'padding': '0', 'margin': '0'}
    ),
    dbc.Col(
        html.A(
            html.Img(src="./assets/Imagenes/CEAA_dorado.png", style={'width': '75%', 'height': '70%', 'padding': '1vh 0 0 10px'}),
            href="https://ceaa.hidalgo.gob.mx/",
            target="_blank"
        ),
        width=3, xxl=3, xl=3, lg=3, md=3, sm=6, xs=6,
        style={'backgroundColor': 'rgb(157, 36, 73)', 'padding': '0', 'margin': '0'}
    )
],
    style={"height": "12vh", 'width': '100vw', 'padding': '0', 'margin': '0'}
)




########################
### Botone Laterales ###
########################

layers_icon = html.I(id="layers_icon", className="bi bi-layers", style={'margin': '0', 'paddin': '0'})
search_icon = html.I(id="search_icon", className="bi bi-search", style={'margin': '0', 'paddin': '0'})
information_icon = html.I(id="about_information_icon", className="bi bi-book",  style={'margin': '0', 'paddin': '0'})
question_icon = html.I(id="question_icon", className="bi bi-question-lg",  style={'margin': '0', 'paddin': '0'})


botton_layers = dbc.Button(
    [layers_icon],
    id="botton_layers_icon",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom",
    style={'width': '70%', 'height': '6vh', 'margin': '1vh 10% 1vh 10%'}
)

botton_search = dbc.Button(
    [search_icon],
    id="botton_search_icon",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom",
    style={'width': '70%', 'height': '6vh', 'margin': '1vh 10% 1vh 10%'}
)

botton_information = dbc.Button(
    [information_icon],
    id="botton_information_icon",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom",
    style={'width': '70%', 'height': '6vh', 'margin': '1vh 10% 1vh 10%'}
)

botton_question = dbc.Button(
    [question_icon],
    id="botton_question_icon",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom",
    style={'width': '70%', 'height': '6vh', 'margin': '1vh 10% 1vh 10%'}
)


###########################
### Offcanvas and Modals###
###########################

########################
### OffCanvas Layers ###
########################

botton_municipal = dbc.Button(
    "Municipal",
    id= "botton_municipal",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom active",
    style={'width': '70%', 'height': '6vh', 'margin': '1vh 10% 1vh 10%'}
)

botton_regional = dbc.Button(
    "Regional",
    id= "botton_regional",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom",
    style={'width': '70%', 'height': '6vh', 'margin': '1vh 10% 1vh 10%'}
)

botton_pozo = dbc.Button(
    "Pozos",
    id= "botton_pozo",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom",
    style={'width': '70%', 'height': '6vh', 'margin': '1vh 10% 1vh 10%'}
)



slider_periodo = dcc.Slider(
    id="slider_periodo",
    step=None,
    marks=anios,
    value=list(anios.keys())[-1],
    className="slider-custom"
)

slider_periodo_pozos = dcc.Slider(
    id="slider_periodo_pozos",
    step=None,
    marks=anios_nh,
    value=list(anios_nh.keys())[-1],
    className="slider-custom-off",

)

play_pause_icon = html.I(id="play_pause", className="bi bi-play-fill")

botton_time = dbc.Button(
    ["Histórico", play_pause_icon],
    id="botton_time",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom",
    style={'width': '70%', 'height': '5vh', 'margin': '1vh 10% 1vh 10%'}
)

intervalo_tiempo = dcc.Interval(
    id="intervalo_tiempo",
    interval=2500,  # 1000 = 1s
    n_intervals=2024,  # Valor inicial
    disabled=True
)

intervalo_tiempo_pozos = dcc.Interval(
    id = "intervalo_tiempo_pozos",
    interval = 2500,
    n_intervals = 2012,
    disabled = True
)


offcanvas_layers = html.Div(
    [
        dbc.Offcanvas(
            children=[ 
                html.H5("Tipo de mapa", style={'color': 'black'}),
                html.Div( 
                    children= [ botton_municipal, botton_regional],
                    style={"display": "flex", "justifyContent": "space-around"}
                ),
                html.Div(
                    children= [botton_pozo],
                    style={"display": "flex", "justifyContent": "center"}
                ),
                html.Br(),
                html.H5("Periodo", style={'color': 'black'}),
                slider_periodo,
                slider_periodo_pozos,
                html.Br(),
                html.Br(),
                html.H5("Explora el tiempo", style={'color': 'black'}),
                botton_time,
                intervalo_tiempo,
                intervalo_tiempo_pozos
            ],
            id="offcanvas_layers",
            title= html.H4("Capas de información", style={'textAlign': 'center', 'color': 'black'}),
            is_open=False,
            backdrop=False,
            style={"height": "88vh", "marginTop": "12vh", "backgroundColor": " #c1c0c0"}
        ),
    ],
)



########################
### OffCanvas Search ###
########################


# Dropdown para buscar municipios o regiones según el mapa actual.
buscador = dcc.Dropdown(
    id='buscador',
    options=[{'label': mun, 'value': latitud} for mun, latitud in zip(municipal_geo.NOM_MUN, municipal_geo.latitud)],
    placeholder="Buscar:",
    clearable=False,
    className="buscador_custom"
)

offcanvas_search = html.Div(
    [
        dbc.Offcanvas( 
            children = [
                buscador
            ],
            id="offcanvas_search",
            title= html.H4("Busca tu municipio o región", style={'textAlign': 'center', 'color': 'black'}),
            is_open=False,
            backdrop=False,
            style={"height": "88vh", "marginTop": "12vh", "backgroundColor": " #c1c0c0"},
        ),
    ]
)




modal_information = dbc.Modal(children=[
    dbc.ModalHeader(dbc.ModalTitle("Información Adicional")),
    dbc.ModalBody([
        "La Norma Oficial Mexicana ",
        html.A("NOM-127-SSA1-2021", href="https://www.dof.gob.mx/nota_detalle_popup.php?codigo=5650705", target="_blank"),
        " establece los límites permitidos de calidad del agua para uso y consumo humano."
    ]),
    dbc.ModalFooter(
        dbc.Button("De Acuerdo", id="close_information", className="ms-auto", n_clicks=0)
    ),
],
    id="modal_information",
    is_open=False,
)

modal_content = [
    dbc.ModalHeader(
        dbc.ModalTitle("Explora el mapa")
    ),
    dbc.ModalBody(
        html.Div([
            html.P(
                "Este mapa web interactivo tiene una barra lateral en la parte izquierda con cuatro secciones principales:"
            ),
            html.Ol([
                html.Li([
                    html.Strong("Capas de Información:"),
                    html.Ul([
                        html.Li("Permite elegir el tipo de mapa a visualizar (municipal, regional o pozo)."),
                        html.Li("Incluye una línea de tiempo para seleccionar el año deseado."),
                        html.Li('Tiene un botón "Histórico" que cambia el mapa automáticamente cada 2.5 segundos para mostrar diferentes periodos.')
                    ])
                ]),
                html.Li([
                    html.Strong("Buscador:"),
                    html.Ul([
                        html.Li("Facilita buscar un municipio o una región, según el mapa que estés viendo."),
                        html.Li("Al buscar, el mapa se centra en el área seleccionada.")
                    ])
                ]),
                html.Li([
                    html.Strong("Información Adicional:"),
                    html.P("Ofrece detalles y explicaciones más específicas sobre los indicadores mostrados.")
                ]),
                html.Li([
                    html.Strong("Explora el Mapa:"),
                    html.P("Es la opción que has seleccionado para interactuar directamente con el mapa.")
                ])
            ]),
            html.P("Cada sección está diseñada para que puedas navegar y obtener la información que necesites de manera sencilla y visual.")
        ])
    )
]

modal_question = dbc.Modal(
    children=[
        *modal_content,
        dbc.ModalFooter(
            dbc.Button("De Acuerdo", id="close_question", className="ms-auto", n_clicks=0)
        ),
    ],
    id="modal_question",
    is_open=False,
)


##################################
### Barra vertical interactiva ###
##################################

vertical_nav = dbc.Nav(
    [
        dbc.NavLink(children = botton_layers, id="layers_nav", style = {'margin': '0', 'padding': '0'}),
        dbc.NavLink(children = botton_search, id="search_nav", style = {'margin': '0', 'padding': '0'}),
        dbc.NavLink(children = botton_information, id="information_nav", style = {'margin': '0', 'padding': '0'}),
        dbc.NavLink(children = botton_question, id="question_nav", style = {'margin': '0', 'padding': '0'})
    ],
    vertical=True,
    pills=True,
    style={
        "height": "100vh",
        'width': '6vw',
        "padding": "0",
        'margin': '0',
        'backgroundColor': 'rgb(179, 142, 93)'
    }
)


###############
### Lateral ###
###############

barra_lateral = html.Div(
    children= vertical_nav,
    id="barra_lateral",
    className="barra_lateral",
    style={
        "position": "absolute",
        "backgroundColor": "black",
        "height": "100vh", 
        'width': '6vw',
        "zIndex": "1000"
    },
)

# Mapa
mapa = dbc.Row(
    children=[
        dbc.Col(
            dl.Map(
                id="mapa",  # Id asignado para usar en callbacks
                children=[
                    dl.TileLayer(),
                    dl.LayersControl(
                        children=[dl.BaseLayer(children=[geojson], name="Cloro Residual Libre", checked=True)] + overlays_puntuales,
                        position="topright",
                        id="layers_control",
                        collapsed= False,  # Para que el control de capas esté expandido por defecto
                    ),
                    barra_lateral,
                    dl.ZoomControl(position="topleft"),
                ],
                center=[20.41509, -98.82936],  # Coordenadas iniciales
                zoom=9,
                viewport={"center": [20.41509, -98.82936], "zoom": 9},  # Cambiado a viewport
                zoomControl=False,
                style={'height': '88vh'}
            ),
            width=12, xxl=12, xl=12, lg=12, md=12, sm=12, xs=12,
            style={'backgroundColor': '#000000', 'padding': '0', 'margin': '0'}
        )
    ],
    style={"height": "88vh", 'width': '100vw', 'padding': '0', 'margin': '0'}
)



##############
### Layout ###
##############

simbologia_imagen = html.Div(
    [
        html.Div("Cloro Residual Libre", style={'color': 'black', 'fontSize': '12px', 'fontWeight': 'bold', 'marginBottom': '4px'}),
        *[
            html.Div(
                [
                    html.Div(style={
                        'width': '20px', 'height': '20px', 'marginRight': '6px',
                        'backgroundColor': cat["color"], 'border': '1px solid black',
                        'flexShrink': '0'
                    }),
                    html.Span(cat["label"], style={'color': 'black', 'fontSize': '12px'})
                ],
                style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '4px'}
            )
            for cat in CATEGORIAS_MUNICIPIO
        ],

        html.Div("Capas de puntos", style={'color': 'black', 'fontSize': '12px', 'fontWeight': 'bold', 'margin': '8px 0 4px 0'}),
        *[
            html.Div(
                [
                    html.Img(
                        src=f"https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-{capa['color']}.png",
                        style={'height': '20px', 'marginRight': '6px'}
                    ),
                    html.Span(capa["nombre"], style={'color': 'black', 'fontSize': '12px'})
                ],
                style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '4px'}
            )
            for capa in CAPAS_PUNTUALES
        ],
    ],
    style={
        'position': 'absolute',
        'bottom': '25px',
        'right': '10px',
        'zIndex': '1000',
        'backgroundColor': 'rgba(255, 255, 255, 0.8)',
        'padding': '8px 10px',
        'borderRadius': '6px'
    },
    className="simbologia_imagen_custom"
)

dash.register_page(__name__, 
                   path='/',
                   title='Acciones de desinfección')


#################################################
### Generar entonrnos de descarga y impresion ###
#################################################

### Municipal
popup_texto_municipio_municipal = html.P(id="popup_texto_municipio_municipal")
impresion_texto_municipio_municipal = html.P(id="impresion_texto_municipio_municipal")

popup_texto_numero_pozos_municipal = html.P(id="popup_texto_numero_pozos_municipal")
impresion_texto_numero_pozos_municipal = html.P(id="impresion_texto_numero_pozos_municipal")

popup_tabla_cloro_municipal = dag.AgGrid(
    id="popup_tabla_cloro_municipal",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "34vh", "width": "100%"}
)

impresion_tabla_cloro_municipal = dag.AgGrid(
    id="impresion_tabla_cloro_municipal",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "", "width": ""},
    dashGridOptions={"domLayout": "print"}
)

popup_tabla_dosificadores_municipal = dag.AgGrid(
    id="popup_tabla_dosificadores_municipal",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "30vh", "width": "100%"}
)

impresion_tabla_dosificadores_municipal = dag.AgGrid(
    id="impresion_tabla_dosificadores_municipal",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "", "width": "100%"},
    dashGridOptions={"domLayout": "print"}
)


popup_modal_municipal = dbc.Modal(
    [
        dbc.ModalHeader(popup_texto_municipio_municipal),
        dbc.ModalBody(children=[
            popup_tabla_cloro_municipal,
            html.P(children= "Acerca del municipio:"),
            popup_texto_numero_pozos_municipal,
            popup_tabla_dosificadores_municipal
            ]),
        dbc.ModalFooter(
            children=[
                dbc.Button(
                    [
                        html.I(className="bi bi-file-earmark-pdf-fill"),
                        html.Span(" Descargar PDF", id="descargar_municipal_texto"),
                    ],
                    id="descargar_municipal",
                    className="btn-download",
                    n_clicks=0,
                ),
                dbc.Button(
                    [html.I(className="bi bi-x-lg"), "Cerrar"],
                    id="close_popup_municipal",
                    className="btn-close-modal",
                    n_clicks=0,
                ),
            ],
            className="modal-footer-custom",
        ),
    ],
    id="popup_modal_municipal",
    size="xl",
    is_open=False
)

## Aqui estaba impresion_entorno_municipal

### regional
popup_texto_region_regional= html.P(id="popup_texto_region_regional")
impresion_texto_region_regional = html.P(id="impresion_texto_region_regional")

popup_texto_numero_pozos_regional = html.P(id="popup_texto_numero_pozos_regional")
impresion_texto_numero_pozos_regional = html.P(id="impresion_texto_numero_pozos_regional")

popup_tabla_cloro_regional = dag.AgGrid(
    id="popup_tabla_cloro_regional",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "34vh", "width": "100%"}
)

impresion_tabla_cloro_regional = dag.AgGrid(
    id="impresion_tabla_cloro_regional",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "", "width": ""},
    dashGridOptions={"domLayout": "print"}
)

popup_tabla_dosificadores_regional = dag.AgGrid(
    id="popup_tabla_dosificadores_regional",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "30vh", "width": "100%"}
)

impresion_tabla_dosificadores_regional = dag.AgGrid(
    id="impresion_tabla_dosificadores_regional",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "", "width": "100%"},
    dashGridOptions={"domLayout": "print"}
)

popup_modal_regional = dbc.Modal(
    [
        dbc.ModalHeader(popup_texto_region_regional),
        dbc.ModalBody(children=[
            popup_tabla_cloro_regional,
            html.P(children= "Acerca de la región:"),
            popup_texto_numero_pozos_regional,
            popup_tabla_dosificadores_regional
            ]),
        dbc.ModalFooter(
            children=[
                dbc.Button(
                    [
                        html.I(className="bi bi-file-earmark-pdf-fill"),
                        html.Span("Descargar PDF", id="descargar_regional_texto"),
                    ],
                    id="descargar_regional",
                    className="btn-download",
                    n_clicks=0,
                ),
                dbc.Button(
                    [html.I(className="bi bi-x-lg"), "Cerrar"],
                    id="close_popup_regional",
                    className="btn-close-modal",
                    n_clicks=0,
                ),
            ],
            className="modal-footer-custom",
        ),
    ],
    id="popup_modal_regional",
    size="xl",
    is_open=False
)

# Aqui estaba impresion_entorno_regional
### Pozo

popup_texto_localidad = html.P(id="popup_texto_localidad")
popup_texto_municicio = html.P(id="popup_texto_municipio")
popup_texto_region = html.P(id="popup_texto_region")
popup_texto_pozo = html.P(id="popup_texto_pozo")

impresion_texto_localidad = html.P(id="impresion_texto_localidad")
impresion_texto_municicio = html.P(id="impresion_texto_municipio")
impresion_texto_region = html.P(id="impresion_texto_region")    
impresion_texto_pozo = html.P(id="impresion_texto_pozo")


popup_tabla_pozo = dag.AgGrid(
    id="popup_tabla_pozo",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},
    style={"height": "50vh", "width": "100%"}
)

impresion_tabla_pozo = dag.AgGrid(
    id="impresion_tabla_pozo",
    rowData=[],
    columnDefs=[],
    defaultColDef={"flex": 1, "sortable": True, "filter": True},        
    style={"height": "", "width": ""},
    dashGridOptions={"domLayout": "print"}
)

popup_modal_pozo = dbc.Modal(
    [
        dbc.ModalHeader(popup_texto_pozo),
        dbc.ModalBody(children=[
                popup_texto_municicio,
                popup_texto_localidad,
                popup_texto_region,
                popup_tabla_pozo
            ]),
        dbc.ModalFooter(
                    children=[
                        dbc.Button(
                            [
                                html.I(className="bi bi-file-earmark-pdf-fill"),
                                html.Span("Descargar PDF", id="descargar_pozo_texto"),
                            ],
                            id="descargar_pozo",
                            className="btn-download",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            [html.I(className="bi bi-x-lg"), "Cerrar"],
                            id="close_popup_pozo",
                            className="btn-close-modal",
                            n_clicks=0,
                        ),
                    ],
                    className="modal-footer-custom",
                ),  
    ],
    id="popup_modal_pozo",
    size="xl",
    is_open=False
)

#Aqui estaba impresion_entorno_pozo
datos_descarga_store = dcc.Store(id="datos_descarga")
toast_descarga = dbc.Toast(
    "Tu reporte se descargó correctamente.",
    id="toast_descarga",
    header="Descarga completa",
    icon="success",
    is_open=False,
    dismissable=True,
    duration=3500,
    className="toast-descarga",
)



layout = dbc.Container([
    encabezado,
    mapa,
    offcanvas_layers,
    offcanvas_search,
    modal_information,
    modal_question,
    simbologia_imagen,
    popup_modal_municipal,
    #impresion_entorno_municipal,
    popup_modal_regional,
    #impresion_entorno_regional,
    popup_modal_pozo,
    #impresion_entorno_pozo,
    html.Div(id="dummy-print"),
    dcc.Store(id="current_map", data="municipal", storage_type="session"),  # Almacena el estado actual del mapa
    datos_descarga_store,
    toast_descarga
],
    fluid=True,
    style={'height': '100vh', 'width': '100vw', 'padding': '0', 'margin': '0'}
)
