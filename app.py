import streamlit as st
import pandas as pd

st.set_page_config(page_title="Control BIRK - Ordenado", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS9mEVGhFL6d_wC49GEz52Z3Hrb1wf-cGqYxEUrZPIiTI7nJ0KLEjYw0YqBCqPYP3yMfPx8h79RRjS7/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # --- CORRECCIÓN DE FECHAS ---
        col_fecha = 'FECHA SERVICIO'
        if col_fecha in df.columns:
            # Convertimos a fecha real (Día/Mes/Año)
            df[col_fecha] = pd.to_datetime(df[col_fecha], dayfirst=True, errors='coerce')
            # Ordenamos cronológicamente
            df = df.sort_values(by=col_fecha, ascending=True)
        
        # Limpieza de números
        for col in ['TOTAL PATINES', 'PENDIENTES']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load_data()

if df is not None:
    st.title("👡 Control de Producción (Orden Cronológico)")

    # --- FILTRO ---
    with st.expander("🔍 Filtrar por Orden de Compra"):
        col_oc = 'ORDEN DE COMPRA'
        ocs = ["Todas"] + sorted(df[col_oc].dropna().unique().astype(str).tolist())
        oc_sel = st.selectbox("Seleccionar OC:", ocs)
        df_filtered = df.copy()
        if oc_sel != "Todas":
            df_filtered = df_filtered[df_filtered[col_oc] == oc_sel]

    # --- TABLA CON SUBTOTALES ---
    # Formateamos la fecha para que se vea bonita (DD/MM/YYYY) antes de mostrarla
    df_display = df_filtered.copy()
    df_display['FECHA SERVICIO'] = df_display['FECHA SERVICIO'].dt.strftime('%d/%m/%Y')

    # Agrupamos por fecha para los subtotales
    st.subheader("📊 Resumen de Totales por Fecha")
    resumen = df_filtered.groupby('FECHA SERVICIO')[['TOTAL PATINES', 'PENDIENTES']].sum().reset_index()
    resumen['FECHA SERVICIO'] = resumen['FECHA SERVICIO'].dt.strftime('%d/%m/%Y')
    
    st.table(resumen) # Tabla fija de subtotales

    st.divider()

    # --- DETALLE CON COLORES ---
    st.subheader("📋 Detalle de Artículos")

    def apply_style(row):
        color = '#92d050' if row['PENDIENTES'] == 0 else '#bfbfbf'
        return [f'background-color: {color}; color: black'] * len(row)

    st.dataframe(
        df_display.style.apply(apply_style, axis=1),
        use_container_width=True,
        hide_index=True
    )

    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
