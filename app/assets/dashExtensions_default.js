window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, layer, context) {
            layer.bindTooltip(
                `
            <p><b>Municipio:</b> ${feature.properties.NOM_MUN}</p>
            `
            );
        }

    }
});