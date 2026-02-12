import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="MENU POR CATEGORÍA", layout="wide")
st.title("📋 PLANEADOR DE PROTEÍNAS COMPLETO")

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
total_comidas = (dias_totales * 2)

# 2. CUOTAS CALCULADAS
st.subheader("📊 Cuotas de Comida (Porcentajes)")
porc_config = {
    "RES": 0.30, "CERDO": 0.25, "HUEVO": 0.15, 
    "POLLO": 0.15, "PESCADO": 0.05, "EMBUTIDOS": 0.10
}

cuotas = {}
cols = st.columns(6)
for i, (cat, p) in enumerate(porc_config.items()):
    cant = round(total_comidas * p)
    cuotas[cat] = cant
    cols[i].metric(cat, f"{cant} platos")

# 3. CONEXIÓN A LAS PESTAÑAS DE DRIVE
def leer_pestaña(sheet_id, nombre_pestaña):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
    try:
        df = pd.read_csv(url)
        return df.iloc[:, 0].dropna().unique()
    except:
        return []

sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"

st.markdown("---")
st.subheader("🛒 Selecciona tus carnes por categoría")

# Inventario donde guardaremos todo
inventario_final = []

# AGREGAR HUEVOS AUTOMÁTICAMENTE (Si la cuota es mayor a 0)
if cuotas["HUEVO"] > 0:
    inventario_final.append({"Proteína": "HUEVOS (Paquete 15 pzas)", "Cat": "HUEVO", "Cantidad": cuotas["HUEVO"]})
    st.success(f"✅ Se han añadido automáticamente {cuotas['HUEVO']} servicios de Huevo a tu lista.")

c1, c2, c3 = st.columns(3)
with c1:
    res_list = leer_pestaña(sheet_id, "RES")
    res_sel = st.multiselect(f"RES (Necesitas {cuotas['RES']})", options=res_list)
    for r in res_sel:
        cant = st.number_input(f"¿Cuántas comidas de {r}?", min_value=1, value=1, key=f"res_{r}")
        inventario_final.append({"Proteína": r, "Cat": "RES", "Cantidad": cant})

with c2:
    cerdo_list = leer_pestaña(sheet_id, "CERDO")
    cerdo_sel = st.multiselect(f"CERDO (Necesitas {cuotas['CERDO']})", options=cerdo_list)
    for c in cerdo_sel:
        cant = st.number_input(f"¿Cuántas comidas de {c}?", min_value=1, value=1, key=f"cer_{c}")
        inventario_final.append({"Proteína": c, "Cat": "CERDO", "Cantidad": cant})

with c3:
    pollo_list = leer_pestaña(sheet_id, "POLLO")
    pollo_sel = st.multiselect(f"POLLO (Necesitas {cuotas['POLLO']})", options=pollo_list)
    for p in pollo_sel:
        cant = st.number_input(f"¿Cuántas comidas de {p}?", min_value=1, value=1, key=f"pol_{p}")
        inventario_final.append({"Proteína": p, "Cat": "POLLO", "Cantidad": cant})

c4, c5 = st.columns(2)
with c4:
    emb_list = leer_pestaña(sheet_id, "EMBUTIDOS")
    emb_sel = st.multiselect(f"EMBUTIDOS (Necesitas {cuotas['EMBUTIDOS']})", options=emb_list)
    for e in emb_sel:
        cant = st.number_input(f"¿Cuántas comidas de {e}?", min_value=1, value=1, key=f"emb_{e}")
        inventario_final.append({"Proteína": e, "Cat": "EMBUTIDOS", "Cantidad": cant})

with c5:
    pes_list = leer_pestaña(sheet_id, "PESCADO")
    pes_sel = st.multiselect(f"PESCADO (Necesitas {cuotas['PESCADO']})", options=pes_list)
    for pe in pes_sel:
        cant = st.number_input(f"¿Cuántas comidas de {pe}?", min_value=1, value=1, key=f"pes_{pe}")
        inventario_final.append({"Proteína": pe, "Cat": "PESCADO", "Cantidad": cant})

# 4. BOTÓN FINAL
if st.button("GENERAR MI LISTA FINAL"):
    st.markdown("### 🖨️ LISTA DE DISTRIBUCIÓN")
    if inventario_final:
        df_inv = pd.DataFrame(inventario_final)
        st.table(df_inv)
        
        total_p = df_inv["Cantidad"].sum()
        st.write(f"**Total de platos cubiertos:** {total_p} de {total_comidas}")
        
        # Check de balance
        if total_p < total_comidas:
            st.warning(f"⚠️ Te faltan cubrir {total_comidas - total_p} platos.")
        
        # Texto para descarga
        txt = f"PLAN DE PROTEÍNAS ({fecha_inicio} al {fecha_final})\n"
        txt += "="*40 + "\n"
        for item in inventario_final:
            txt += f"[ ] {item['Proteína']} - {item['Cantidad']} veces ({item['Cat']})\n"
        st.download_button("Descargar Plan para Imprimir", txt, "plan_comidas.txt")
