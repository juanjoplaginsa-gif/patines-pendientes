import streamlit as st
import pandas as pd

st.set_page_config(page_title="Control BIRK - Resumen", layout="wide")

# Estilo para mejorar la lectura
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS9mEVGhFL6d_wC49GEz52Z3Hrb1wf-cGqYxEUrZPIiTI7nJ0KLEjYw0YqBCqPYP3yMfPx8h79RRjS7/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip().upper() for c in df.columns]
        for col in ['TOTAL PATINES', 'PENDIENTES']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load_data()

if df is not None:
    st.title("👡 Control de Producción con Subtotales")

    # --- FILTROS ---
    with st.expander("🔍 Filtros y Opciones"):
        col_oc = 'ORDEN DE COMPRA' if 'ORDEN DE COMPRA' in df.columns else None
        df_filtered = df.copy()
        if col_oc:
            ocs = ["Todas"] + sorted(df[col_oc].dropna().unique().astype(str).tolist())
            oc_selected = st.selectbox("Seleccionar OC:", ocs)
            if oc_selected != "Todas":
                df_filtered = df_filtered[df_filtered[col_oc] == oc_selected]

    # --- LÓGICA DE SUMATORIOS POR FECHA ---
    # Agrupamos por fecha para obtener los subtotales
    col_fecha = 'FECHA SERVICIO' if 'FECHA SERVICIO' in df.columns else df.columns[0]
    
    st.subheader("📊 Resumen por Fecha")
    
    # Crear el resumen agrupado
    resumen_fechas = df_filtered.groupby(col_fecha)[['TOTAL PATINES', 'PENDIENTES']].sum().reset_index()
    
    # Mostrar el resumen en columnas pequeñas o tabla
    st.dataframe(resumen_fechas, use_container_width=True, hide_index=True)

    st.divider()

    # --- DETALLE COMPLETO CON COLORES ---
    st.subheader("📋 Detalle de Artículos")

    # Función para aplicar colores (Gris y Verde)
    def apply_style(row):
        color = '#92d050' if row['PENDIENTES'] == 0 else '#bfbfbf'
        return [f'background-color: {color}; color: black'] * len(row)

    # Mostrar tabla principal
    st.dataframe(
        df_filtered.style.apply(apply_style, axis=1),
        use_container_width=True,
        hide_index=True
    )

    if st.button("🔄 Actualizar"):
        st.cache_data.clear()
        st.rerun()
