import dash_leaflet as dl
from dash_extensions.enrich import DashProxy, Input, Output, html
from dash_extensions.javascript import assign
from dash_extensions.javascript import arrow_function


on_each_feature = assign("""
                                          
function(feature, layer, context){
                         
    layer.bindTooltip(
        feature.properties["Fuente de abastecimiento"]
    );

    layer.bindPopup(
        `
        <h4><b>Fuente de abastecimiento:</b> ${feature.properties["Fuente de abastecimiento"]}</h4>
        <p><b>Municipio:</b> ${feature.properties.NOM_MUN}</p>
        <p><b>Localidad:</b> ${feature.properties.NOM_LOC}</p>
        `
    );
                                   
}
""")



geojson = dl.GeoJSON(
    url="assets/Pozos.geojson",
    zoomToBounds=True,  
    onEachFeature=on_each_feature,
    id="geojson-pozos",  
)


app = DashProxy(prevent_initial_callbacks=True)

app.layout = html.Div(
    [
        dl.Map(
            children=[dl.TileLayer(), geojson],
            style={"height": "90vh"},
            center=[20, -98], 
            zoom=6
        ),
        html.Div(id="clic"),
    ],
    style={"height": "100vh"}
)

@app.callback(Output("clic", "children"), [Input("geojson-pozos", "clickData")])
def clic_click(feature):
    if feature is not None:
        return f"You clicked {feature['properties']['Fuente de abastecimiento']}"

if __name__ == "__main__":
    app.run(debug=True)