import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Control de Producción - BIRK", layout="wide")

# Tu enlace de Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS9mEVGhFL6d_wC49GEz52Z3Hrb1wf-cGqYxEUrZPIiTI7nJ0KLEjYw0YqBCqPYP3yMfPx8h79RRjS7/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    # Limpiamos los nombres de las columnas para evitar errores de espacios
    df.columns = df.columns.str.strip().str.upper()
    
    # Aseguramos que las columnas numéricas sean tratadas como tal
    cols_numericas = ['TOTAL PATINES', 'PENDIENTES']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

try:
    df = load_data()

    st.title("📦 Panel de Control de Pendientes")

    # --- FILTROS EN LA BARRA LATERAL ---
    st.sidebar.header("Filtros")
    
    # Filtro de Orden de Compra (si existe la columna)
    col_oc = "ORDEN DE COMPRA"
    if col_oc in df.columns:
        oc_list = ["Todas"] + sorted(df[col_oc].unique().astype(str).tolist())
        oc_sel = st.sidebar.selectbox("Seleccionar Orden de Compra:", oc_list)
    else:
        oc_sel = "Todas"

    # Aplicar Filtro
    df_final = df.copy()
    if oc_sel != "Todas":
        df_final = df_final[df_final[col_oc] == oc_sel]

    # --- MÉTRICAS ---
    m1, m2 = st.columns(2)
    if 'TOTAL PATINES' in df_final.columns:
        m1.metric("Total Programado", f"{int(df_final['TOTAL PATINES'].sum()):,}")
    if 'PENDIENTES' in df_final.columns:
        m2.metric("Total Pendientes", f"{int(df_final['PENDIENTES'].sum()):,}")

    st.divider()

    # --- TABLA CON FORMATO ---
    # Pintamos de verde las filas donde PENDIENTES es 0
    def style_rows(row):
        if 'PENDIENTES' in row.index and row['PENDIENTES'] == 0:
            return ['background-color: #d4edda; color: #155724'] * len(row)
        return [''] * len(row)

    st.subheader("📋 Detalle de Producción")
    st.dataframe(
        df_final.style.apply(style_rows, axis=1),
        use_container_width=True,
        hide_index=True
    )

    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error("Error al cargar la tabla.")
    st.write("Verifica que los nombres de las columnas en el Excel sean correctos.")
    st.write(f"Detalle técnico: {e}")
