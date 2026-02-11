import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import geopandas as gpd
import pandas as pd
import os
import dash_bootstrap_components as dbc  # Importa Dash Bootstrap Components
from dash import Dash, html, Output, Input, State, no_update,dcc, ctx
import re
from dash_extensions.javascript import arrow_function, assign
import geopandas as gpd
import funciones_auxiliares
from funciones_auxiliares import generarMapApartirEleccion_Municipal, generarMapApartirEleccion_Regional, obtenerCentroides_Municipales, obtenerCentroides_Regionales, generarMap_dosificadores
from dash.exceptions import PreventUpdate
from flask import Flask

import dash_ag_grid as dag






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
shp_municipal = gpd.read_file("./assets/Acciones_de_desinfeccion_municipal.geojson")
shp_regional = gpd.read_file("./assets/Acciones_de_desinfeccion_regional.geojson")
shp_dosificadores = gpd.read_file("./assets/Datos/shp/Dosidicadores.shp")
geojson_pozo = gpd.read_file("./assets/Pozos.geojson")

columns_list = shp_municipal.columns.tolist()
opciones_cloro = [col for col in columns_list if 'CLORO' in col]
anios = {i: re.sub(r"CLORO_", "", col) for i, col in enumerate(opciones_cloro)}

map_default_municipal = funciones_auxiliares.generarMapApartirEleccion_Municipal(geojson=shp_municipal, lista_eleccion=opciones_cloro[0])
map_default_regional = funciones_auxiliares.generarMapApartirEleccion_Regional(geojson=shp_regional, lista_eleccion=opciones_cloro[0])
map_default_pozo = funciones_auxiliares.generarMapApartirEleccion_Pozo(geojson=geojson_pozo, lista_eleccion= anios_nh[11])
map_dosificadores = funciones_auxiliares.generarMap_dosificadores(arhivo_sph = shp_dosificadores)

#print(map_default_municipal)

municipal_geo = funciones_auxiliares.obtenerCentroides_Municipales(shp_municipal)
print(len(municipal_geo.latitud.unique()))
regional_geo = funciones_auxiliares.obtenerCentroides_Regionales(shp_regional)


server = Flask(__name__)

app = dash.Dash(__name__,server, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP,"assets/Style.css"],use_pages=True)
app.layout = html.Div([
    dash.page_container
])



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
        Output("botton_pozo", "className"),
        Output("buscador", "options"),
        Output("slider_periodo", "className"),
        Output("slider_periodo_pozos", "className"),
        Output("current_map", "data", allow_duplicate=True),
        #Output("geojson", "onEachFeature")
    ],
    [
        Input("botton_municipal", "n_clicks"),
        Input("botton_regional", "n_clicks"),
        Input("botton_pozo", "n_clicks"),
    ],
    State("current_map", "data"),
    State("slider_periodo","value"),
    State("slider_periodo_pozos","value"),
    prevent_initial_call=True  # evita que se dispare automáticamente al cargar
)
def toggle_active(mun_clicks, reg_clicks, pozo_clicks, current_map, valor_actual_slider, valor_actual_slider_pozos):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    clicked = ctx.triggered[0]["prop_id"].split(".")[0]

    if clicked == "botton_municipal":
        # Se genera el mapa para el caso municipal
        new_data = funciones_auxiliares.generarMapApartirEleccion_Municipal(
            geojson=shp_municipal, lista_eleccion=opciones_cloro[valor_actual_slider]
        )
        opciones = [{'label': mun, 'value': latitud} 
                    for mun, latitud in zip(municipal_geo.NOM_MUN, municipal_geo.latitud)]
        return new_data, "municipal", "button-custom active", "button-custom", "button-custom", opciones, "slider-custom", "slider-custom-off", "municipal"#, on_each_feature_municipio

    elif clicked == "botton_regional":
        # Se genera el mapa para el caso regional
        new_data = funciones_auxiliares.generarMapApartirEleccion_Regional(
            geojson=shp_regional, lista_eleccion=opciones_cloro[valor_actual_slider]
        )
        opciones = [{'label': mun, 'value': lat} 
                    for mun, lat in zip(regional_geo.Región, regional_geo.latitud)]
        return new_data, "regional", "button-custom", "button-custom active", "button-custom", opciones, "slider-custom", "slider-custom-off", "regional"#, on_each_feature_region
    elif clicked == "botton_pozo":
        # Se genera el mapa para el caso pozo
        new_data = funciones_auxiliares.generarMapApartirEleccion_Pozo(
            geojson=geojson_pozo, lista_eleccion=anios_nh[valor_actual_slider_pozos]
        )
        opciones = [{'label': mun, 'value': latitud} 
                    for mun, latitud in zip(municipal_geo.NOM_MUN, municipal_geo.latitud)]
        return new_data, "pozo", "button-custom", "button-custom", "button-custom active", opciones, "slider-custom-off", "slider-custom", "pozo"#, on_each_feature_pozo
    raise PreventUpdate




