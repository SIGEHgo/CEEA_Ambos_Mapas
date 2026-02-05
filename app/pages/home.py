import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import geopandas as gpd

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

# Clases para la paleta de colores
classes = [-2, -0.0000000001, 0.199999999999999999, 1.5]
colorscale = ['rgb(205,205,205)', 'rgb(255,0,0)', 'rgb(112,173,71)', 'rgb(255, 192, 0)']
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

# Crea colorbar.
ctg = ["{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}+".format(classes[-1])]
colorbar = dlx.categorical_colorbar(
    categories=["No hay dato", "CI < 0.2", "0,2 <= CI <= 1.5", "CI > 1.5"],
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
    zoomToBounds=False,
    zoomToBoundsOnClick=True,
    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
    hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="Valor-actual"),
    id="geojson"
)

geojson_dosificadores = dl.GeoJSON(
    data=map_dosificadores
)
############################################
### Definición de Componentes del Layout ###
############################################

map_icon = html.I(id="map_icon", className="bi bi-map", style={'margin': '0', 'paddin': '0'})
botton_map= dbc.Button(
    [map_icon],
    id="navigate-button",
    color="primary",
    n_clicks=0,
    size="sm",
    outline=True,
    className="button-custom-map",
    style={'width': '70%', 'height': '6vh', 'margin': '1vh 10% 1vh 10%'}
)

tooltip_map = dbc.Tooltip(
    "Abre el mapa de Indicadores de Calidad del Agua en una nueva ventana",  # Texto que se muestra
    target="navigate-button",   # Debe coincidir con el id del botón
    placement="top"              
)

encabezado = dbc.Row([
    dbc.Col(
        html.H2("Acciones de desinfección", style={'color': 'white', 'margin': '0', 'padding': '2vh 0 0 10px'}),
        width=6, xxl=6, xl=6, lg=6, md=6, sm=12, xs=12,
        style={'backgroundColor': 'rgb(157, 36, 73)', 'padding': '0', 'margin': '0'}
    ),
    dbc.Col(
        html.A(
            html.Img(src="./assets/Imagenes/Planeacion_dorado.png", style={'width': '100%', 'height': '70%', 'padding': '1vh 0 0 10px'}),
            href="http://sigeh.hidalgo.gob.mx/",
            target="_blank"
        ),
        width=3, xxl=3, xl=3, lg=3, md=3, sm=6, xs=6,
        style={'backgroundColor': 'rgb(157, 36, 73)', 'padding': '0', 'margin': '0'}
    ),
    dbc.Col(
        html.A(
            html.Img(src="./assets/Imagenes/CEAA_dorado.png", style={'width': '75%', 'height': '75%', 'padding': '1vh 0 0 10px'}),
            href="https://ceaa.hidalgo.gob.mx/",
            target="_blank"
        ),
        width=2, xxl=2, xl=2, lg=2, md=2, sm=5, xs=5,
        style={'backgroundColor': 'rgb(157, 36, 73)', 'padding': '0', 'margin': '0'}
    ),
    dbc.Col(
            children= [botton_map,tooltip_map,
                       html.P("Explora otro mapa", style={'color': 'white', 'margin': '0', 'padding': '0vh 0 0vh 10%', 'fontSize': '11px'})],
            width = 1,
            xxl = 1, xl = 1, lg = 1, md = 1, sm = 1,  xs = 1, 
            style = {'backgroundColor': '#9C2448', 'padding': '0', 'margin':'0'}
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

slider_periodo = dcc.Slider(
    id="slider_periodo",
    step=None,
    marks=anios,
    value=list(anios.keys())[-1],
    className="slider-custom"
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


offcanvas_layers = html.Div(
    [
        dbc.Offcanvas(
            children=[ 
                html.H5("Tipo de mapa", style={'color': 'black'}),
                html.Div( 
                    children= [ botton_municipal, botton_regional],
                    style={"display": "flex", "justifyContent": "space-around"}
            ),
                html.Br(),
                html.H5("Periodo", style={'color': 'black'}),
                slider_periodo,
                html.Br(),
                html.Br(),
                html.H5("Explora el tiempo", style={'color': 'black'}),
                botton_time,
                intervalo_tiempo
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
        " establece que el agua de uso y consumo humano debe presentar una concentración de cloro residual libre entre 0.2 y 1.5mg/L."
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
                        html.Li("Permite elegir el tipo de mapa a visualizar (municipal o regional)."),
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




# modal_popup = [
#     dbc.ModalHeader(
#         dbc.ModalTitle("Nombre del municipio")
#     ),
#     dbc.ModalBody(
#         html.Div([
#             html.Ol([
#                 html.Li([
#                     html.Strong("Cloro Residual Libre:"),
#                     html.Ul([
#                         html.Li("2020:"),
#                         html.Li("2021:"),
#                         html.Li('2022:'),
#                         html.Li('2023:'),
#                     ])
#                 ]),
#             ]),
#             html.P("Numero de pozos en ese municipio: X", propierties),
#             html.P("Numero de dosificadores en ese municipio: X"),
#             html.P("Nombre de dosificadores: X"),
#             html.P("Localidad donde se encuentra el dosificador: X"),
#             html.P("Año de instalación de dosificadores: X"),
#         ])
#     )
# ]


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
                        children=[
                            dl.BaseLayer(children=[geojson], name="Cloro Residual Libre", checked=True),
                            dl.Overlay(children=[geojson_dosificadores], name="Dosificadores de Cloro", checked=False),
                        ],
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
    html.Img(src="assets/Imagenes/simbologia_corel.png", style={'width': 'auto', 'height': '24vh', 'margin': '0 0 0 0'}),
    style={
        'position': 'absolute',
        'bottom': '25px',
        'right': '10px',
        'zIndex': '1000'
    },
    className="simbologia_imagen_custom"
)

dash.register_page(__name__, 
                   path='/',
                   title='Acciones de desinfección')


layout = dbc.Container([
    dcc.Location(id='url', refresh=True),
    encabezado,
    mapa,
    offcanvas_layers,
    offcanvas_search,
    modal_information,
    modal_question,
    
    
    simbologia_imagen,
    dcc.Store(id="current_map", data="municipal"),  # Almacena el estado actual del mapa
],
    fluid=True,
    style={'height': '100vh', 'width': '100vw', 'padding': '0', 'margin': '0'}
)
