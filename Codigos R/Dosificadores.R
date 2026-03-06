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

dosificadores |>  sf::write_sf("app/assets/Dosificadores.shp")

library(leaflet)

leaflet() |> 
  addTiles() |> 
  addMarkers(data = dosificadores)




