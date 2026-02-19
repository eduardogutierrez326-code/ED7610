import streamlit as st
import pandas as pd

st.set_page_config(page_title="Presupuesto Eduardo", layout="wide")

# 1. Función para limpiar el dinero (quita $, comas y espacios)
def limpiar_monto(valor):
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, str):
        valor = valor.replace('$', '').replace(',', '').strip()
    try:
        return float(valor)
    except:
        return 0.0

# 2. Configuración de la URL
SHEET_ID = "1K0oQeGA2T5hyd5CoAq6erWV-br0hQj_rdZe-HH3LMSw"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.title("📊 Mi Presupuesto Dinámico")

try:
    # Leer el CSV
    df = pd.read_csv(URL)
    
    # Limpiar nombres de columnas (quita espacios al inicio/final y pasa a mayúsculas)
    df.columns = df.columns.str.strip().str.upper()
    
    # --- AUTO-CORRECCIÓN DE COLUMNAS ---
    # Si escribiste "CATIDAD" en lugar de "CANTIDAD", esto lo arregla:
    if 'CATIDAD' in df.columns and 'CANTIDAD' not in df.columns:
        df.rename(columns={'CATIDAD': 'CANTIDAD'}, inplace=True)
    
    # 3. Limpiar los datos
    if 'CANTIDAD' in df.columns:
        df['CANTIDAD'] = df['CANTIDAD'].apply(limpiar_monto)
    
    if 'DP' in df.columns:
        df['DP'] = pd.to_numeric(df['DP'], errors='coerce').fillna(0).astype(int)

    # --- INTERFAZ ---
    st.sidebar.header("Configuración")
    opciones_dp = sorted(df['DP'].unique())
    # Filtrar solo los DPs válidos que acordamos (1, 8, 16, 24)
    opciones_dp = [x for x in opciones_dp if x in [1, 8, 16, 24]]
    
    periodo = st.sidebar.selectbox("Selecciona tu Día de Pago:", opciones_dp if opciones_dp else [1, 8, 16, 24])

    # Filtrar
    df_periodo = df[df['DP'] == periodo]

    # Mostrar Métricas
    total = df_periodo['CANTIDAD'].sum()
    st.metric(label=f"Presupuesto para el DP {periodo}", value=f"${total:,.2f}")

    # Mostrar Tabla
    if not df_periodo.empty:
        st.subheader(f"Gastos del periodo (Día {periodo})")
        # Seleccionamos solo las columnas que existan para evitar errores
        cols_a_mostrar = [c for c in ['GASTO', 'CANTIDAD', 'TEMPORALIDAD', 'OBSERVACIONES'] if c in df.columns]
        st.dataframe(df_periodo[cols_a_mostrar], use_container_width=True, hide_index=True)
    else:
        st.warning(f"No hay datos para el DP {periodo}. Revisa la columna DP en tu Excel.")

except Exception as e:
    st.error("⚠️ Error de conexión")
    st.write("Verifica que tu Google Sheet tenga activada la opción: **'Cualquier persona con el enlace puede leer'**.")
    st.info(f"Detalle técnico: {e}")

st.markdown("---")
st.caption("Estrategia: 1, 8, 16 y 24")
