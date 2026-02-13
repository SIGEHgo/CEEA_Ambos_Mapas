window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.hideout;
            const value = feature.properties[colorProp];
            for (let i = 0; i < classes.length; ++i) {
                if (value > classes[i]) {
                    style.fillColor = colorscale[i];
                }
            }
            return style;
        },
        function1: function(feature, layer, context) {


            const sesion = sessionStorage.getItem('current_map');
            const modo = JSON.parse(sesion);
            console.log("Mapa actual:", modo); // Verificar el valor de modo en la consola

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
             <p> Cloro Residual Libre :<b> ${feature.properties["Valor-actual"]} </b> </p>
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
        },
        function2: function(feature, latlng) {
            const flag = L.icon({
                iconUrl: `assets/Imagenes/No hay dato_gota.png`,
                iconSize: [45, 35]
            });
            return L.marker(latlng, {
                icon: flag
            });
        }
    }
});