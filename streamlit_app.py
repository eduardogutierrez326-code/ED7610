import streamlit as st
import pandas as pd
import random
from datetime import timedelta

st.set_page_config(page_title="MENU", layout="wide")
st.title("🍴 MENU - DISTRIBUIDOR REAL")

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

# 2. CONEXIÓN A TU DRIVE
sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df_db = pd.read_csv(url)
    st.markdown("---")
    # Intentamos buscar la columna 'PROTEINAS' o la primera columna
    columna_datos = 'PROTEINAS' if 'PROTEINAS' in df_db.columns else df_db.columns[0]
    opciones = df_db[columna_datos].dropna().unique()
    
    # AQUÍ SELECCIONAS TUS CARNES
    seleccionadas = st.multiselect("🛒 Selecciona las carnes que vas a usar hoy:", options=opciones)
except:
    st.error("⚠️ No pude leer tu Excel. Revisa que el enlace sea público.")
    seleccionadas = []

# 3. BOTÓN DE DISTRIBUCIÓN
if st.button("GENERAR CALENDARIO CON MIS CARNES"):
    if not seleccionadas:
        st.warning("Por favor, selecciona al menos una carne de la lista.")
    else:
        menu_final = []
        # Hacemos una copia de la lista para ir repartiendo
        pool_carnes = seleccionadas.copy()
        
        for i in range(dias_totales):
            fecha = fecha_inicio + timedelta(days=i)
            
            # REGLA DESAYUNO: Cada 3 días Huevo, si no, lo que elegiste
            if i % 3 == 0:
                desayuno = "HUEVOS (15 pzas)"
            else:
                desayuno = random.choice(pool_carnes)
            
            # REGLA ALMUERZO: Cada 4 días Caldo, si no, lo que elegiste
            if i % 4 == 0:
                almuerzo = "CALDO (Costilla/Hueso)"
            else:
                almuerzo = random.choice(pool_carnes)
            
            menu_final.append([fecha.strftime("%d/%m/%Y"), desayuno, almuerzo])

        # 4. TABLA RESULTANTE
        st.markdown("### 🖨️ Distribución Final")
        df_res = pd.DataFrame(menu_final, columns=["FECHA", "DESAYUNO", "ALMUERZO"])
        st.table(df_res)
        
        csv = df_res.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar Menú", csv, "mi_menu.csv", "text/csv")
