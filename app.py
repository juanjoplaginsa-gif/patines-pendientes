import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Control de Producción - BIRK", layout="wide")

# Tu enlace de Google Sheets corregido
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS9mEVGhFL6d_wC49GEz52Z3Hrb1wf-cGqYxEUrZPIiTI7nJ0KLEjYw0YqBCqPYP3yMfPx8h79RRjS7/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    # Leemos directamente del link de Google
    df = pd.read_csv(SHEET_URL)
    df.columns = [c.strip() for c in df.columns]
    # Convertimos a número la columna PENDIENTES
    df['PENDIENTES'] = pd.to_numeric(df['PENDIENTES'], errors='coerce').fillna(0)
    return df

try:
    df = load_data()

    st.title("📦 Panel de Control de Pendientes")

    # --- FILTROS ---
    st.sidebar.header("Filtros")
    oc_list = ["Todas"] + sorted(df["ORDEN DE COMPRA"].unique().astype(str).tolist())
    oc_sel = st.sidebar.selectbox("Orden de Compra:", oc_list)

    df_final = df.copy()
    if oc_sel != "Todas":
        df_final = df_final[df_final["ORDEN DE COMPRA"] == oc_sel]

    # --- MÉTRICAS ---
    m1, m2 = st.columns(2)
    m1.metric("Total Programado", f"{int(df_final['TOTAL PATINES'].sum()):,}")
    m2.metric("Pendientes", f"{int(df_final['PENDIENTES'].sum()):,}")

    # --- TABLA ---
    def style_rows(row):
        return ['background-color: #d4edda' if row['PENDIENTES'] == 0 else '' for _ in row]

    st.dataframe(df_final.style.apply(style_rows, axis=1), use_container_width=True)

except Exception as e:
    st.error("Error al cargar datos. Verifica el formato del Sheet.")
    st.write(e)
