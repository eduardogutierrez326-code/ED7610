import streamlit as st
import pandas as pd

st.set_page_config(page_title="Presupuesto Eduardo - Sobres", layout="wide")

# Estilo CSS para controlar la impresión y el tamaño de letra
st.markdown("""
    <style>
    /* Estilo para pantalla */
    .stMetric { font-size: 1.2rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    .stAlert { padding: 0.5rem !important; font-size: 0.85rem !important; }

    /* ESTILO PARA IMPRESIÓN */
    @media print {
        .no-print { display: none !important; }
        .page-break { page-break-before: always; }
        .stMetric { border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; }
    }
    </style>
    """, unsafe_allow_html=True)

# 1. Función para limpiar el dinero
def limpiar_monto(valor):
    if pd.isna(valor): return 0.0
    if isinstance(valor, str):
        valor = valor.replace('$', '').replace(',', '').strip()
    try: return float(valor)
    except: return 0.0

# 2. Configuración de la URL
SHEET_ID = "1K0oQeGA2T5hyd5CoAq6erWV-br0hQj_rdZe-HH3LMSw"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip().str.upper()
    
    if 'CATIDAD' in df.columns and 'CANTIDAD' not in df.columns:
        df.rename(columns={'CATIDAD': 'CANTIDAD'}, inplace=True)
    
    df['CANTIDAD'] = df['CANTIDAD'].apply(limpiar_monto)
    df['DP'] = pd.to_numeric(df['DP'], errors='coerce').fillna(0).astype(int)

    # --- BARRA LATERAL (No se imprime) ---
    st.sidebar.header("Configuración")
    opciones_dp = [1, 8, 16, 24]
    periodo = st.sidebar.selectbox("Selecciona el DP:", opciones_dp)
    
    df_periodo = df[df['DP'] == periodo]
    total_periodo = df_periodo['CANTIDAD'].sum()

    # --- HOJA 1: RESUMEN DE SOBRES ---
    st.title(f"💰 Resumen de Sobres - Pago Día {periodo}")
    st.metric(label="TOTAL A RETIRAR", value=f"${total_periodo:,.2f}")
    
    st.subheader("Distribución para Sobres")
    if not df_periodo.empty:
        resumen_sobres = df_periodo.groupby('SOBRE')['CANTIDAD'].sum().reset_index()
        cols = st.columns(3) # 3 columnas para que los nombres se lean bien
        for i, row in resumen_sobres.iterrows():
            with cols[i % 3]:
                st.info(f"**{row['SOBRE']}**\n\n${row['CANTIDAD']:,.2f}")
    
    # --- SALTO DE PÁGINA PARA IMPRESIÓN ---
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

    # --- HOJA 2: DETALLE DE GASTOS ---
    st.subheader(f"📋 Detalle de Gastos (DP {periodo})")
    if not df_periodo.empty:
        # Usamos table para que sea 100% compatible con impresión
        st.table(df_periodo[['SOBRE', 'GASTO', 'CANTIDAD', 'OBSERVACIONES']])
        
        # Botón de descarga (solo visible en pantalla)
        csv = df_periodo.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f'Detalle_DP_{periodo}.csv',
            mime='text/csv',
        )
    else:
        st.warning("No hay datos para este DP.")

except Exception as e:
    st.error(f"Error: {e}")

st.sidebar.write("---")
st.sidebar.warning("💡 **Para imprimir:** Presiona **Ctrl+P** y asegúrate de que 'Gráficos de fondo' esté activado en los ajustes de impresión.")
