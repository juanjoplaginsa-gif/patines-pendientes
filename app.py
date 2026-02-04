import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Control de Pendientes BIRK", layout="wide")

# Enlace directo a tu CSV de Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS9mEVGhFL6d_wC49GEz52Z3Hrb1wf-cGqYxEUrZPIiTI7nJ0KLEjYw0YqBCqPYP3yMfPx8h79RRjS7/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=10) # Se actualiza casi al instante
def load_data():
    try:
        # Forzamos la lectura sin caché si hay problemas
        df = pd.read_csv(SHEET_URL)
        # Limpiar nombres de columnas (quitar espacios y poner en mayúsculas)
        df.columns = df.columns.str.strip().str.upper()
        # Convertir a números
        if 'TOTAL PATINES' in df.columns:
            df['TOTAL PATINES'] = pd.to_numeric(df['TOTAL PATINES'], errors='coerce').fillna(0)
        if 'PENDIENTES' in df.columns:
            df['PENDIENTES'] = pd.to_numeric(df['PENDIENTES'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None

df = load_data()

if df is not None:
    st.title("👡 Control de Producción - BIRK")

    # --- FILTROS ---
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por OC
    col_oc = 'ORDEN DE COMPRA'
    ocs = ["Todas"] + sorted(df[col_oc].dropna().unique().astype(str).tolist())
    oc_selected = st.sidebar.selectbox("Filtrar por OC:", ocs)

    # Filtrar datos
    df_filtered = df.copy()
    if oc_selected != "Todas":
        df_filtered = df_filtered[df_filtered[col_oc] == oc_selected]

    # --- MÉTRICAS ---
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Programado", f"{int(df_filtered['TOTAL PATINES'].sum()):,}")
    with c2:
        st.metric("Pendientes Reales", f"{int(df_filtered['PENDIENTES'].sum()):,}")

    # --- FORMATO DE COLORES (COMO EN TU EXCEL) ---
    def apply_style(row):
        # Verde si pendientes es 0
        if row['PENDIENTES'] == 0:
            return ['background-color: #92d050; color: black'] * len(row)
        # Gris si tiene pendientes (mayor a 0)
        elif row['PENDIENTES'] > 0:
            return ['background-color: #bfbfbf; color: black'] * len(row)
        return [''] * len(row)

    st.subheader("📋 Detalle de la Hoja PENDIENTES")
    st.dataframe(
        df_filtered.style.apply(apply_style, axis=1),
        use_container_width=True,
        hide_index=True
    )

    if st.button("🔄 Refrescar Datos"):
        st.cache_data.clear()
        st.rerun()
else:
    st.warning("No se pudieron cargar los datos. Revisa que el Google Sheet esté publicado correctamente.")
