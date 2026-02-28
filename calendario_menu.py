import streamlit as st
import pandas as pd
import random
import re
from datetime import timedelta

st.set_page_config(page_title="Calendario de Ejecución", layout="wide")

st.title("📅 DISTRIBUIDOR DE MENÚ POR LISTA REAL")

# 1. ENTRADA DE FECHAS (INICIO Y FIN)
st.sidebar.header("🗓️ Configuración del Periodo")
fecha_inicio = st.sidebar.date_input("FECHA DE INICIO", value=pd.to_datetime("today"))
fecha_final = st.sidebar.date_input("FECHA FINAL", value=fecha_inicio + timedelta(days=14))

# Cálculo de días y platos necesarios
dias_totales = (fecha_final - fecha_inicio).days + 1
servicios_necesarios = dias_totales * 2

st.sidebar.markdown("---")
st.sidebar.metric("Días Totales", f"{dias_totales} días")
st.sidebar.metric("Platos requeridos", f"{servicios_necesarios} platos")

if dias_totales <= 0:
    st.error("La fecha final debe ser posterior a la fecha de inicio.")

# 2. CARGA DE DATOS
st.subheader("1. Pega tu lista de platillos")
st.info(f"Para cubrir este periodo necesitas {servicios_necesarios} servicios en total.")
datos_input = st.text_area("Copia y pega la lista aquí:", height=250)

if st.button("GENERAR CALENDARIO"):
    if datos_input:
        inventario = []
        lineas = datos_input.strip().split('\n')
        
        for linea in lineas:
            linea_upper = linea.upper()
            
            # --- DETECTOR DE CATEGORÍAS ---
            cat = "FUERTE" 
            if "HUEVO" in linea_upper: cat = "HUEVO"
            elif "CEMEX" in linea_upper: cat = "EMBUTIDOS"
            elif "RES" in linea_upper: cat = "RES"
            elif "CERDO" in linea_upper or "CHA " in linea_upper: cat = "CERDO"
            elif "POLLO" in linea_upper: cat = "POLLO"
            elif "PES" in linea_upper or "CAMARON" in linea_upper: cat = "PESCADO"

            nombre = linea.replace("[ ]", "").split("(")[0].strip()
            
            cant_match = re.search(r'(\d+)\s+servicio', linea_upper)
            cant = int(cant_match.group(1)) if cant_match else 1
            
            for _ in range(cant):
                inventario.append({"Platillo": nombre, "Cat": cat})

        # --- REGLAS DE DISTRIBUCIÓN ---
        random.shuffle(inventario)
        
        # Separar para priorizar desayunos
        desayunables = [p for p in inventario if p['Cat'] in ['HUEVO', 'EMBUTIDOS']]
        platos_fuertes = [p for p in inventario if p['Cat'] not in ['HUEVO', 'EMBUTIDOS']]
        
        rango_fechas = pd.date_range(fecha_inicio, fecha_final)
        calendario = []

        for i, fecha in enumerate(rango_fechas):
            # --- ASIGNAR DESAYUNO ---
            desayuno = "Desayuno Libre"
            cat_des = "LIBRE"
            
            if desayunables:
                item = desayunables.pop(0)
                desayuno = item['Platillo']
                cat_des = item['Cat']
            elif platos_fuertes:
                item = platos_fuertes.pop(0)
                desayuno = item['Platillo']
                cat_des = item['Cat']

            # --- ASIGNAR COMIDA ---
            comida = "Recalentado / Complemento"
            cat_com = "LIBRE"
            
            for idx, p in enumerate(platos_fuertes):
                if p['Cat'] != cat_des:
                    item = platos_fuertes.pop(idx)
                    comida = item['Platillo']
                    cat_com = item['Cat']
                    break
            
            if comida == "Recalentado / Complemento" and platos_fuertes:
                item = platos_fuertes.pop(0)
                comida = item['Platillo']

            calendario.append({
                "Fecha": fecha.strftime('%d/%m'),
                "Día": fecha.strftime('%A'),
                "DESAYUNO": desayuno,
                "COMIDA": comida
            })

        # --- TABLA FINAL ---
        st.markdown("---")
        st.subheader(f"📋 Plan del {fecha_inicio.strftime('%d/%m')} al {fecha_final.strftime('%d/%m')}")
        df_final = pd.DataFrame(calendario)
        st.table(df_final)
        
        # Check de balance
        servicios_usados = len(inventario)
        if servicios_usados < servicios_necesarios:
            st.warning(f"⚠️ Nota: Solo tenías {servicios_usados} servicios para {servicios_necesarios} espacios. Los huecos se llenaron con 'Libre/Recalentado'.")
        
    else:
        st.error("Pega la lista para organizar el calendario.")
