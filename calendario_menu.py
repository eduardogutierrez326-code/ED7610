import streamlit as st
import pandas as pd
import random
import re
from datetime import timedelta

st.set_page_config(page_title="Calendario de Ejecución", layout="wide")

st.title("📅 DISTRIBUIDOR INTELIGENTE DE COMIDAS")

# 1. CONFIGURACIÓN
st.sidebar.header("Configuración")
fecha_inicio = st.sidebar.date_input("Fecha de Inicio", value=pd.to_datetime("today"))
dias_plan = st.sidebar.number_input("Días a planear", min_value=1, value=15)
fecha_fin = fecha_inicio + timedelta(days=dias_plan-1)

st.subheader("1. Pega aquí tu lista de la App anterior")
datos_input = st.text_area("Copia y pega la lista generada:", height=250)

if st.button("GENERAR CALENDARIO"):
    if datos_input:
        inventario = []
        lineas = datos_input.strip().split('\n')
        
        for linea in lineas:
            linea_upper = linea.upper()
            
            # --- DETECTOR INTELIGENTE DE CATEGORÍAS ---
            cat = "FUERTE" # Default
            if "HUEVO" in linea_upper: cat = "HUEVO"
            elif "CEMEX" in linea_upper: cat = "EMBUTIDOS"
            elif "RES" in linea_upper: cat = "RES"
            elif "CERDO" in linea_upper or "CHA " in linea_upper: cat = "CERDO"
            elif "POLLO" in linea_upper: cat = "POLLO"
            elif "PES" in linea_upper or "CAMARON" in linea_upper: cat = "PESCADO"

            # Extraer el nombre del platillo
            nombre = linea.replace("[ ]", "").split("(")[0].strip()
            
            # Extraer cantidad de servicios
            cant_match = re.search(r'(\d+)\s+servicio', linea_upper)
            cant = int(cant_match.group(1)) if cant_match else 1
            
            # Si es huevo, no lo metemos al pool de "fuertes" porque tiene su propia regla
            if cat != "HUEVO":
                for _ in range(cant):
                    inventario.append({"Platillo": nombre, "Cat": cat})

        # --- REGLAS DE DISTRIBUCIÓN ---
        embutidos = [p for p in inventario if p['Cat'] == 'EMBUTIDOS']
        fuertes = [p for p in inventario if p['Cat'] != 'EMBUTIDOS']
        
        random.shuffle(fuertes)
        random.shuffle(embutidos)
        
        rango_fechas = pd.date_range(fecha_inicio, fecha_fin)
        calendario = []

        for i, fecha in enumerate(rango_fechas):
            # --- REGLA DESAYUNO ---
            desayuno = ""
            cat_des = ""
            
            if i % 2 == 0: # Día sí, día no
                desayuno = "🍳 HUEVOS AL GUSTO"
                cat_des = "HUEVO"
            elif embutidos:
                item = embutidos.pop(0)
                desayuno = f"🥪 {item['Platillo']}"
                cat_des = "EMBUTIDOS"
            elif fuertes:
                item = fuertes.pop(0)
                desayuno = f"🌅 {item['Platillo']}"
                cat_des = item['Cat']
            else:
                desayuno = "☕ Desayuno Ligero"

            # --- REGLA COMIDA ---
            comida = ""
            cat_com = ""
            
            encontrado = False
            for idx, p in enumerate(fuertes):
                if p['Cat'] != cat_des: # Que no se repita proteína en el mismo día
                    item = fuertes.pop(idx)
                    comida = f"🍲 {item['Platillo']}"
                    cat_com = item['Cat']
                    encontrado = True
                    break
            
            if not encontrado:
                comida = "🔄 Recalentado / Complemento"

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
        st.error("Por favor pega la lista primero.")
