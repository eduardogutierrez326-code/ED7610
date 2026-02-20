import streamlit as st
import pandas as pd

st.set_page_config(page_title="Presupuesto Eduardo - Sobres", layout="wide")

# Estilo CSS REFORZADO para forzar el salto de página en navegadores
st.markdown("""
    <style>
    /* Estilo para pantalla */
    .stMetric { font-size: 1.2rem !important; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    .stAlert { padding: 0.5rem !important; font-size: 0.85rem !important; }

    /* ESTILO PARA IMPRESIÓN REFORZADO */
    @media print {
        header, footer, .no-print, [data-testid="stSidebar"] {
            display: none !important;
        }
        
        .main-container {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Fuerza el salto de página antes de este elemento */
        .page-break-header {
            display: block !important;
            page-break-before: always !important;
            break-before: page !important;
            margin-top: 50px !important;
        }

        /* Asegura que la tabla no se corte a la mitad de forma fea */
        table {
            page-break-inside: auto !important;
            width: 100% !important;
        }
        tr {
            page-break-inside: avoid !important;
            page-break-after: auto !important;
        }
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

    # --- BARRA LATERAL ---
    st.sidebar.header("Configuración")
    opciones_dp = [1, 8, 16, 24]
    periodo = st.sidebar.selectbox("Selecciona el DP:", opciones_dp)
    
    df_periodo = df[df['DP'] == periodo]
    total_periodo = df_periodo['CANTIDAD'].sum()

    # --- HOJA 1: RESUMEN DE SOBRES ---
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title(f"💰 Resumen de Sobres - DP {periodo}")
    st.metric(label="TOTAL A RETIRAR", value=f"${total_periodo:,.2f}")
    
    st.subheader("Distribución para Sobres")
    if not df_periodo.empty:
        resumen_sobres = df_periodo.groupby('SOBRE')['CANTIDAD'].sum().reset_index()
        cols = st.columns(3)
        for i, row in resumen_sobres.iterrows():
            with cols[i % 3]:
                st.info(f"**{row['SOBRE']}**\n\n${row['CANTIDAD']:,.2f}")
    
    # --- DIVISOR CON SALTO DE PÁGINA FORZADO ---
    # Usamos una clase específica que el CSS detectará para saltar de hoja
    st.markdown('<div class="page-break-header"></div>', unsafe_allow_html=True)

    # --- HOJA 2: DETALLE DE GASTOS ---
    st.subheader(f"📋 Informe Detallado de Gastos (DP {periodo})")
    if not df_periodo.empty:
        columnas_finales = ['SOBRE', 'GASTO', 'CANTIDAD', 'TEMPORALIDAD', 'OBSERVACIONES']
        columnas_disponibles = [c for c in columnas_finales if c in df_periodo.columns]
        
        st.table(df_periodo[columnas_disponibles])
    else:
        st.warning("No hay datos para este DP.")
    
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

st.sidebar.write("---")
st.sidebar.info("💡 **PARA IMPRIMIR CORRECTAMENTE:**\n\n1. Presiona **Ctrl + P**.\n2. En el menú de impresión, ve a **'Más ajustes'**.\n3. Activa la casilla **'Gráficos de fondo'**.\n4. ¡Listo! Verás las dos hojas.")
