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
datos_input = st.text_area("Copia y pega la lista tal cual te la dio la otra app:", height=250)

if st.button("GENERAR CALENDARIO"):
    if datos_input:
        # --- NUEVO PROCESADOR DE TEXTO (Limpia los [ ] y detecta categoría) ---
        inventario = []
        lineas = datos_input.strip().split('\n')
        
        for linea in lineas:
            # Buscamos el platillo y la categoría usando expresiones regulares o limpieza simple
            # Formato esperado: [ ] PLATILLO - X veces (CATEGORIA)
            if "(" in linea and ")" in linea:
                # Extraer categoría entre paréntesis
                cat = linea.split('(')[-1].split(')')[0].strip().upper()
                # Extraer nombre del platillo (lo que está después del [ ] y antes del -)
                nombre = linea.replace("[ ]", "").split("-")[0].strip()
                # Extraer cantidad
                cant_match = re.search(r'(\d+)\s+veces', linea)
                cant = int(cant_match.group(1)) if cant_match else 1
                
                # Agregar al pool tantas veces como diga la cantidad
                for _ in range(cant):
                    inventario.append({"Platillo": nombre, "Cat": cat})

        # --- REGLAS DE DISTRIBUCIÓN ---
        # Separar huevos y embutidos
        embutidos = [p for p in inventario if p['Cat'] == 'EMBUTIDOS']
        # Proteínas para las comidas (Res, Pollo, Cerdo, Pescado)
        fuertes = [p for p in inventario if p['Cat'] in ['RES', 'POLLO', 'CERDO', 'PESCADO']]
        
        random.shuffle(fuertes)
        random.shuffle(embutidos)
        
        rango_fechas = pd.date_range(fecha_inicio, fecha_fin)
        calendario = []
        ultima_cat_dia_anterior = ""

        for i, fecha in enumerate(rango_fechas):
            # --- REGLA DESAYUNO ---
            desayuno = ""
            cat_des = ""
            
            # Huevo cada 2 días
            if i % 2 == 0:
                desayuno = "🍳 HUEVOS AL GUSTO"
                cat_des = "HUEVO"
            # Si no toca huevo, intentar Embutido
            elif embutidos:
                item = embutidos.pop(0)
                desayuno = f"🥪 {item['Platillo']}"
                cat_des = "EMBUTIDOS"
            # Si no hay embutidos, ver si queda algo fuerte
            elif fuertes:
                item = fuertes.pop(0)
                desayuno = f"🌅 {item['Platillo']}"
                cat_des = item['Cat']
            else:
                desayuno = "☕ Desayuno Ligero / Libre"
                cat_des = "LIBRE"

            # --- REGLA COMIDA ---
            comida = ""
            cat_com = ""
            
            # Buscamos en los fuertes uno que NO sea igual al desayuno de hoy
            p_encontrada = False
            for idx, p in enumerate(fuertes):
                if p['Cat'] != cat_des:
                    item = fuertes.pop(idx)
                    comida = f"🍲 {item['Platillo']}"
                    cat_com = item['Cat']
                    p_encontrada = True
                    break
            
            if not p_encontrada:
                comida = "🔄 Recalentado / Complemento"
                cat_com = "LIBRE"

            calendario.append({
                "Fecha": fecha.strftime('%d/%m'),
                "Día": fecha.strftime('%A'),
                "DESAYUNO": desayuno,
                "COMIDA": comida
            })

        # --- MOSTRAR RESULTADO ---
        st.markdown("---")
        df_final = pd.DataFrame(calendario)
        st.table(df_final)
        
        st.download_button("Descargar Calendario", df_final.to_csv(index=False).encode('utf-8'), "calendario.csv")
    else:
        st.error("Pega la lista de platillos para poder trabajar.")
