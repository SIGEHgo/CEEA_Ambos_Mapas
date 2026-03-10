purificadoras = "Input/2026/PLANTAS PURIFICADORAS SOLARES_RESGUARDOS (1).xlsx" |>  
  readxl::read_excel()

purificadoras = purificadoras |> 
  dplyr::select(...28:...34)

purificadoras |>  names() = purificadoras[1,]


purificadoras = purificadoras |> 
  dplyr::filter(!is.na(X)) |> 
  dplyr::slice(-1) |> 
  sf::st_as_sf(coords = c("X","Y"), remove = T,   na.fail = T, crs = 32614) |> 
  sf::st_transform(crs = 4326)



mun = "../../Importantes_documentos_usar/Municipios/municipiosjair.shp" |>  
  sf::read_sf() |>  
  sf::st_drop_geometry() |> 
  dplyr::select(NOM_MUN)


comparar = fuzzyjoin::stringdist_join(
  x = purificadoras |> sf::st_drop_geometry() |>  
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
  dplyr::group_by(MUNICIPIO)  |> 
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


purificadoras = purificadoras |> 
  dplyr::mutate(
    MUNICIPIO = dplyr::case_when(
      MUNICIPIO == "XOCHIATIPAN" ~ "Xochiatipan", 
      MUNICIPIO == "YAHUALICA" ~ "Yahualica", 
      MUNICIPIO == "TIZAYUCA" ~ "Tizayuca", 
      MUNICIPIO == "JUAREZ HIDALGO" ~ "Juárez Hidalgo", 
      MUNICIPIO == "NICOLAS FLORES" ~ "Nicolás Flores", 
      MUNICIPIO == "IXMIQUILPAN" ~ "Ixmiquilpan", 
      MUNICIPIO == "JACALA" ~ "Ajacuba", 
      MUNICIPIO == "ZACUALTIPAN" ~ "Zacualtipán de Ángeles",
      T ~ MUNICIPIO
    ),
    LOCALIDAD = LOCALIDAD |>  stringr::str_to_title() |>  stringr::str_squish(),
    FECHA = FECHA |>  as.numeric() |>   as.Date(origin = "1899-12-30") |>  as.character() 
  )


purificadoras = purificadoras |> 
  dplyr::mutate(
    FECHA = paste0(
      FECHA |>  stringr::word(start = 3,sep = "-"),
      "/",
      FECHA |>  stringr::word(start = 2,sep = "-"),
      "/",
      FECHA |>  stringr::word(start = 1,sep = "-")
    ) |>  stringr::str_squish()
  ) |> 
  dplyr::select(MUNICIPIO, LOCALIDAD, FECHA)


purificadoras |>  sf::write_sf("app/assets/Purificadoras.geojson")