# Callback para actualizar el mapa según el slider
@app.callback(
    Output("geojson", "data", allow_duplicate=True),
    [Input("slider_periodo", "value"),
     Input("slider_periodo_pozos", "value")],
    State("current_map", "data"),
    prevent_initial_call=True
)
def actualizar_mapa_por_slider(indice, indice_pozos, current_map):
    if current_map != "pozo":
        columna = opciones_cloro[indice]
    else:
        columna = anios_nh[indice_pozos]

    if current_map == "municipal":
        map_default = funciones_auxiliares.generarMapApartirEleccion_Municipal(
            geojson=shp_municipal, lista_eleccion=columna)
    elif current_map == "regional":
        map_default = funciones_auxiliares.generarMapApartirEleccion_Regional(
            geojson=shp_regional, lista_eleccion=columna)
    elif current_map == "pozo":        
        map_default = funciones_auxiliares.generarMapApartirEleccion_Pozo(
            geojson=geojson_pozo, lista_eleccion=columna)
    return map_default






# Callback para hacer que funcione el botón de play/pause y el intervalo de tiempo
@app.callback(
    [Output("intervalo_tiempo", "disabled"),
     Output("intervalo_tiempo_pozos", "disabled"),
     Output("play_pause", "className"),
     Output("botton_time", "className")],  
    [Input("botton_time", "n_clicks"),
     Input("botton_time", "className")],
    State("intervalo_tiempo", "disabled"),
    State("current_map", "data"),
)
def intervalo_tiempo_activar_desactivar(numero_clicks, clase, disabled, current_map):
    if not numero_clicks or numero_clicks == 0:
        return True, True, "bi bi-play-fill", "button-custom"  
    if numero_clicks % 2 == 1:
        return False, False, "bi bi-pause-fill", "button-custom active"  
    else:
        return True, True, "bi bi-play-fill", "button-custom"  
    





# Callback para mover el slider automáticamente
@app.callback(
    Output("slider_periodo", "value"),
    Output("slider_periodo_pozos", "value"),
    Input("intervalo_tiempo", "n_intervals"),
    Input("intervalo_tiempo_pozos", "n_intervals"),
    State("slider_periodo", "value"),
    State("slider_periodo_pozos", "value"),
    State("current_map", "data"),
)
def moverse_automaticamente(n_intervals, n_intervals_pozos, valor_actual, valor_actual_pozos, current_map):
    if current_map != "pozo":
        total_anios = len(opciones_cloro)
        nuevo_valor = (valor_actual + 1) % total_anios
        return nuevo_valor, valor_actual_pozos
    else:
        total_anios_pozos = len(anios_nh)
        nuevo_valor_pozos = (valor_actual_pozos + 1) % total_anios_pozos
        return valor_actual, nuevo_valor_pozos

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

    if current_map != "regional":
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
    Output("popup_modal_pozo", "is_open"),

    Output("popup_texto_localidad", "children"),
    Output("popup_texto_municipio", "children"),
    Output("popup_texto_region", "children"),
    Output("popup_texto_pozo", "children"),

    Output("popup_tabla_pozo", "rowData"),
    Output("popup_tabla_pozo", "columnDefs"),

    Input("geojson", "clickData"),
    Input("close_popup_pozo", "n_clicks"),
    Input("geojson", "n_clicks"),
    State("popup_modal_pozo", "is_open"),
    State("current_map", "data"),
)
def toggle_popup_pozo(feature, close_clicks, n_clicks, is_open, current_map):

    trigger_id = ctx.triggered_id
    print("El trigger id es: ", trigger_id)

    if trigger_id == "geojson" and feature and current_map == "pozo":
        print("Si se esta ejecutando el callback del popup")
        properties = feature["properties"]
        pozo_id = properties.get("ID")
        
        abastecimiento = properties.get("Fuente de abastecimiento", "N/A")
        nom_municipio = properties.get("NOM_MUN", "N/A")
        nom_localidad = properties.get("NOM_LOC", "N/A")

        
        df_filtro = geojson_pozo[geojson_pozo["ID"] == pozo_id].drop(columns=["geometry"], errors='ignore')
        columnas_eliminar = ["CVEGEO_LOC", "ID", "NOM_MUN", "NOM_LOC", "Fuente de abastecimiento"]
        df_filtro = df_filtro.drop(columns=columnas_eliminar, errors='ignore')

        df_filtro = df_filtro.T.reset_index()
        df_filtro.columns = df_filtro.iloc[0]
        df_filtro = df_filtro.iloc[1:]
        
       

        return (True, nom_localidad, f"Municipio: {nom_municipio}", "", f"Fuente de Abastecimiento: {abastecimiento}", df_filtro.to_dict('records'), [{"field": i} for i in df_filtro.columns])
    
    elif trigger_id == "close_popup_pozo":
        return (False, no_update, no_update, no_update, no_update, no_update, no_update)
    
    return (is_open, no_update, no_update, no_update, no_update, no_update, no_update)

   



if __name__ == '__main__':
    app.run(debug=True)
