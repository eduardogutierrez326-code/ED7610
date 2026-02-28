import streamlit as st
import pandas as pd
import random
import re
from datetime import timedelta

st.set_page_config(page_title="Calendario de Ejecución", layout="wide")

st.title("📅 DISTRIBUIDOR DE MENÚ POR LISTA REAL")

# 1. CONFIGURACIÓN
st.sidebar.header("Configuración")
fecha_inicio = st.sidebar.date_input("Fecha de Inicio", value=pd.to_datetime("today"))
dias_plan = st.sidebar.number_input("Días a planear", min_value=1, value=15)
fecha_fin = fecha_inicio + timedelta(days=dias_plan-1)

st.subheader("1. Pega tu lista (HUEVO 1, HUEVO 2, etc.)")
datos_input = st.text_area("Copia y pega aquí:", height=250)

if st.button("GENERAR CALENDARIO"):
    if datos_input:
        inventario = []
        lineas = datos_input.strip().split('\n')
        
        for linea in lineas:
            linea_upper = linea.upper()
            
            # --- DETECTOR DE CATEGORÍAS ---
            # Ahora el HUEVO entra al inventario normal, no tiene regla aparte
            cat = "FUERTE" 
            if "HUEVO" in linea_upper: cat = "HUEVO"
            elif "CEMEX" in linea_upper: cat = "EMBUTIDOS"
            elif "RES" in linea_upper: cat = "RES"
            elif "CERDO" in linea_upper or "CHA " in linea_upper: cat = "CERDO"
            elif "POLLO" in linea_upper: cat = "POLLO"
            elif "PES" in linea_upper or "CAMARON" in linea_upper: cat = "PESCADO"

            # Limpiar nombre
            nombre = linea.replace("[ ]", "").split("(")[0].strip()
            
            # Detectar cuántos servicios
            cant_match = re.search(r'(\d+)\s+servicio', linea_upper)
            cant = int(cant_match.group(1)) if cant_match else 1
            
            # Metemos todo al mismo costal para repartir
            for _ in range(cant):
                inventario.append({"Platillo": nombre, "Cat": cat})

        # --- REGLAS DE DISTRIBUCIÓN LIMPIA ---
        # Mezclamos todo el inventario
        random.shuffle(inventario)
        
        # Priorizamos Embutidos y Huevos para el desayuno
        desayunables = [p for p in inventario if p['Cat'] in ['HUEVO', 'EMBUTIDOS']]
        platos_fuertes = [p for p in inventario if p['Cat'] not in ['HUEVO', 'EMBUTIDOS']]
        
        rango_fechas = pd.date_range(fecha_inicio, fecha_fin)
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
                # Si se acaban los huevos/embutidos, desayunamos lo que haya
                item = platos_fuertes.pop(0)
                desayuno = item['Platillo']
                cat_des = item['Cat']

            # --- ASIGNAR COMIDA ---
            comida = "Recalentado / Complemento"
            cat_com = "LIBRE"
            
            # Buscamos algo que no sea la misma proteína que el desayuno de hoy
            for idx, p in enumerate(platos_fuertes):
                if p['Cat'] != cat_des:
                    item = platos_fuertes.pop(idx)
                    comida = item['Platillo']
                    cat_com = item['Cat']
                    break
            
            # Si no encontramos algo diferente, tomamos lo que sea que quede
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
        df_final = pd.DataFrame(calendario)
        st.table(df_final)
        
    else:
        st.error("Pega la lista para organizar.")
