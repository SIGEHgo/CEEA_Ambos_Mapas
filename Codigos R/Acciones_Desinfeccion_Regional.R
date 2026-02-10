datos = "app/assets/Acciones_de_desinfeccion_municipal.geojson" |>  sf::read_sf()

orden = names(datos)

datos = datos |> 
  dplyr::mutate(
    dplyr::across(
      .cols = CLORO_2020:CLORO_2024,
      .fns = ~ dplyr::if_else(condition = .x == "-1", true = NA, false = .x)
    ),
    CVE_MUN = paste0("13", CVE_MUN) |>  stringr::str_squish(),
    dplyr::across(
      .cols = CLORO_2020:CLORO_2024,
      .fns = ~ .x |>  as.numeric()
    )
  )






datos = datos |> 
  sf::st_drop_geometry() |> 
  dplyr::group_by(Región) |> 
  dplyr::summarise(
    
    dplyr::across(
      .cols = c(CVE_MUN, NOM_MUN, Dosificadores_localidad:Dosificadores_marca),
      .fns = ~ paste(.x, collapse = ", ")
    ),
    
    dplyr::across(
      .cols = CLORO_2020:CLORO_2024,
      .fns = ~ mean(.x, na.rm = T)
    ),
    
    dplyr::across(
      .cols = c(Pozos_Municipio, Dosificadores_municipio),
      .fns = ~ sum(.x, na.rm = T)
    )
    
  ) |> 
  dplyr::ungroup()



datos = datos |> 
  dplyr::mutate(
    dplyr::across(
      .cols = Dosificadores_localidad:Dosificadores_marca,
      .fns =  ~ .x |>  gsub(pattern = "No hay dosificadores,", replacement = "") |>  
        gsub(pattern = "No hay dosificadores", replacement = "") |> 
        gsub(pattern = ",\\s*$", replacement = "") |> 
        stringr::str_squish()
    ),
    dplyr::across(
      .cols = Dosificadores_localidad:Dosificadores_marca,
      .fns =  ~ dplyr::if_else(condition = .x == "", true = "No hay dosificadores", false = .x)
    )
  )



datos = datos |> 
  dplyr::select(
    dplyr::any_of(orden)
  )

datos = datos |> 
  dplyr::mutate(
    dplyr::across(
      .cols = CLORO_2020:CLORO_2024,
      .fns = ~ dplyr::if_else(condition = is.na(.x), true = -1, false = .x)
      )
  )

geometrias = sf::read_sf("app/assets/Datos/shp/Regional_.shp")
geometrias = geometrias |> 
  dplyr::select(Región,geometry)

datos = datos |> 
  dplyr::mutate(
    Región = Región |>  gsub(pattern = "Región", replacement = "") |> stringr::str_squish() 
    ) |> 
  dplyr::left_join(y = geometrias, by = c("Región" = "Región"))


datos = datos |>  sf::st_as_sf()

datos |>  sf::write_sf("app/assets/Acciones_de_desinfeccion_regional.geojson")
