datos = "app/assets/Acciones_de_desinfeccion_municipal.geojson" |>  sf::read_sf()

cloro = datos |>  sf::st_drop_geometry() |> 
  dplyr::filter(NOM_MUN == "Metepec") |> 
  dplyr::select(CLORO_2020:CLORO_2024)

cloro = cloro |> 
  tidyr::pivot_longer(
    cols = CLORO_2020:CLORO_2024,
    names_to = "Año"
  )

cloro = cloro |> 
  dplyr::mutate(
    Año = Año |>  gsub(pattern = "CLORO_", replacement = "") |>  stringr::str_squish(),
    limite = dplyr::case_when(
      value >= 0.2 & value <= 1.5 ~ "Limite permisible",
      TRUE ~ "Fuera del limite permisible"
    )
  )





  
  
  
dosificadores = datos |>  sf::st_drop_geometry() |> 
  dplyr::filter(NOM_MUN == "Metepec") |> 
  dplyr::select(Dosificadores_localidad:Dosificadores_gasto_agua)



dosificadores = dosificadores |> 
  tidyr::separate_rows(
    Dosificadores_localidad:Dosificadores_gasto_agua,
    sep = ","
  ) |> 
  dplyr::mutate(
    dplyr::across(
      .cols = Dosificadores_localidad:Dosificadores_gasto_agua,
      .fns =  ~ .x |>  stringr::str_squish()
    )
  )
