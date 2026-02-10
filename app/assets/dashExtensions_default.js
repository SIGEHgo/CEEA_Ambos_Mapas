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
            layer.bindTooltip(
                `
            <p><b>Municipio:</b> ${feature.properties.NOM_MUN}</p>
            <p><b>Valor:</b> ${feature.properties["Valor-actual"]}</p>`
            );
        }
    }
});