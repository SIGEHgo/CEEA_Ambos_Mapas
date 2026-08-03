### `Input`

La carpeta `Input` contiene los archivos originales proporcionados por la **CEAA**. Los únicos archivos que forman parte de esta fuente son:

- Los archivos de Excel ubicados directamente en la raíz de la carpeta.
- La carpeta `2026`.

La carpeta `Filtrados` probablemente proviene de otro repositorio de GitHub. No se tiene certeza su origen, ya que este proyecto no se encontraba completamente organizado al momento de su revisión. Por ello, se recomienda utilizar únicamente los archivos mencionados anteriormente como fuente oficial de entrada.

### `Outputs`

La carpeta `Outputs` contiene los archivos procesados y depurados. Estos son los archivos finales utilizados para la visualización en el mapa web.

Asimismo, estos mismos archivos también se encuentran disponibles dentro de la carpeta `assets`, ya que son los que consume directamente la aplicación.

## Nota

Dentro del archivo GeoJSON correspondiente a los pozos existe una columna llamada `id`. Este identificador se genera con el siguiente formato:

```text
NombreDelMunicipio_NombreLocalidad_NombreDelPozo
```

Este campo permite identificar de manera única cada pozo dentro del conjunto de datos. Ademas que recordemos que la posicion de los pozos fue generado de manera aleatoria dentro del poligono que cae dentro, asi que es una forma de mantener discreción sobre este mapa web, ademas que la CEAA no tenia la georeferenciación exacta del pozo.