import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Presupuesto Eduardo - Completo", layout="wide")

# CSS para impresión y diseño
st.markdown("""
    <style>
    @media print {
        @page { size: letter; margin: 1cm; }
        header, footer, .no-print, [data-testid="stSidebar"], [data-testid="stHeader"] { display: none !important; }
        .page-break { display: block; page-break-before: always; margin-top: 20px; }
        table { font-size: 10pt; width: 100%; }
    }
    .stMetric { font-size: 1.1rem !important; }
    .stAlert { padding: 0.4rem !important; font-size: 0.8rem !important; min-height: 80px; }
    </style>
    """, unsafe_allow_html=True)

def limpiar_monto(valor):
    if pd.isna(valor): return 0.0
    if isinstance(valor, str):
        valor = valor.replace('$', '').replace(',', '').strip()
    try: return float(valor)
    except: return 0.0

def extraer_dia(texto):
    if pd.isna(texto): return 99
    # Busca el primer número en el texto para ordenar (ej. "CADA 30" -> 30)
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
    df['ORDEN_DIA'] = df['TEMPORALIDAD'].apply(extraer_dia)

    # --- BARRA LATERAL CON TODOS LOS PERIODOS ---
    st.sidebar.header("🗓️ Control de Gastos")
    # Aquí ya incluimos el 1 y el 8 nuevamente
    periodo = st.sidebar.selectbox("Selecciona el Día de Pago (DP):", [1, 8, 16, 24])
    
    # Filtrar y ordenar por día cronológico
    df_periodo = df[df['DP'] == periodo].sort_values(by='ORDEN_DIA')
    total = df_periodo['CANTIDAD'].sum()

    # --- HOJA 1: RESUMEN DE SOBRES ---
    st.title(f"💰 Sobres - Pago Día {periodo}")
    st.metric(label="TOTAL A SEPARAR", value=f"${total:,.2f}")
    
    st.subheader("Totales por Sobre")
    if not df_periodo.empty:
        resumen_sobres = df_periodo.groupby('SOBRE')['CANTIDAD'].sum().reset_index()
        cols = st.columns(3)
        for i, row in resumen_sobres.iterrows():
            with cols[i % 3]:
                st.info(f"**{row['SOBRE']}**\n\n${row['CANTIDAD']:,.2f}")
    
    # --- SALTO DE PÁGINA ---
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

    # --- HOJA 2: DETALLE PARA ESPOSA ---
    st.subheader(f"📋 Detalle Cronológico de Gastos (DP {periodo})")
    if not df_periodo.empty:
        # Reordenamos columnas para que lo primero que vea sea la fecha/temporalidad
        columnas_ver = ['TEMPORALIDAD', 'GASTO', 'CANTIDAD', 'SOBRE', 'OBSERVACIONES']
        st.table(df_periodo[[c for c in columnas_ver if c in df_periodo.columns]])
    else:
        st.warning(f"No hay gastos programados para el DP {periodo}.")

except Exception as e:
    st.error(f"Error: {e}")

st.sidebar.write("---")
st.sidebar.info("💡 **Tip:** Al imprimir, el sistema ordenará los gastos del DP seleccionado según el número que encuentre en 'Temporalidad'.")
