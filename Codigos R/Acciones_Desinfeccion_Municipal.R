pozos= "app/assets/Datos/shp/Nivel_Pozo/Datos_2012_2023_RandomPuntos.shp" |>  sf::read_sf()


pozos = pozos |> 
  dplyr::rename(
    NOM_LOC = NOMGEO_LOC,
    `Fuente de abastecimiento` = f_abast,
    `Coliformes Totales (Ausencia o Presencia/100mL)` = coli_total,
    `E. Coli (Ausencia o Presencia/100mL)` = e_coli,
    `Arsenico (mg/L)` = as,
    `Bario (mg/L)` = ba,
    `Cadmio (mg/L)` = cd,
    `Cobre (mg/L)` = cu,
    `Hierro (mg/L)` = fe,
    `Manganeso (mg/L)` = mn,
    `Plomo (mg/L)` = pb,
    `Zinc (mg/L)` = zn,
    `Cianuros (mg/L)` = cn,
    `Cloro Residual (mg/L)` = cl_res,
    `Cloruros (mg/L)` = cl,
    `Dureza Total (mg/L)` = dur,
    `Fluoruros (mg/L)` = flu,
    `Nitratos (mg/L)` = no3,
    `Nitritos (mg/L)` = no2,
    `Ph` = ph,
    `SDT (mg/L)` = sdt,
    `Sulfatos (mg/L)` = so4,
    `Cloro Total (mg/L)` = cl_tot,
    `Conductividad (muS/cm)` = cond,
    `Temperatura (°C)` = temp
  )

names(pozos) = names(pozos) |> stringr::str_squish()

pozos_conteo = pozos |> 
  dplyr::select(CVEGEO_LOC, NOM_MUN,`Fuente de abastecimiento`) |>  
  unique()|>  sf::st_drop_geometry() |> dplyr::group_by(NOM_MUN) |>  
  dplyr::summarise(Pozos_Municipio = dplyr::n()) |>  dplyr::ungroup()



  


cloro = "app/assets/Datos/shp/Historicos_Acciones.shp" |>  sf::read_sf()
dosificadores = "app/assets/Datos/shp/Dosidicadores.shp" |>  sf::read_sf()

loc = "../../Importantes_documentos_usar/Localidades/shp1/13l.shp" |>  
  sf::read_sf() |>  
  sf::st_transform(crs = 4326) |> 
  dplyr::select(CVEGEO, NOMGEO)


dosificadores = dosificadores |>  sf::st_join(y = loc, join = sf::st_nearest_feature)
dosificadores = dosificadores |> 
  dplyr::select(-CVEGEO) |> 
  dplyr::rename(NOM_LOC= NOMGEO)



dosificadores_conteo = dosificadores |> sf::st_drop_geometry() |> 
  dplyr::group_by(Municip) |>  
  dplyr::summarise(
    Dosificadores_municipio = dplyr::n(),
    Dosificadores_localidad = paste(NOM_LOC, collapse = ", "),
    Dosificadores_locacion = paste(Locacin, collapse = ", "),
    Dosificadores_anios = paste(Año, collapse = ", "),
    Dosificadores_marca = paste(Marca, Modelo, collapse = ", ", sep = ": "),
    Dosificadores_gasto_agua = paste(Gastdag, collapse = ", ")
    ) |>  
  dplyr::ungroup() |> 
  dplyr::mutate(Dosificadores_locacion = Dosificadores_locacion |>  stringr::str_squish())


cloro = cloro |> 
  dplyr::left_join(y = pozos_conteo, by = c("NOM_MUN" = "NOM_MUN")) |> 
  dplyr::left_join(y = dosificadores_conteo, by = c("NOM_MUN" = "Municip"))

cloro = cloro |> 
  dplyr::relocate(geometry, .after = dplyr::last_col())


cloro = cloro |>
  dplyr::mutate(
    Dosificadores_municipio = dplyr::if_else(
      condition = is.na(Dosificadores_municipio),
      true = 0,
      false = Dosificadores_municipio
    ),
    dplyr::across(
      Dosificadores_localidad:Dosificadores_marca,
      ~ dplyr::if_else(
        condition = is.na(.x),
        true = "No hay dosificadores",
        false = .x
      )
    )
  )




info = "../../Importantes_documentos_usar/Banco de datos infografias _Eduardo.xlsx" |>  readxl::read_excel()
info = info |>  dplyr::filter(!is.na(Región)) |> 
  dplyr::select(Municipio, Región, `Zona Metropolitana`)


cloro = cloro |> 
  dplyr::left_join(y = info, by = c("NOM_MUN" = "Municipio"))

cloro = cloro |> 
  dplyr::relocate(Región, `Zona Metropolitana`, .after = NOM_MUN)

cloro = cloro |> 
  dplyr::mutate(
    Pozos_Municipio = dplyr::if_else(condition = is.na(Pozos_Municipio), true = 0, false = Pozos_Municipio),
    Dosificadores_gasto_agua = dplyr::if_else(condition = is.na(Dosificadores_gasto_agua), true = "No hay dosificadores", false = Dosificadores_gasto_agua)
  )


cloro |>  sf::write_sf("app/assets/Acciones_de_desinfeccion_municipal.geojson", delete_dsn = TRUE)


prueba = "../../../../Acciones_de_desinfeccion_municipal.geojson" |>  sf::read_sf()


leaflet() |>  addTiles() |>  addMarkers(data = dosificadores, label = dosificadores$Locacin) |> 
  addPolygons(data = loc, label = loc$NOMGEO)
