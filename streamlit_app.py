import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="PLANEADOR AUTOMÁTICO", layout="wide")
st.title("🍽️ ASIGNADOR DE MENÚ (CONTROL DE GASTO)")

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

# 2. CUOTAS FIJAS (Basadas en tus porcentajes de ahorro)
porc_config = {
    "RES": 0.20, "CERDO": 0.25, "HUEVO": 0.15, 
    "POLLO": 0.15, "PESCADO": 0.05, "EMBUTIDOS": 0.15
}

cuotas = {cat: round(total_comidas * p) for cat, p in porc_config.items()}

# Mostrar métricas de cuotas
st.subheader(f"📊 Tienes {total_comidas} platos para asignar")
cols = st.columns(6)
for i, (cat, cant) in enumerate(cuotas.items()):
    cols[i].metric(cat, f"{cant} platos")

# 3. FUNCIÓN DE LECTURA
def leer_pestaña(sheet_id, nombre_pestaña):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
    try:
        df = pd.read_csv(url)
        return df.iloc[:, 0].dropna().unique().tolist()
    except:
        return []

sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"

st.markdown("---")
st.subheader("📝 Arma tu menú (1 platillo = 1 unidad)")

inventario_final = []

# Autocompletar HUEVOS
if cuotas["HUEVO"] > 0:
    inventario_final.append({"Platillo": "HUEVOS (Varios estilos)", "Categoría": "HUEVO", "Cantidad": cuotas["HUEVO"]})
    st.success(f"🥚 {cuotas['HUEVO']} servicios de Huevo asignados automáticamente.")

# SELECTORES SIN ENTRADA MANUAL DE NÚMEROS
c1, c2, c3 = st.columns(3)

with c1:
    res_list = leer_pestaña(sheet_id, "RES")
    res_sel = st.multiselect(f"RES (Elige {cuotas['RES']} platillos)", options=res_list)
    for r in res_sel:
        inventario_final.append({"Platillo": r, "Categoría": "RES", "Cantidad": 1})

with c2:
    cerdo_list = leer_pestaña(sheet_id, "CERDO")
    cerdo_sel = st.multiselect(f"CERDO (Elige {cuotas['CERDO']} platillos)", options=cerdo_list)
    for c in cerdo_sel:
        inventario_final.append({"Platillo": c, "Categoría": "CERDO", "Cantidad": 1})

with c3:
    pollo_list = leer_pestaña(sheet_id, "POLLO")
    pollo_sel = st.multiselect(f"POLLO (Elige {cuotas['POLLO']} platillos)", options=pollo_list)
    for p in pollo_sel:
        inventario_final.append({"Platillo": p, "Categoría": "POLLO", "Cantidad": 1})

c4, c5 = st.columns(2)
with c4:
    emb_list = leer_pestaña(sheet_id, "EMBUTIDOS")
    emb_sel = st.multiselect(f"EMBUTIDOS (Elige {cuotas['EMBUTIDOS']} platillos)", options=emb_list)
    for e in emb_sel:
        inventario_final.append({"Platillo": e, "Categoría": "EMBUTIDOS", "Cantidad": 1})

with c5:
    pes_list = leer_pestaña(sheet_id, "PESCADO")
    pes_sel = st.multiselect(f"PESCADO (Elige {cuotas['PESCADO']} platillos)", options=pes_list)
    for pe in pes_sel:
        inventario_final.append({"Platillo": pe, "Categoría": "PESCADO", "Cantidad": 1})

# 4. VALIDACIÓN Y GENERACIÓN
st.markdown("---")
if st.button("FINALIZAR Y GENERAR LISTA"):
    if inventario_final:
        df_resumen = pd.DataFrame(inventario_final)
        
        # Agrupar por si eligieron el mismo platillo varias veces
        df_final = df_resumen.groupby(['Platillo', 'Categoría']).sum().reset_index()
        
        st.table(df_final)
        
        total_asignado = df_final["Cantidad"].sum()
        
        if total_asignado > total_comidas:
            st.error(f"🚨 Te pasaste por {total_asignado - total_comidas} platos. Revisa tus selecciones.")
        elif total_asignado < total_comidas:
            st.warning(f"⚠️ Te faltan {total_comidas - total_asignado} platos por asignar.")
        else:
            st.success("🎯 ¡Perfecto! Menú completo y dentro del presupuesto.")

        # Texto para descarga
        txt = f"LISTA DE COCINA ({fecha_inicio} al {fecha_final})\n"
        txt += "="*40 + "\n"
        for _, row in df_final.iterrows():
            txt += f"[ ] {row['Platillo']} ({row['Cantidad']} servicios)\n"
        
        st.download_button("Descargar Plan", txt, "plan_cocina.txt")
