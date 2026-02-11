 import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="PLAN DE PROTEÍNAS", layout="wide")
st.title("📋 CONTADOR Y PLANEADOR DE COCINA")

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

st.info(f"📅 Periodo: {dias_totales} días | Comidas totales: {total_comidas}")

# 2. CUOTAS CALCULADAS
st.subheader("📊 Cuotas necesarias (Según tus %)")
porc_config = {
    "RES (30%)": 0.30, "CERDO (25%)": 0.25, "HUEVO (15%)": 0.15, 
    "POLLO (15%)": 0.15, "PESCADO (5%)": 0.05, "EMBUTIDOS (10%)": 0.10
}

cuotas = {}
cols = st.columns(6)
for i, (cat, p) in enumerate(porc_config.items()):
    cant = round(total_comidas * p)
    cuotas[cat] = cant
    cols[i].metric(cat.split()[0], f"{cant} platos")

# 3. SELECCIÓN Y CANTIDADES
sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df_db = pd.read_csv(url)
    columna_datos = 'PROTEINAS' if 'PROTEINAS' in df_db.columns else df_db.columns[0]
    opciones = df_db[columna_datos].dropna().unique()
    
    st.markdown("---")
    st.subheader("🛒 ¿Qué tienes en el refri y cuánto?")
    
    seleccionadas = st.multiselect("Selecciona las proteínas que usarás:", options=opciones)
    
    inventario_usuario = []
    if seleccionadas:
        st.write("Indica cuántas veces usarás cada proteína:")
        # Creamos columnas para que no se vea una lista larga hacia abajo
        c1, c2 = st.columns(2)
        for idx, item in enumerate(seleccionadas):
            with (c1 if idx % 2 == 0 else c2):
                cantidad = st.number_input(f"Repeticiones para: {item}", min_value=1, max_value=20, value=1, key=item)
                inventario_usuario.append({"Proteína": item, "Cantidad": cantidad})

except:
    st.error("⚠️ No se pudo conectar con Drive.")

# 4. TABLA FINAL PARA IMPRIMIR
if st.button("GENERAR LISTA FINAL PARA EL REFRI"):
    st.markdown("---")
    st.subheader("🖨️ LISTA DE DISTRIBUCIÓN LIBRE")
    
    # Tabla de lo que tienes vs lo que necesitas
    df_inventario = pd.DataFrame(inventario_usuario)
    total_piezas = df_inventario["Cantidad"].sum() if not df_inventario.empty else 0
    
    st.table(df_inventario)
    
    st.write(f"**Total de platos cubiertos con tu selección:** {total_piezas} de {total_comidas} necesarios.")
    
    if total_piezas < total_comidas:
        st.warning(f"⚠️ Te faltan cubrir {total_comidas - total_piezas} comidas para completar el periodo.")
    
    # Formato para imprimir
    resumen_texto = f"PLAN DE COMIDAS ({fecha_inicio} al {fecha_final})\n"
    resumen_texto += "-"*30 + "\n"
    for item in inventario_usuario:
        resumen_texto += f"[ ] {item['Proteína']} (Usar {item['Cantidad']} veces)\n"
    
    st.download_button("Descargar Lista para Imprimir", resumen_texto, "mi_plan_cocina.txt")
