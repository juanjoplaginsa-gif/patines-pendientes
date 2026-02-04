import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Control BIRK", layout="wide")

# Enlace de tu Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS9mEVGhFL6d_wC49GEz52Z3Hrb1wf-cGqYxEUrZPIiTI7nJ0KLEjYw0YqBCqPYP3yMfPx8h79RRjS7/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # LIMPIEZA CRÍTICA: Quitamos espacios en blanco de los nombres de las columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Convertir a número las columnas importantes
        for col in ['TOTAL PATINES', 'PENDIENTES']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

df = load_data()

if df is not None:
    st.title("👡 Control de Producción - BIRK")

    # Identificar nombres de columnas reales para evitar errores
    col_oc = 'ORDEN DE COMPRA' if 'ORDEN DE COMPRA' in df.columns else df.columns[5] if len(df.columns)>5 else None
    col_pen = 'PENDIENTES' if 'PENDIENTES' in df.columns else df.columns[-1]

    # --- FILTROS ---
    st.sidebar.header("🔍 Filtros")
    if col_oc:
        ocs = ["Todas"] + sorted(df[col_oc].dropna().unique().astype(str).tolist())
        oc_selected = st.sidebar.selectbox("Filtrar por OC:", ocs)
        
        df_filtered = df.copy()
        if oc_selected != "Todas":
            df_filtered = df_filtered[df_filtered[col_oc] == oc_selected]
    else:
        df_filtered = df.copy()

    # --- MÉTRICAS ---
    c1, c2 = st.columns(2)
    with c1:
        total_col = 'TOTAL PATINES' if 'TOTAL PATINES' in df.columns else df.columns[4] if len(df.columns)>4 else None
        if total_col:
            st.metric("Total Programado", f"{int(df_filtered[total_col].sum()):,}")
    with c2:
        st.metric("Pendientes", f"{int(df_filtered[col_pen].sum()):,}")

    # --- COLORES (GRIS Y VERDE) ---
    def apply_style(row):
        # Si pendientes es 0 -> Verde
        if row[col_pen] == 0:
            return ['background-color: #92d050; color: black'] * len(row)
        # Si tiene pendientes -> Gris
        else:
            return ['background-color: #bfbfbf; color: black'] * len(row)

    st.dataframe(
        df_filtered.style.apply(apply_style, axis=1),
        use_container_width=True,
        hide_index=True
    )

    if st.button("🔄 Actualizar"):
        st.cache_data.clear()
        st.rerun()
