import streamlit as st
import pandas as pd

# Configuración de página optimizada
st.set_page_config(page_title="Control BIRK", layout="wide")

# Estilo CSS para que la tabla sea más cómoda en móvil
st.markdown("""
    <style>
    .stDataFrame { width: 100%; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
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
    st.title("👡 Control BIRK")

    # Filtros simplificados
    col_oc = 'ORDEN DE COMPRA' if 'ORDEN DE COMPRA' in df.columns else None
    
    with st.expander("🔍 Toca aquí para Filtrar"):
        if col_oc:
            ocs = ["Todas"] + sorted(df[col_oc].dropna().unique().astype(str).tolist())
            oc_selected = st.selectbox("Seleccionar OC:", ocs)
            df_filtered = df.copy()
            if oc_selected != "Todas":
                df_filtered = df_filtered[df_filtered[col_oc] == oc_selected]
        else:
            df_filtered = df.copy()

    # Métricas adaptables
    c1, c2 = st.columns(2)
    total_col = 'TOTAL PATINES' if 'TOTAL PATINES' in df.columns else None
    with c1:
        if total_col:
            st.metric("Programado", f"{int(df_filtered[total_col].sum()):,}")
    with c2:
        st.metric("Pendiente", f"{int(df_filtered['PENDIENTES'].sum()):,}")

    # Estilo de colores (Gris y Verde)
    def apply_style(row):
        color = '#92d050' if row['PENDIENTES'] == 0 else '#bfbfbf'
        return [f'background-color: {color}; color: black'] * len(row)

    # Mostrar tabla sin índice para ahorrar espacio
    st.dataframe(
        df_filtered.style.apply(apply_style, axis=1),
        use_container_width=True,
        hide_index=True
    )

    if st.button("🔄 Actualizar"):
        st.cache_data.clear()
        st.rerun()
