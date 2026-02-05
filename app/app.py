import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import geopandas as gpd
import os
import dash_bootstrap_components as dbc  # Importa Dash Bootstrap Components
from dash import Dash, html, Output, Input, State, no_update,dcc
import re
from dash_extensions.javascript import arrow_function, assign
import geopandas as gpd
import funciones_auxiliares
from funciones_auxiliares import generarMapApartirEleccion_Municipal, generarMapApartirEleccion_Regional, obtenerCentroides_Municipales, obtenerCentroides_Regionales, generarMap_dosificadores
from dash.exceptions import PreventUpdate
from flask import Flask


##Cargamos variables de la segunda pagina:
archivos = os.listdir("./assets/Datos/Mapas/") 
archivos_html = [f for f in archivos if f.endswith(".html")]

anios_nh = [re.sub(r"\.html", "", i) for i in archivos_html]
anios_nh = [re.sub(r"Mapa_", "", i) for i in anios_nh]
anios_nh = sorted(anios_nh, key=lambda x: int(x)) # Ordenamos
anios_nh = {i: anio for i, anio in enumerate(anios_nh)}
print(anios_nh)
# anios_nh=0
# archivos_html = [os.path.join("./assets/Datos/Mapas/", f) for f in archivos_html]



#Carga de datos y definición de variables
shp_municipal = gpd.read_file("./assets/Datos/shp/Historicos_Acciones.shp")
shp_regional = gpd.read_file("./assets/Datos/shp/Regional_.shp")
shp_dosificadores = gpd.read_file("./assets/Datos/shp/Dosidicadores.shp")
columns_list = shp_municipal.columns.tolist()
opciones_cloro = [col for col in columns_list if 'CLORO' in col]
anios = {i: re.sub(r"CLORO_", "", col) for i, col in enumerate(opciones_cloro)}

map_default_municipal = funciones_auxiliares.generarMapApartirEleccion_Municipal(arhivo_sph=shp_municipal, lista_eleccion=opciones_cloro[0])
map_default_regional = funciones_auxiliares.generarMapApartirEleccion_Regional(arhivo_sph=shp_regional, lista_eleccion=opciones_cloro[0])
map_dosificadores = funciones_auxiliares.generarMap_dosificadores(arhivo_sph = shp_dosificadores)

municipal_geo = funciones_auxiliares.obtenerCentroides_Municipales(shp_municipal)
print(len(municipal_geo.latitud.unique()))
regional_geo = funciones_auxiliares.obtenerCentroides_Regionales(shp_regional)


server = Flask(__name__)

app = dash.Dash(__name__,server, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP,"assets/Style.css"],use_pages=True)
app.layout = html.Div([
    dash.page_container,

])
# app.layout = dbc.Container([
#     dash.page_container,
#     encabezado,
#     mapa,
#     offcanvas_layers,
#     offcanvas_search,
#     modal_information,
#     modal_question,
#     simbologia_imagen,
#     dcc.Store(id="current_map", data="municipal"),  # Almacena el estado actual del mapa
# ],
#     fluid=True,
#     style={'height': '100vh', 'width': '100vw', 'padding': '0', 'margin': '0'}
# )


#####################################
### CallBacks Model and OffCanvas ###
######################################


### offcanvas_layers
@app.callback(
    Output("offcanvas_layers", "is_open"),
    [Input("botton_layers_icon", "n_clicks")],
    [State("offcanvas_layers", "is_open")]
)
def offcanvas_layers_open(n1, is_open):
    if n1:
        return not is_open
    return is_open


### offcanvas_search
@app.callback(
    Output("offcanvas_search", "is_open"),
    [Input("botton_search_icon", "n_clicks")],
    [State("offcanvas_search", "is_open")]
)
def offcanvas_layers_open(n1, is_open):
    if n1:
        return not is_open
    return is_open

