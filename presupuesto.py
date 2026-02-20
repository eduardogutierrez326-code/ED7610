import streamlit as st
import pandas as pd

st.set_page_config(page_title="Presupuesto Eduardo - Sobres", layout="wide")

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

st.title("📊 Gestión de Presupuesto por Sobres")

try:
    # Leer el CSV
    df = pd.read_csv(URL)
    
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip().str.upper()
    
    # 3. Limpiar los datos numéricos
    if 'CANTIDAD' in df.columns:
        df['CANTIDAD'] = df['CANTIDAD'].apply(limpiar_monto)
    
    if 'DP' in df.columns:
        df['DP'] = pd.to_numeric(df['DP'], errors='coerce').fillna(0).astype(int)

    # --- INTERFAZ DE FILTROS ---
    st.sidebar.header("Control de Periodo")
    opciones_dp = [1, 8, 16, 24]
    periodo = st.sidebar.selectbox("Selecciona el Día de Pago (DP):", opciones_dp)

    # Filtrar datos por el DP seleccionado
    df_periodo = df[df['DP'] == periodo]
    total_periodo = df_periodo['CANTIDAD'].sum()

    # --- MÉTRICA PRINCIPAL ---
    st.metric(label=f"Total a cubrir para el DP {periodo}", value=f"${total_periodo:,.2f}")

    # --- RESUMEN POR SOBRES (LO NUEVO) ---
    st.subheader("💰 Distribución por Sobres")
    if not df_periodo.empty:
        # Agrupar por la nueva columna SOBRE
        resumen_sobres = df_periodo.groupby('SOBRE')['CANTIDAD'].sum().reset_index()
        
        # Crear columnas para mostrar los sobres de forma visual
        cols = st.columns(len(resumen_sobres) if len(resumen_sobres) > 0 else 1)
        for i, row in resumen_sobres.iterrows():
            cols[i % len(cols)].info(f"**{row['SOBRE']}**\n\n${row['CANTIDAD']:,.2f}")
    
    # --- DETALLE DE GASTOS ---
    st.subheader("📋 Detalle de Gastos")
    if not df_periodo.empty:
        # Mostrar tabla organizada
        st.table(df_periodo[['SOBRE', 'GASTO', 'CANTIDAD', 'OBSERVACIONES']])
        
        # Botón para descargar el resumen del DP
        csv = df_periodo.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar lista de este DP",
            data=csv,
            file_name=f'Presupuesto_Sobres_DP_{periodo}.csv',
            mime='text/csv',
        )
    else:
        st.warning("No hay gastos registrados para este DP.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")

st.markdown("---")
st.caption("Sistema de Sobres | Eduardo Gutierrez")
