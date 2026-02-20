import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Presupuesto Eduardo - Acople DP16-DP24", layout="wide")

# CSS para impresión y diseño de sobres
st.markdown("""
    <style>
    @media print {
        @page { size: letter; margin: 1cm; }
        .no-print, [data-testid="stSidebar"], [data-testid="stHeader"] { display: none !important; }
        .page-break { display: block; page-break-before: always; margin-top: 20px; }
        table { font-size: 10pt; width: 100%; }
    }
    .stMetric { font-size: 1.1rem !important; }
    .stAlert { padding: 0.5rem !important; font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

def limpiar_monto(valor):
    if pd.isna(valor): return 0.0
    if isinstance(valor, str):
        valor = valor.replace('$', '').replace(',', '').strip()
    try: return float(valor)
    except: return 0.0

def extraer_dia(texto):
    # Busca números en la columna TEMPORALIDAD para ordenar
    if pd.isna(texto): return 99
    numeros = re.findall(r'\d+', str(texto))
    return int(numeros[0]) if numeros else 99

SHEET_ID = "1K0oQeGA2T5hyd5CoAq6erWV-br0hQj_rdZe-HH3LMSw"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip().str.upper()
    
    # Limpieza de datos
    df['CANTIDAD'] = df['CANTIDAD'].apply(limpiar_monto)
    df['DP'] = pd.to_numeric(df['DP'], errors='coerce').fillna(0).astype(int)
    
    # Crear columna auxiliar para ordenar cronológicamente
    df['ORDEN_DIA'] = df['TEMPORALIDAD'].apply(extraer_dia)

    # --- INTERFAZ ---
    st.sidebar.header("📊 Fase de Acople")
    # Selector para elegir entre el cierre del 16 o inicio del 24
    periodo = st.sidebar.selectbox("Selecciona el Periodo de Pago:", [16, 24])
    
    df_periodo = df[df['DP'] == periodo].sort_values(by='ORDEN_DIA')
    total = df_periodo['CANTIDAD'].sum()

    # --- HOJA 1: RESUMEN DE SOBRES ---
    st.title(f"💰 Sobres para el Pago Día {periodo}")
    st.metric(label="TOTAL A RETIRAR", value=f"${total:,.2f}")
    
    st.subheader("Distribución por Categoría")
    resumen_sobres = df_periodo.groupby('SOBRE')['CANTIDAD'].sum().reset_index()
    cols = st.columns(3)
    for i, row in resumen_sobres.iterrows():
        with cols[i % 3]:
            st.info(f"**{row['SOBRE']}**\n\n${row['CANTIDAD']:,.2f}")

    # --- HOJA 2: DETALLE CRONOLÓGICO ---
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    st.subheader(f"📋 Plan de Pagos Ordenado (DP {periodo})")
    
    # Mostramos la tabla con el orden de fechas que detectamos
    columnas_ver = ['TEMPORALIDAD', 'GASTO', 'CANTIDAD', 'SOBRE', 'OBSERVACIONES']
    st.table(df_periodo[[c for c in columnas_ver if c in df_periodo.columns]])

except Exception as e:
    st.error(f"Error en la base de datos: {e}")

st.sidebar.write("---")
st.sidebar.info("💡 **Consejo de Acople:**\nAl imprimir el **DP 24**, verás que los gastos como 'Renta mitad 2' (Día 30) aparecen al final de la lista, ayudando a tu esposa a priorizar.")