### modal_information
@app.callback(
    Output("modal_information", "is_open"),
    [Input("botton_information_icon", "n_clicks"), Input("close_information", "n_clicks")],
    [State("modal_information", "is_open")]
)
def modal_information_open(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


### modal_question
@app.callback(
    Output("modal_question", "is_open"),
    [Input("botton_question_icon", "n_clicks"), Input("close_question", "n_clicks")],
    [State("modal_question", "is_open")]
)
def modal_question_open(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open



# Callback para cambiar el mapa entre municipal y regional ademas de cambiar el color del botón activo
@app.callback(
    [
        Output("geojson", "data", allow_duplicate=True),
        Output("current_map", "data"),
        Output("botton_municipal", "className"),
        Output("botton_regional", "className"),
        Output("buscador", "options")
    ],
    [
        Input("botton_municipal", "n_clicks"),
        Input("botton_regional", "n_clicks")
    ],
    State("current_map", "data"),
    State("slider_periodo","value"),
    prevent_initial_call=True  # evita que se dispare automáticamente al cargar
)
def toggle_active(mun_clicks, reg_clicks, current_map,valor_actual_slider):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    clicked = ctx.triggered[0]["prop_id"].split(".")[0]

    if clicked == "botton_municipal":
        # Se genera el mapa para el caso municipal
        new_data = funciones_auxiliares.generarMapApartirEleccion_Municipal(
            arhivo_sph=shp_municipal, lista_eleccion=opciones_cloro[valor_actual_slider]
        )
        opciones = [{'label': mun, 'value': latitud} 
                    for mun, latitud in zip(municipal_geo.NOM_MUN, municipal_geo.latitud)]
        return new_data, "municipal", "button-custom active", "button-custom", opciones

    elif clicked == "botton_regional":
        # Se genera el mapa para el caso regional
        new_data = funciones_auxiliares.generarMapApartirEleccion_Regional(
            arhivo_sph=shp_regional, lista_eleccion=opciones_cloro[valor_actual_slider]
        )
        opciones = [{'label': mun, 'value': lat} 
                    for mun, lat in zip(regional_geo.Región, regional_geo.latitud)]
        return new_data, "regional", "button-custom", "button-custom active", opciones

    raise PreventUpdate




# Callback para actualizar el mapa según el slider
@app.callback(
    Output("geojson", "data", allow_duplicate=True),
    [Input("slider_periodo", "value")],
    State("current_map", "data"),
    prevent_initial_call=True
)
def actualizar_mapa_por_slider(indice, current_map):
    columna = opciones_cloro[indice]
    if current_map == "municipal":
        map_default = funciones_auxiliares.generarMapApartirEleccion_Municipal(
            arhivo_sph=shp_municipal, lista_eleccion=columna)
    else:
        map_default = funciones_auxiliares.generarMapApartirEleccion_Regional(
            arhivo_sph=shp_regional, lista_eleccion=columna)
    return map_default



# Callback para hacer que funcione el botón de play/pause y el intervalo de tiempo
@app.callback(
    [Output("intervalo_tiempo", "disabled"),
     Output("play_pause", "className"),
     Output("botton_time", "className")],  
    [Input("botton_time", "n_clicks"),
     Input("botton_time", "className")],
    State("intervalo_tiempo", "disabled")
)
def intervalo_tiempo_activar_desactivar(numero_clicks, disabled, clase):
    print(f"Clicks: {numero_clicks}, Disabled: {disabled}")
    if not numero_clicks or numero_clicks == 0:
        return True, "bi bi-play-fill", "button-custom"  
    if numero_clicks % 2 == 1:
        return False, "bi bi-pause-fill", "button-custom active"  
    else:
        return True, "bi bi-play-fill", "button-custom"  


# Callback para mover el slider automáticamente
@app.callback(
    Output("slider_periodo", "value"),
    Input("intervalo_tiempo", "n_intervals"),
    State("slider_periodo", "value")
)
def moverse_automaticamente(n_intervals, valor_actual):
    total_anios = len(opciones_cloro)
    nuevo_valor = (valor_actual + 1) % total_anios
    return nuevo_valor

# Callback para centrar el mapa al seleccionar un municipio o región desde el dropdown
@app.callback(
    Output("mapa", "viewport"),
    Input("buscador", "value"),
    State("current_map", "data"),
    prevent_initial_call=True
)
def update_map(latitud, current_map):
    if latitud is None:
        raise PreventUpdate

    if current_map == "municipal":
        # Filtra el DataFrame para encontrar el municipio seleccionado
        municipio = municipal_geo[municipal_geo["latitud"] == latitud]
        if municipio.empty:
            raise PreventUpdate
        longitud = float(municipio.longitud.iloc[0])
    else:
        # Filtra el DataFrame para encontrar la región seleccionada
        region = regional_geo[regional_geo["latitud"] == latitud]
        if region.empty:
            raise PreventUpdate
        longitud = float(region.longitud.iloc[0])

    # Actualiza el viewport del mapa con la nueva ubicación
    return {"center": [latitud, longitud], "zoom": 12}


@app.callback(
    dash.dependencies.Output('url', 'href'),
    [dash.dependencies.Input('navigate-button', 'n_clicks')]
)
def navigate(n_clicks):
    if n_clicks:
        return '/Indicadores_de_Calidad_del_Agua'
    return dash.no_update
@app.callback(
    dash.dependencies.Output('url2', 'href'),
    [dash.dependencies.Input('navigate-button2', 'n_clicks')]
)
def navigate2(n_clicks):
    if n_clicks:
        return '/'
    return dash.no_update
#################
### Copilador ###
#################
@app.callback(
    Output("mapa_nh", "src"),
    Input("slider_periodo_nh", "value")
)
def actualizar_mapa(value):
    direccion_mapa = f"/assets/Datos/Mapas/Mapa_{anios_nh[value]}.html"
    #print(direccion_mapa)
    return direccion_mapa


if __name__ == '__main__':
    app.run(debug=True)
