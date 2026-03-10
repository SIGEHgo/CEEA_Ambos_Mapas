potabilizadoras = "Input/2026/PLANTAS POTABILIZADORAS PARA PEQUEÑAS POBLACIONES (1) (1).xlsx" |>  readxl::read_excel()

potabilizadoras = potabilizadoras |> 
  dplyr::select(-...14)

potabilizadoras |>  names() = potabilizadoras[1,]

potabilizadoras = potabilizadoras |> 
  dplyr::select(`Id. Nr`, FECHA, MUNICIPIO, LOCALIDAD, X, Y) |> 
  dplyr::slice(-1) |>  
  dplyr::mutate(
    X = X |>  as.numeric(),
    Y = Y |>  as.numeric(),
    FECHA = FECHA |>  as.numeric() |>   as.Date(origin = "1899-12-30") |>  as.character()
  ) |> 
  sf::st_as_sf(coords = c("X", "Y"), remove = T,  na.fail = T, crs = 32614) |> 
  sf::st_transform(crs = 4326) 


potabilizadoras = potabilizadoras |> 
  dplyr::mutate(
    FECHA = paste0(
      FECHA |>  stringr::word(start = 3,sep = "-"),
      "/",
      FECHA |>  stringr::word(start = 2,sep = "-"),
      "/",
      FECHA |>  stringr::word(start = 1,sep = "-")
      ) |>  stringr::str_squish()
    )





mun = "../../Importantes_documentos_usar/Municipios/municipiosjair.shp" |>  
  sf::read_sf() |>  
  sf::st_drop_geometry() |> 
  dplyr::select(NOM_MUN)


comparar = fuzzyjoin::stringdist_join(
  x = potabilizadoras |> sf::st_drop_geometry() |>  
    dplyr::select(MUNICIPIO) |>  
    dplyr::mutate(
      mun = MUNICIPIO |>  tolower() |>  stringr::str_squish()
      ),
  y = mun,
  by = c("mun" = "NOM_MUN"),
  ignore_case = F,
  method = "jw",
  max_dist = 1,
  distance_col = "dist"
) |> 
  dplyr::group_by(mun)  |> 
  dplyr::slice_min(order_by = dist, n = 1) |> 
  dplyr::filter(dist > 0) |>  
  dplyr::arrange(dist) |> 
  unique()



for (i in 1:nrow(comparar)) {
  cat(
    'MUNICIPIO == "',
    comparar$MUNICIPIO[i],
    '" ~ "',
    comparar$NOM_MUN[i],
    '", \n',
    sep = ""
  )
}



potabilizadoras = potabilizadoras |> 
  dplyr::mutate(
    MUNICIPIO = dplyr::case_when(
      MUNICIPIO == "TIANGUISTENGO" ~ "Tianguistengo", 
      MUNICIPIO == "TLAHUILTEPA" ~ "Tlahuiltepa", 
      MUNICIPIO == "TENANGO DE DORIA" ~ "Tenango de Doria", 
      MUNICIPIO == "CALNALI" ~ "Calnali", 
      MUNICIPIO == "HUAUTLA" ~ "Huautla", 
      MUNICIPIO == "ELOXOCHITLAN" ~ "Eloxochitlán", 
      MUNICIPIO == "METZTITLAN" ~ "Metztitlán", 
      MUNICIPIO == "HUEHUETLA" ~ "Huehuetla", 
      T ~ MUNICIPIO
    ),
    LOCALIDAD = LOCALIDAD |>  stringr::str_to_title()
  ) |> 
  dplyr::rename(
    Localidad = LOCALIDAD,
    Municipio = MUNICIPIO,
    Fecha = FECHA
    ) 



potabilizadoras |>  sf::write_sf("app/assets/Potabilizadoras.geojson")



library(leaflet)
leaflet() |> 
  addTiles() |> 
  addMarkers(data = potabilizadoras)
