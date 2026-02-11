import streamlit as st
import pandas as pd
import random
from datetime import timedelta

st.set_page_config(page_title="MENU", layout="wide")
st.title("🍴 MENU - CONTROL TOTAL")

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

dias_totales = (fecha_final - fecha_inicio).days + 1
total_comidas = dias_totales * 2

# 2. CÁLCULO DE CANTIDADES POR CATEGORÍA
st.markdown("---")
st.subheader("📊 Cantidades de Comida Necesarias")
porc_config = {
    "RES": 0.30, "CERDO": 0.25, "HUEVO": 0.15, 
    "POLLO": 0.15, "PESCADO": 0.05, "EMBUTIDOS": 0.10
}

# Diccionario para guardar cuántas comidas tocan de cada una
conteo_comidas = {}
cols_p = st.columns(6)
for i, (cat, p) in enumerate(porc_config.items()):
    cant = round(total_comidas * p)
    conteo_comidas[cat] = cant
    cols_p[i].metric(cat, f"{cant} platos")

# 3. SELECCIÓN DESDE TU DRIVE
sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df_db = pd.read_csv(url)
    st.markdown("---")
    columna_datos = 'PROTEINAS' if 'PROTEINAS' in df_db.columns else df_db.columns[0]
    opciones = df_db[columna_datos].dropna().unique()
    
    st.subheader("🛒 Asigna tus carnes a las categorías:")
    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)
    
    res_sel = c1.multiselect("Tus cortes de RES:", options=opciones)
    cerdo_sel = c2.multiselect("Tus cortes de CERDO:", options=opciones)
    pollo_sel = c3.multiselect("Tus piezas de POLLO:", options=opciones)
    emb_sel = c4.multiselect("Tus EMBUTIDOS:", options=opciones)
    pes_sel = c5.multiselect("Tus PESCADOS:", options=opciones)
    # El huevo es fijo
except:
    st.error("⚠️ Revisa el enlace de tu Drive.")

# 4. BOTÓN DE DISTRIBUCIÓN
if st.button("GENERAR CALENDARIO Y DISTRIBUIR"):
    menu_final = []
    
    # Creamos una lista larga de proteínas basada en tus porcentajes
    # Si no seleccionas nada en una categoría, usará el nombre genérico
    pool_res = res_sel if res_sel else ["Res Genérica"]
    pool_cerdo = cerdo_sel if cerdo_sel else ["Cerdo Genérico"]
    pool_pollo = pollo_sel if pollo_sel else ["Pollo Genérico"]
    pool_emb = emb_sel if emb_sel else ["Embutido Genérico"]
    pool_pes = pes_sel if pes_sel else ["Pescado Genérico"]

    for i in range(dias_totales):
        fecha = fecha_inicio + timedelta(days=i)
        
        # Lógica de Desayuno (Huevo fijo cada 3 días)
        if i % 3 == 0:
            desayuno = "HUEVOS (15 pzas)"
        else:
            desayuno = random.choice(pool_emb + pool_pollo) # Desayunos variados
            
        # Lógica de Almuerzo (Caldos fijos cada 4 días)
        if i % 4 == 0:
            almuerzo = "CALDO (Costilla/Hueso de Res)"
        else:
            # Alterna entre Res, Cerdo y Pollo para el almuerzo
            opciones_hoy = pool_res + pool_cerdo + pool_pollo
            almuerzo = random.choice(opciones_hoy)
            
        menu_final.append([fecha.strftime("%d/%m/%Y"), desayuno, almuerzo])

    st.markdown("### 🖨️ Calendario de Comidas")
    df_res = pd.DataFrame(menu_final, columns=["FECHA", "DESAYUNO", "ALMUERZO"])
    st.table(df_res)
    
    csv = df_res.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Menú para Imprimir", csv, "menu_final.csv")
