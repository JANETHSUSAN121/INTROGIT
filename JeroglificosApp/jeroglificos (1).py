import streamlit as st
import pandas as pd
import requests
import io

# URL raw de tu Excel en GitHub
url = "https://github.com/JANETHSUSAN121/INTROGIT/raw/main/profesiones_jeroglificos.xlsx"

# Función para cargar los datos con caching
@st.cache_data
def cargar_datos():
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Esto lanzará un error si falla la descarga
        df = pd.read_excel(io.BytesIO(respuesta.content))
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

df = cargar_datos()

# Configuración de la página
st.set_page_config(page_title="Diccionario de Profesiones", layout="wide")

st.title("Diccionario de Profesiones en Jeroglíficos 🏺")
st.markdown("Selecciona una profesión para ver su jeroglífico, transliteración y descripción.")

# Inicializar selección
if "seleccion" not in st.session_state:
    st.session_state["seleccion"] = None

# Crear dos columnas: galería y panel de detalles
galeria_col, detalles_col = st.columns([3, 2])

# Galería de tarjetas (2 tarjetas por fila)
num_cols = 2
tarjetas = galeria_col.columns(num_cols)

for idx, fila in df.iterrows():
    col = tarjetas[idx % num_cols]
    with col:
        # Mostrar imagen si existe en tu Excel
        if "Imagen" in df.columns and pd.notna(fila["Imagen"]):
            st.image(fila["Imagen"], width=150)
        # Botón para seleccionar profesión
        if st.button(fila["profesion"], key=idx):
            st.session_state["seleccion"] = idx

# Mostrar detalles de la profesión seleccionada
if st.session_state["seleccion"] is not None and not df.empty:
    fila = df.loc[st.session_state["seleccion"]]
    detalles_col.subheader(f"{fila['profesion']}")
    detalles_col.markdown(f"**Jeroglífico:** {fila['jeroglifico']}")
    detalles_col.markdown(f"**Transliteración:** {fila['transliteracion']}")
    detalles_col.markdown(f"**Descripción:** {fila['descripcion']}")
    # Mostrar imagen grande si existe
    if "Imagen" in df.columns and pd.notna(fila["Imagen"]):
        detalles_col.image(fila["Imagen"], use_column_width=True)



 
