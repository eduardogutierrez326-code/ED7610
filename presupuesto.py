import streamlit as st
import pandas as pd

st.set_page_config(page_title="Presupuesto Eduardo", layout="wide")

# 1. Función para limpiar el dinero
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

st.title("📊 Mi Presupuesto Semanal")

try:
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip().str.upper()
    
    # Auto-corrección de columnas
    if 'CATIDAD' in df.columns and 'CANTIDAD' not in df.columns:
        df.rename(columns={'CATIDAD': 'CANTIDAD'}, inplace=True)
    
    if 'CANTIDAD' in df.columns:
        df['CANTIDAD'] = df['CANTIDAD'].apply(limpiar_monto)
    
    if 'DP' in df.columns:
        df['DP'] = pd.to_numeric(df['DP'], errors='coerce').fillna(0).astype(int)

    # --- INTERFAZ ---
    st.sidebar.header("Opciones de Impresión")
    opciones_dp = [1, 8, 16, 24]
    periodo = st.sidebar.selectbox("Selecciona DP para imprimir:", opciones_dp)

    # Filtrar
    df_periodo = df[df['DP'] == periodo]
    total = df_periodo['CANTIDAD'].sum()

    # --- BOTONES DE DESCARGA ---
    # Creamos un archivo CSV para que lo abras en Excel e imprimas fácil
    csv = df_periodo.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Descargar para Excel",
        data=csv,
        file_name=f'Presupuesto_DP_{periodo}.csv',
        mime='text/csv',
    )

    # Visualización
    st.header(f"Resumen de Gastos - Pago del día {periodo}")
    st.metric(label="TOTAL A SEPARAR", value=f"${total:,.2f}")

    if not df_periodo.empty:
        # Mostramos la tabla
        st.table(df_periodo[['GASTO', 'CANTIDAD', 'OBSERVACIONES']])
        
        st.info("💡 **Tip para imprimir:** Presiona `Ctrl + P` (en Windows) o `Cmd + P` (en Mac) para imprimir esta pantalla directamente.")
    else:
        st.warning("No hay datos para este DP.")

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.caption("Estrategia 1-8-16-24 | Eduardo y Esposa")
