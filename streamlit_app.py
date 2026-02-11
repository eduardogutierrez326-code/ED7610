import streamlit as st
import pandas as pd
from datetime import timedelta

# Configuración de pantalla
st.set_page_config(page_title="MENU", layout="wide")
st.title("🍴 MENU - CONTROL DE PROTEÍNAS")

# 1. ENTRADA DE FECHAS
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("FECHA DE INICIO")
with col2:
    # Lógica de fechas (Si es 10 termina 25, si es 25 termina 10)
    if fecha_inicio.day <= 15:
        fecha_def_fin = fecha_inicio.replace(day=25)
    else:
        proximo_mes = (fecha_inicio.replace(day=28) + timedelta(days=4)).replace(day=10)
        fecha_def_fin = proximo_mes
    fecha_final = st.date_input("FECHA FINAL", value=fecha_def_fin)

# 2. CÁLCULO DE COMIDAS TOTALES
dias_totales = (fecha_final - fecha_inicio).days + 1
total_comidas = dias_totales * 2 # Desayuno y Almuerzo

col_dias, col_com = st.columns(2)
col_dias.metric("DÍAS TOTALES", dias_totales)
col_com.metric("NÚMERO DE COMIDAS", total_comidas)

# 3. PORCENTAJES Y CANTIDADES POR CATEGORÍA
st.markdown("---")
st.subheader("📊 Distribución por Porcentaje")
porc_config = {
    "RES (30%)": 0.30, "CERDO (25%)": 0.25, "HUEVO (15%)": 0.15, 
    "POLLO (15%)": 0.15, "PESCADO (5%)": 0.05, "EMBUTIDOS (10%)": 0.10
}

# Mostrar cuántas comidas tocan de cada una
cols_p = st.columns(len(porc_config))
for i, (cat, p) in enumerate(porc_config.items()):
    cant = round(total_comidas * p)
    cols_p[i].write(f"**{cat}**")
    cols_p[i].info(f"{cant} comidas")

# 4. CONEXIÓN A GOOGLE DRIVE (PROTEÍNAS)
# Usamos tu ID de hoja compartido
sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

try:
    # Leemos la base de datos para las listas desplegables
    df_db = pd.read_csv(url)
    st.markdown("---")
    st.subheader("🍗 Selección de Proteínas Específicas")
    
    # Aquí puedes elegir lo que vas a usar esta quincena
    seleccion = st.multiselect("Selecciona las proteínas que usarás de tu inventario:", 
                               options=df_db.iloc[:, 1].dropna().unique()) # Ajustado a tus columnas
except:
    st.warning("Conecta tu base de datos de Drive para ver la lista de proteínas.")

# 5. BOTÓN PARA DISTRIBUIR
if st.button("GENERAR DISTRIBUCIÓN Y CALENDARIO"):
    menu_final = []
    
    for i in range(dias_totales):
        fecha = fecha_inicio + timedelta(days=i)
        
        # REGLA 1: HUEVOS SIEMPRE DESAYUNO (Cada 3 días por el 15%)
        # REGLA 2: CALDOS (HUESO/COSTILLA) SIEMPRE ALMUERZO
        desayuno = "HUEVO (15 unidades)" if i % 4 == 0 else "Proteína Variada / Embutido"
        almuerzo = "COSTILLA / HUESO (Caldo)" if i % 5 == 0 else "Proteína (Res/Cerdo/Pollo)"
        
        menu_final.append([fecha.strftime("%d/%m/%Y"), desayuno, almuerzo])

    # 6. TABLA PARA IMPRESIÓN
    st.markdown("### 🖨️ Calendario de Comidas")
    df_resultado = pd.DataFrame(menu_final, columns=["FECHA", "DESAYUNO", "ALMUERZO"])
    st.table(df_resultado)
    
    # Opción de descargar
    csv_data = df_resultado.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Menú para Imprimir", csv_data, "distribucion_menu.csv")
