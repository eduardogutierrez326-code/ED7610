import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Presupuesto Eduardo y Esposa", layout="wide")

# Título de la App
st.title("📊 Sistema de Gestión de Sobres (1-8-16-24)")
st.write("Estructura financiera basada en 4 periodos mensuales.")

# ID de tu Google Sheet (extraído de tu URL)
sheet_id = "1K0oQeGA2T5hyd5CoAq6erWV-br0hQj_rdZe-HH3LMSw"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

# Función para cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv(url)
    # Limpiar nombres de columnas por si hay espacios
    df.columns = df.columns.str.strip()
    # Asegurar que DP sea entero
    df['DP'] = df['DP'].fillna(0).astype(int)
    # Asegurar que CANTIDAD sea numérica
    df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0)
    return df

try:
    df = load_data()

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Control de Periodo")
    periodo_seleccionado = st.sidebar.selectbox(
        "Selecciona el Día de Pago (DP):",
        options=[1, 8, 16, 24],
        format_func=lambda x: f"Día de Pago {x}"
    )

    # Filtrar datos por el DP seleccionado
    df_filtrado = df[df['DP'] == periodo_seleccionado]

    # --- DASHBOARD PRINCIPAL ---
    col1, col2 = st.columns(2)
    
    total_periodo = df_filtrado['CANTIDAD'].sum()

    with col1:
        st.metric(label=f"Total a cubrir en DP {periodo_seleccionado}", value=f"${total_periodo:,.2f}")

    with col2:
        st.info(f"Este presupuesto cubre aproximadamente del día {periodo_seleccionado} al siguiente periodo.")

    # --- TABLA DE GASTOS ---
    st.subheader(f"📋 Detalle de Gastos - DP {periodo_seleccionado}")
    
    if not df_filtrado.empty:
        # Mostrar tabla limpia
        st.dataframe(
            df_filtrado[['GASTO', 'CANTIDAD', 'TEMPORALIDAD', 'OBSERVACIONES']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No hay gastos registrados para este día de pago en el Excel.")

    # --- RESUMEN POR CATEGORÍA ---
    st.subheader("📝 Resumen por Categoría")
    resumen_cat = df_filtrado.groupby('TEMPORALIDAD')['CANTIDAD'].sum()
    st.bar_chart(resumen_cat)

except Exception as e:
    st.error(f"Error al conectar con el Excel: {e}")
    st.info("Asegúrate de que el archivo de Google Sheets tenga los permisos de 'Cualquier persona con el enlace puede leer'.")

# Pie de página
st.markdown("---")
st.caption("Configuración: DP 1 (Inicio mes) | DP 8 (1er Pago Fuerte) | DP 16 (Provisión Casa) | DP 24 (2do Pago Fuerte)")
