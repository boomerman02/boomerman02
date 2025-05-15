
import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
import time
import cv2
import numpy as np
from PIL import ImageGrab

st.title("Visualizador de rutas GPX con mapas, animación y vídeo")

modo = st.radio("Selecciona el modo de visualización", ["Ver ruta estática", "Ver animación", "Generar video"])

map_options = {
    "OpenStreetMap": "OpenStreetMap",
    "Stamen Terrain": "Stamen Terrain",
    "Stamen Toner": "Stamen Toner",
    "CartoDB Positron": "CartoDB positron",
    "CartoDB Dark": "CartoDB dark_matter"
}
tipo_mapa = st.selectbox("Selecciona el tipo de mapa base", list(map_options.keys()))

gpx_file = st.file_uploader("Sube tu archivo GPX", type=["gpx"])

def create_video_from_gpx(gpx_file, output_file, map_type="OpenStreetMap"):
    gpx = gpxpy.parse(gpx_file)

    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude))

    if not coords:
        raise ValueError("No coordinates found in the GPX file.")

    video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*"mp4v"), 1, (800, 600))

    for i in range(len(coords)):
        mapa = folium.Map(location=coords[i], zoom_start=13)
        folium.TileLayer(map_type).add_to(mapa)
        folium.PolyLine(coords[:i+1], color="red", weight=4).add_to(mapa)
        folium.CircleMarker(location=coords[i], radius=8, color="blue", fill=True).add_to(mapa)
        mapa.save("map.html")

        img = ImageGrab.grab(bbox=(0, 0, 800, 600))
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        video_writer.write(frame)

    video_writer.release()

if gpx_file is not None:
    gpx = gpxpy.parse(gpx_file)

    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude))

    if coords:
        if modo == "Ver ruta estática":
            mapa = folium.Map()
            folium.TileLayer(map_options[tipo_mapa]).add_to(mapa)
            folium.PolyLine(coords, color="red", weight=4).add_to(mapa)
            folium.Marker(location=coords[0], tooltip="Inicio").add_to(mapa)
            folium.Marker(location=coords[-1], tooltip="Fin").add_to(mapa)
            mapa.fit_bounds(coords)

            st.subheader("Vista de la ruta completa")
            st_folium(mapa, width=700, height=500)

        elif modo == "Ver animación":
            st.write("Simulación de movimiento sobre la ruta.")

            for i in range(0, len(coords), max(1, len(coords)//30)):
                mapa = folium.Map(location=coords[i], zoom_start=13)
                folium.TileLayer(map_options[tipo_mapa]).add_to(mapa)
                folium.PolyLine(coords, color="red", weight=4).add_to(mapa)
                folium.CircleMarker(location=coords[i], radius=8, color="blue", fill=True).add_to(mapa)
                st_folium(mapa, width=700, height=500)
                time.sleep(0.2)

        elif modo == "Generar video":
            st.write("Generando video de la ruta...")
            output_file = "output_video.mp4"
            create_video_from_gpx(gpx_file, output_file, map_options[tipo_mapa])
            st.success("Vídeo generado correctamente.")
            st.video(output_file)
