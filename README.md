# app.py

import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium

st.title("Visualizador de rutas GPX")

# Subir archivo GPX
gpx_file = st.file_uploader("Sube tu archivo GPX", type=["gpx"])

if gpx_file is not None:
    gpx = gpxpy.parse(gpx_file)

    # Extraer puntos
    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude))

    # Mostrar en mapa
    if coords:
        center = coords[len(coords)//2]
        mapa = folium.Map(location=center, zoom_start=13)
        folium.PolyLine(coords, color="red", weight=4).add_to(mapa)
        folium.Marker(coords[0], tooltip="Inicio").add_to(mapa)
        folium.Marker(coords[-1], tooltip="Fin").add_to(mapa)

        st.subheader("Vista de la ruta")
        st_folium(mapa, width=700, height=500)

