import dash_leaflet as dl
from dash_extensions.enrich import DashProxy
from dash_extensions.javascript import assign


on_each_feature = assign("""
function(feature, layer, context){
    console.lo                     

    layer.bindTooltip(
        feature.properties.NOM_MUN
    );

    layer.bindPopup(
        `
        <h4><b>Municipio:</b> ${feature.properties.NOM_MUN}</h4>
        <p><b>Cloro 2020:</b> ${feature.properties.CLORO_2020}</p>
        <p><b>Cloro 2021:</b> ${feature.properties.CLORO_2021}</p>
        <p><b>Cloro 2022:</b> ${feature.properties.CLORO_2022}</p>
        <p><b>Cloro 2023:</b> ${feature.properties.CLORO_2023}</p>
        <p><b>Numero de pozos en ese municipio:</b> ${feature.properties.Pozos_Municipio}</p>
        <p><b>Numero de dosificadores en ese municipio:</b> ${feature.properties.Dosificadores_municipio}</p>                 
        <p><b>Nombre de dosificador:</b> ${feature.properties.Dosificadores_nombres}</p>
        <p><b>Localidad donde se encuentra el dosificador:</b> ${feature.properties.Dosificadores_localidad}</p>
        <p><b>Año de instalación de dosificadores:</b> ${feature.properties.Dosificadores_anios}</p>
        `
    );
}
""")



geojson = dl.GeoJSON(
    url="assets/Acciones_de_desinfeccion_municipal.geojson",
    zoomToBounds=True,  
    onEachFeature=on_each_feature,  
)


app = DashProxy(prevent_initial_callbacks=True)
app.layout = dl.Map([dl.TileLayer(), geojson], style={"height": "100vh"}, center=[20, -98], zoom=6)

if __name__ == "__main__":
    app.run(debug=True)