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

pozos = pozos |> 
  dplyr::mutate(
    ID = paste(NOM_MUN, NOM_LOC, `Fuente de abastecimiento`,sep = "_") |>  stringr::str_squish()
  ) |> 
  dplyr::relocate(ID, .before = geometry)


pozos |>  sf::write_sf("app/assets/Pozos.geojson")


