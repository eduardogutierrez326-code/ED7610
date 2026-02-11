import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="LISTA DE PROTEÍNAS", layout="wide")
st.title("📋 PLANEADOR DE PROTEÍNAS")

# 1. ENTRADA DE FECHAS Y CÁLCULO DE COMIDAS
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

st.info(f"📅 Periodo: {dias_totales} días | Total de comidas a planear: {total_comidas}")

# 2. TABLA DE PORCENTAJES Y CUOTAS
st.subheader("📊 Cuotas de Comida por Categoría")
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

# 3. SELECCIÓN DE PROTEÍNAS DESDE DRIVE
sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df_db = pd.read_csv(url)
    columna_datos = 'PROTEINAS' if 'PROTEINAS' in df_db.columns else df_db.columns[0]
    opciones = df_db[columna_datos].dropna().unique()
    
    st.markdown("---")
    st.subheader("🛒 Selecciona qué usarás para cubrir tus cuotas:")
    
    seleccion = st.multiselect("Selecciona todas las carnes que tienes disponibles:", options=opciones)
    
except:
    st.error("⚠️ Revisa el enlace de tu Drive.")

# 4. GENERAR LISTA PARA IMPRIMIR
if st.button("GENERAR LISTA DE COMPRAS/PLANEO"):
    st.markdown("### 🖨️ RESUMEN PARA LA COCINA")
    
    # Crear una tabla resumen
    resumen_data = []
    for cat, cant in cuotas.items():
        resumen_data.append({
            "Categoría": cat,
            "Platos Necesarios": cant,
            "Sugerencias": "Huevo (15 pzas) / Costilla" if "HUEVO" in cat or "RES" in cat else "Ver lista seleccionada"
        })
    
    st.table(resumen_data)
    
    st.markdown("**Proteínas seleccionadas para distribuir libremente:**")
    for item in seleccion:
        st.write(f"- [ ] {item}")
        
    # Botón para descargar
    texto_imprimir = f"RESUMEN DE COMIDAS\nDel {fecha_inicio} al {fecha_final}\n\n"
    for cat, cant in cuotas.items():
        texto_imprimir += f"{cat}: {cant} comidas\n"
    texto_imprimir += "\nCARNES SELECCIONADAS:\n" + "\n".join(seleccion)
    
    st.download_button("Descargar Lista de Planeación", texto_imprimir, "plan_cocina.txt")
