import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
import time

st.title("Visualizador de rutas GPX con mapas y animación")

# Modo de visualización
modo = st.radio("Selecciona el modo de visualización", ["Ver ruta estática", "Ver animación"])

# Selector de tipo de mapa
map_options = {
    "OpenStreetMap": "OpenStreetMap",
    "Stamen Terrain": "Stamen Terrain",
    "Stamen Toner": "Stamen Toner",
    "CartoDB Positron": "CartoDB positron",
    "CartoDB Dark": "CartoDB dark_matter",
    "Google Maps (requiere API Key)": "Google"
}
tipo_mapa = st.selectbox("Selecciona el tipo de mapa base", list(map_options.keys()))

# API Key de Google Maps (opcional)
google_api_key = st.text_input("Introduce tu Google Maps API Key (si elegiste Google Maps)", type="password")

# Subida de archivo GPX
gpx_file = st.file_uploader("Sube tu archivo GPX", type=["gpx"])

if gpx_file is not None:
    gpx = gpxpy.parse(gpx_file)

    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude))

    if coords:
        # Calcular el centro de las coordenadas
        center = [sum(x) / len(x) for x in zip(*coords)]

        if modo == "Ver ruta estática":
            mapa = folium.Map(location=center, zoom_start=13)
            selected_tile = map_options[tipo_mapa]

            if selected_tile == "Google":
                if not google_api_key:
                    st.error("Introduce tu API Key de Google Maps para usar este mapa.")
                else:
                    folium.TileLayer(
                        tiles=f"https://mt1.google.com/vt/lyrs=r&x={{x}}&y={{y}}&z={{z}}&key={google_api_key}",
                        attr="Google",
                        name="Google Maps",
                        overlay=False,
                        control=True
                    ).add_to(mapa)
            else:
                folium.TileLayer(selected_tile).add_to(mapa)

            folium.PolyLine(coords, color="red", weight=4).add_to(mapa)
            folium.Marker(coords, tooltip="Inicio").add_to(mapa)
            folium.Marker(coords[-1], tooltip="Fin").add_to(mapa)

            st.subheader("Vista de la ruta")
            st_folium(mapa, width=700, height=500)

        elif modo == "Ver animación":
            st.write("Simulación de movimiento sobre la ruta (experimental).")

            # Crear un mapa centrado en el punto de inicio
            mapa = folium.Map(location=coords, zoom_start=13)
            selected_tile = map_options[tipo_mapa]

            if selected_tile == "Google":
                if not google_api_key:
                    st.error("Introduce tu API Key de Google Maps para usar este mapa.")
                else:
                    folium.TileLayer(
                        tiles=f"https://mt1.google.com/vt/lyrs=r&x={{x}}&y={{y}}&z={{z}}&key={google_api_key}",
                        attr="Google",
                        name="Google Maps",
                        overlay=False,
                        control=True
                    ).add_to(mapa)
            else:
                folium.TileLayer(selected_tile).add_to(mapa)

            folium.PolyLine(coords, color="red", weight=4).add_to(mapa)
            marker = folium.CircleMarker(location=coords, radius=8, color="blue", fill=True)
            marker.add_to(mapa)

            # Mostrar el mapa inicial
            map_placeholder = st.empty()
            map_placeholder.write(st_folium(mapa, width=700, height=500))

            # Actualizar la posición del marcador para simular el movimiento
            for i in range(1, len(coords)):
                mapa = folium.Map(location=coords[i], zoom_start=13)
                if selected_tile == "Google":
                    folium.TileLayer(
                        tiles=f"https://mt1.google.com/vt/lyrs=r&x={{x}}&y={{y}}&z={{z}}&key={google_api_key}",
                        attr="Google",
                        name="Google Maps",
                        overlay=False,
                        control=True
                    ).add_to(mapa)
                else:
                    folium.TileLayer(selected_tile).add_to(mapa)

                folium.PolyLine(coords, color="red", weight=4).add_to(mapa)
                marker = folium.CircleMarker(location=coords[i], radius=8, color="blue", fill=True)
                marker.add_to(mapa)

                map_placeholder.write(st_folium(mapa, width=700, height=500))
                time.sleep(0.2)
