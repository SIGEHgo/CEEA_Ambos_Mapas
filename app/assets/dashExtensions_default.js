window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            const flag = L.icon({
                iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png`,
                shadowUrl: `https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png`,
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });
            return L.marker(latlng, {
                icon: flag
            });
        },
        function1: function(feature, context) {
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
        function2: function(feature, layer, context) {


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
        },
        function3: function(feature, layer) {
                if (feature.properties) {
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

            ,
        function4: function(feature, layer) {
                if (feature.properties) {
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

            ,
        function5: function(feature, latlng) {
            const flag = L.icon({
                iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png`,
                shadowUrl: `https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png`,
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });
            return L.marker(latlng, {
                icon: flag
            });
        },
        function6: function(feature, latlng) {
            const flag = L.icon({
                iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png`,
                shadowUrl: `https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png`,
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });
            return L.marker(latlng, {
                icon: flag
            });
        },
        function7: function(feature, latlng) {
            const flag = L.icon({
                iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png`,
                shadowUrl: `https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png`,
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });
            return L.marker(latlng, {
                icon: flag
            });
        }
    }
});