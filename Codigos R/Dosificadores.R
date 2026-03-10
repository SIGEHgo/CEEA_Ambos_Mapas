ejemplo = "app/assets/Datos/shp/Dosidicadores.shp" |>  sf::read_sf()


dosificadores = "Input/2026/HISTÓRICO BOMBAS DOSIFICADORAS .xlsx" |> readxl::read_excel()

dosificadores |>  names() = dosificadores[2,]

dosificadores = dosificadores |> 
  dplyr::filter(!is.na(No)) |> 
  dplyr::slice(-1)

dosificadores = dosificadores |> 
  dplyr::select(-No) |> 
  dplyr::mutate(
    `Gasto de agua` = `Gasto de agua` |>  tolower() |>  gsub(pattern = "l/s",  replacement = "") |>  stringr::str_squish()  |>  as.numeric()
  )


dosificadores = dosificadores |> 
  dplyr::mutate(
    `Coordenada Y` = Coordenadas |> stringr::str_split_i(pattern = ",", i = 1),
    `Coordenada X` = Coordenadas |> stringr::str_split_i(pattern = ",", i = 2),
    Año = Año |>  as.numeric(),
    Locacion = Locacion |>  gsub(pattern = "pozo", replacement = "Pozo") |> 
      gsub(pattern = "cabecera", replacement = "Cabecera") |>  
      gsub(pattern = "Mpal", replacement = "Municipal") |> 
      stringr::str_squish()
  ) |> 
  sf::st_as_sf(coords = c("Coordenada X", "Coordenada Y"), crs = 4326, remove = T, na.fail = F) |> 
  dplyr::select(Municipio, Locacion, Año, Estado, `Gasto de agua`, Marca, Modelo)



dosificadores = dosificadores |> 
  dplyr::mutate(
    dplyr::across(
      .cols = where(is.character),
      .fns = ~ .x |>  stringr::str_squish()
    )
  )

dosificadores |>  names() = c("Municip", "Locacin", "Año", "estado", "Gastdag", "Marca", "Modelo", "geometry")
dosificadores |> names() = dosificadores |>  names() |>  stringr::str_squish()





mun = "../../Importantes_documentos_usar/Municipios/municipiosjair.shp" |>  
  sf::read_sf() |>  
  sf::st_drop_geometry() |> 
  dplyr::select(NOM_MUN)


comparar = fuzzyjoin::stringdist_join(
  x = dosificadores |>  dplyr::select(Municip),
  y = mun,
  by = c("Municip" = "NOM_MUN"),
  ignore_case = F,
  method = "jw",
  max_dist = 0.5,
  distance_col = "dist"
) |> 
  dplyr::group_by(Municip)  |> 
  dplyr::slice_min(order_by = dist, n = 1) |> 
  dplyr::filter(dist > 0) |>  
  dplyr::arrange(dist)


for (i in 1:nrow(comparar)) {
  cat(
    'Municip == "',
    comparar$Municip[i],
    '" ~ "',
    comparar$NOM_MUN[i],
    '", \n',
    sep = ""
  )
}


dosificadores = dosificadores |> 
  dplyr::mutate(
    Municip = dplyr::case_when(
      Municip == "San Felipe Orizatlan" ~ "San Felipe Orizatlán", 
      Municip == "Tepetitlan" ~ "Tepetitlán", 
      Municip == "Tepetitlan" ~ "Tepetitlán", 
      Municip == "San Agustin Metzquititlan" ~ "San Agustín Metzquititlán", 
      Municip == "Tepeji del Rio" ~ "Tepeji del Río de Ocampo",
      T ~ Municip 
    )
  )



dosificadores |>  sf::write_sf("app/assets/Dosificadores.shp", delete_layer = T)

library(leaflet)

leaflet() |> 
  addTiles() |> 
  addMarkers(data = dosificadores)




