import streamlit as st
import pandas as pd
from datetime import timedelta
import re

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="SIMULADOR DE AHORRO - PROTEÍNAS", layout="wide")
st.title("🥩 PLANEADOR DE PROTEÍNAS ESTRATÉGICO")

# 2. ENTRADA DE FECHAS (Cálculo de platos necesarios)
col_f1, col_f2 = st.columns(2)
with col_f1:
    fecha_inicio = st.date_input("FECHA DE INICIO")
with col_f2:
    if fecha_inicio.day <= 15:
        fecha_def_fin = fecha_inicio.replace(day=25)
    else:
        # Lógica para fin de mes
        proximo_mes = (fecha_inicio.replace(day=28) + timedelta(days=4)).replace(day=10)
        fecha_def_fin = proximo_mes
    fecha_final = st.date_input("FECHA FINAL", value=fecha_def_fin)

dias_totales = (fecha_final - fecha_inicio).days + 1
total_comidas = (dias_totales * 2)

st.info(f"📅 Periodo: {dias_totales} días | 🍽️ Total de servicios necesarios: {total_comidas}")

# 3. SIMULADOR DE PORCENTAJES (Aquí es donde ajustas para ahorrar)
st.subheader("📊 Ajuste de Porcentajes por Categoría")
st.write("Mueve los deslizadores para ver cómo cambia la cantidad de platos.")

col_a, col_b = st.columns(2)
with col_a:
    p_res = st.slider("RES (Más Caro)", 0, 100, 20) 
    p_cerdo = st.slider("CERDO (Económico)", 0, 100, 25)
    p_huevo = st.slider("HUEVO (Más Barato)", 0, 100, 20)
with col_b:
    p_pollo = st.slider("POLLO (Medio)", 0, 100, 20)
    p_embutidos = st.slider("EMBUTIDOS", 0, 100, 10)
    p_pescado = st.slider("PESCADO", 0, 100, 5)

total_p = p_res + p_cerdo + p_huevo + p_pollo + p_embutidos + p_pescado

if total_p != 100:
    st.error(f"⚠️ El total debe sumar 100%. Actualmente suma: {total_p}%")
else:
    st.success("✅ Distribución equilibrada al 100%.")

# 4. CUOTAS CALCULADAS
cuotas = {
    "RES": round(total_comidas * (p_res/100)),
    "CERDO": round(total_comidas * (p_cerdo/100)),
    "HUEVO": round(total_comidas * (p_huevo/100)),
    "POLLO": round(total_comidas * (p_pollo/100)),
    "PESCADO": round(total_comidas * (p_pescado/100)),
    "EMBUTIDOS": round(total_comidas * (p_embutidos/100))
}

# Mostrar resumen de platos resultantes
cols_m = st.columns(6)
categorias = list(cuotas.keys())
for i, cat in enumerate(categorias):
    cols_m[i].metric(cat, f"{cuotas[cat]} platos")

# 5. CONEXIÓN A DRIVE (Para seleccionar los cortes)
def leer_pestaña(sheet_id, nombre_pestaña):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
    try:
        df_sheet = pd.read_csv(url)
        return df_sheet.iloc[:, 0].dropna().unique()
    except:
        return []

sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"

st.markdown("---")
st.subheader("🛒 Selección de Menú")

inventario_final = []

# Autocompletar HUEVOS
if cuotas["HUEVO"] > 0:
    inventario_final.append({"Proteína": "HUEVOS (Servicios)", "Cat": "HUEVO", "Cantidad": cuotas["HUEVO"]})

# Columnas para multiselects
c1, c2, c3 = st.columns(3)
with c1:
    res_list = leer_pestaña(sheet_id, "RES")
    res_sel = st.multiselect(f"RES (Faltan {cuotas['RES']})", options=res_list)
    for r in res_sel:
        cant = st.number_input(f"¿Platos de {r}?", 1, 50, 1, key=f"r_{r}")
        inventario_final.append({"Proteína": r, "Cat": "RES", "Cantidad": cant})

# ... (Se puede repetir la lógica para las demás categorías igual que arriba)

if st.button("GENERAR LISTA FINAL"):
    df_inv = pd.DataFrame(inventario_final)
    st.table(df_inv)
    st.download_button("Descargar Plan", df_inv.to_csv().encode('utf-8'), "plan.csv")
