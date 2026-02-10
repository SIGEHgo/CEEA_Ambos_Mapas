pozos = "app/assets/Pozos.geojson" |>  sf::read_sf()

library(leaflet)

geom_spatraster_rgb(data = maptiles::get_tiles(st_bbox(rutas_comparacion))) +
  
  geom_spatvector(data = terra::vect(rutas_comparacion), 
                  aes(color = servicio, linetype = servicio), 
                  linewidth = 1.2) +
  
  geom_spatvector(data = terra::vect(punto_referencia_fijo |> st_transform(4326)), 
                  color = "black", fill = "yellow", shape = 23, size = 4) +
  
  scale_color_manual(values = setNames(
    c("#E41A1C", "#377EB8", "#4DAF4A", "#FF7F00"),
    c(label_sigeh, label_osm, label_mapbox, label_google)
  )) +
  scale_linetype_manual(values = setNames(
    c("solid", "dashed", "solid", "dashed"),
    c(label_sigeh, label_osm, label_mapbox, label_google)
  )) +
  
  labs(
    title = "Comparativa de Rutas y Tiempos Estimados",
    caption = 
  ) +
  theme_minimal() +
  theme(legend.position = "bottom",
        legend.box.background = element_rect(color = "black", linewidth = 0.3))


prueba = pozos[1,]
prueba = prueba |>  sf::st_buffer(dist = units::set_units(50, "m"))


raster::plot(maptiles::get_tiles(x = sf::st_bbox(prueba)))
