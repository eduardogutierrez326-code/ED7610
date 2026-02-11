import streamlit as st
import pandas as pd
from datetime import timedelta

# Configuración de la página
st.set_page_config(page_title="MENU", layout="wide")
st.title("🍴 MENU")

# 1. ENTRADA DE FECHAS (Lado izquierdo y derecho)
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("FECHA DE INICIO")
with col2:
    # Lógica: si es 10, final 25. Si es 25, final 10 (del mes siguiente)
    if fecha_inicio.day <= 15:
        fecha_def_fin = fecha_inicio.replace(day=25)
    else:
        # Avanza al mes siguiente día 10
        proximo_mes = fecha_inicio.replace(day=28) + timedelta(days=4)
        fecha_def_fin = proximo_mes.replace(day=10)
    fecha_final = st.date_input("FECHA FINAL", value=fecha_def_fin)

# 2. CÁLCULOS DE COMIDAS
dias_totales = (fecha_final - fecha_inicio).days + 1
total_comidas = dias_totales * 2 # Desayuno y Almuerzo

st.subheader(f"📅 Días Totales: {dias_totales} | Total de Comidas: {total_comidas}")

# 3. CATEGORÍAS Y PORCENTAJES
st.markdown("### 📊 Distribución de Proteínas")
porcentajes = {"Res": 0.30, "Cerdo": 0.25, "Huevo": 0.15, "Pollo": 0.15, "Pescado": 0.05, "Embutidos": 0.10}

cols = st.columns(len(porcentajes))
for i, (cat, porc) in enumerate(porcentajes.items()):
    num_comidas = round(total_comidas * porc)
    cols[i].metric(cat, f"{num_comidas} serv.")

# 4. CONEXIÓN A BASE DE DATOS (LECTURA DEL FOOD PLANNER)
sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

try:
    df = pd.read_csv(url)
    # Aquí el usuario elegiría las proteínas de las listas desplegables
    st.info("Conectado al Food Planner: Listo para seleccionar proteínas específicas.")
except:
    st.error("Asegúrate de que el enlace sea público para 'Cualquier persona con el enlace'.")

# 5. BOTÓN DE DISTRIBUCIÓN (LÓGICA DE REGLAS)
if st.button("DISTRIBUIR COMIDAS"):
    data_menu = []
    for i in range(dias_totales):
        fecha_actual = fecha_inicio + timedelta(days=i)
        
        # Regla: Huevo siempre en Desayuno
        desayuno = "Huevos (15 pzas) con vegetales" if i % 3 == 0 else "Embutidos / Proteína"
        
        # Regla: Hueso/Costilla siempre en Almuerzo
        almuerzo = "Caldo de Res (Costilla/Hueso)" if i % 4 == 0 else "Proteína de Categoría"
        
        data_menu.append([fecha_actual.strftime("%d/%m/%Y"), desayuno, almuerzo])
    
    # 6. TABLA FINAL PARA IMPRIMIR
    df_final = pd.DataFrame(data_menu, columns=["FECHA", "DESAYUNO", "ALMUERZO"])
    st.table(df_final)
    
    # Botón para descargar/imprimir
    csv = df_final.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Menú para Imprimir", csv, "menu_semanal.csv", "text/csv")
