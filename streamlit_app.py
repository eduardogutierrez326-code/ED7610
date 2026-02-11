import streamlit as st
import pandas as pd
from datetime import timedelta

# Configuración de la página
st.set_page_config(page_title="MENU", layout="wide")
st.title("🍴 MENU - CONTROL DE PROTEÍNAS")

# 1. ENTRADA DE FECHAS
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("FECHA DE INICIO")
with col2:
    if fecha_inicio.day <= 15:
        fecha_def_fin = fecha_inicio.replace(day=25)
    else:
        proximo_mes = (fecha_inicio.replace(day=28) + timedelta(days=4)).replace(day=10)
        fecha_def_fin = proximo_mes
    fecha_final = st.date_input("FECHA FINAL", value=fecha_def_fin)

# 2. CÁLCULOS
dias_totales = (fecha_final - fecha_inicio).days + 1
total_comidas = dias_totales * 2

col_dias, col_com = st.columns(2)
col_dias.metric("DÍAS TOTALES", dias_totales)
col_com.metric("NÚMERO DE COMIDAS", total_comidas)

# 3. PORCENTAJES
st.markdown("---")
porc_config = {"RES": 0.30, "CERDO": 0.25, "HUEVO": 0.15, "POLLO": 0.15, "PESCADO": 0.05, "EMBUTIDOS": 0.10}

st.subheader("📊 Comidas calculadas por categoría:")
cols_p = st.columns(6)
for i, (cat, p) in enumerate(porc_config.items()):
    cant = round(total_comidas * p)
    cols_p[i].info(f"**{cat}**\n\n{cant} platos")

# 4. CONEXIÓN A TU DRIVE
sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

try:
    df_db = pd.read_csv(url)
    st.markdown("---")
    # Aquí buscamos la columna 'PROTEINAS' que hiciste en el Excel
    opciones = df_db['PROTEINAS'].dropna().unique()
    seleccion = st.multiselect("🛒 Selecciona las carnes que tienes en el refri:", options=opciones)
except:
    st.error("⚠️ Revisa que tu columna en Excel se llame 'PROTEINAS' y el enlace sea público.")

# 5. BOTÓN DE DISTRIBUCIÓN
if st.button("GENERAR CALENDARIO"):
    menu_final = []
    for i in range(dias_totales):
        fecha = fecha_inicio + timedelta(days=i)
        
        # Reglas de oro: Huevo en desayuno y Costilla/Hueso en almuerzo
        desayuno = "HUEVOS (15 pzas)" if i % 3 == 0 else "Proteína Variada"
        almuerzo = "CALDO (Costilla/Hueso)" if i % 4 == 0 else "Guisado del día"
        
        menu_final.append([fecha.strftime("%d/%m/%Y"), desayuno, almuerzo])

    st.markdown("### 🖨️ Menú para Imprimir")
    df_res = pd.DataFrame(menu_final, columns=["FECHA", "DESAYUNO", "ALMUERZO"])
    st.table(df_res)
    
    csv = df_res.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Archivo para Imprimir", csv, "menu.csv", "text/csv")
