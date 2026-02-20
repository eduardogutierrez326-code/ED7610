import streamlit as st
import pandas as pd

st.set_page_config(page_title="Presupuesto Eduardo - Sobres", layout="wide")

# Estilo CSS para reducir el tamaño de letra en las tarjetas de sobres
st.markdown("""
    <style>
    .stMetric {
        font-size: 1.2rem !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    /* Estilo para las cajitas de información (Sobres) */
    .stAlert {
        padding: 0.5rem !important;
        font-size: 0.85rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

st.title("📊 Gestión de Presupuesto por Sobres")

try:
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip().str.upper()
    
    # Corregir columna CANTIDAD si tiene error de dedo
    if 'CATIDAD' in df.columns and 'CANTIDAD' not in df.columns:
        df.rename(columns={'CATIDAD': 'CANTIDAD'}, inplace=True)
    
    if 'CANTIDAD' in df.columns:
        df['CANTIDAD'] = df['CANTIDAD'].apply(limpiar_monto)
    
    if 'DP' in df.columns:
        df['DP'] = pd.to_numeric(df['DP'], errors='coerce').fillna(0).astype(int)

    # --- INTERFAZ ---
    st.sidebar.header("Opciones")
    opciones_dp = [1, 8, 16, 24]
    periodo = st.sidebar.selectbox("Selecciona el Día de Pago (DP):", opciones_dp)

    # Filtrar datos
    df_periodo = df[df['DP'] == periodo]
    total_periodo = df_periodo['CANTIDAD'].sum()

    # Métrica Principal
    st.metric(label=f"Total a cubrir para el DP {periodo}", value=f"${total_periodo:,.2f}")

    # --- RESUMEN POR SOBRES (Letra más pequeña) ---
    st.subheader("💰 Distribución por Sobres")
    if not df_periodo.empty:
        resumen_sobres = df_periodo.groupby('SOBRE')['CANTIDAD'].sum().reset_index()
        
        # Mostrar sobres en columnas (hasta 4 por fila para que no se vea gigante)
        cols = st.columns(4) 
        for i, row in resumen_sobres.iterrows():
            with cols[i % 4]:
                st.info(f"**{row['SOBRE']}**\n\n${row['CANTIDAD']:,.2f}")
    
    # --- DETALLE DE GASTOS Y BOTÓN DE IMPRESIÓN ---
    st.subheader("📋 Detalle de Gastos")
    if not df_periodo.empty:
        # Tabla estática para que se imprima mejor
        st.table(df_periodo[['SOBRE', 'GASTO', 'CANTIDAD', 'OBSERVACIONES']])
        
        # Botón de Descarga/Impresión en la barra lateral
        csv = df_periodo.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📥 Descargar para Imprimir (CSV)",
            data=csv,
            file_name=f'Presupuesto_DP_{periodo}.csv',
            mime='text/csv',
        )
        st.sidebar.write("---")
        st.sidebar.info("💡 **Tip:** Presiona `Ctrl + P` para guardar como PDF o imprimir esta vista.")

    else:
        st.warning("No hay gastos registrados para este DP.")

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.caption("Estrategia 1-8-16-24 | Eduardo Gutierrez")
