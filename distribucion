import streamlit as st
import pandas as pd
import random
from datetime import timedelta

st.set_page_config(page_title="Calendario de Ejecución", layout="wide")

st.title("📅 DISTRIBUIDOR INTELIGENTE DE COMIDAS")
st.write("Esta app organiza tu inventario para que la dieta sea variada y rinda todo el periodo.")

# 1. ENTRADA DE DATOS (Simulando la recepción de la lista anterior)
# En un futuro podemos hacer que esta lista se cargue sola
st.sidebar.header("Configuración del Periodo")
fecha_inicio = st.sidebar.date_input("Fecha de Inicio", value=pd.to_datetime("today"))
dias_plan = st.sidebar.number_input("¿Cuántos días planear?", min_value=1, value=15)
fecha_fin = fecha_inicio + timedelta(days=dias_plan-1)

# Base de datos de ejemplo (Lo que vendría de tu App anterior)
# Aquí tú pegarías los platillos que elegiste
st.subheader("1. Carga de Inventario Seleccionado")
datos_input = st.text_area("Pega aquí tus platillos (Nombre, Categoría)", 
             placeholder="Ejemplo:\nBistec, RES\nChuleta, CERDO\nJamón, EMBUTIDOS")

# --- PROCESAMIENTO ---
if st.button("GENERAR CALENDARIO CRONOLÓGICO"):
    # Convertir el texto en una lista de trabajo
    lineas = datos_input.strip().split('\n')
    inventario = []
    for l in lineas:
        if ',' in l:
            p, c = l.split(',')
            inventario.append({"Platillo": p.strip(), "Cat": c.strip().upper()})

    # Separar por grupos para las reglas
    embutidos = [p for p in inventario if p['Cat'] == 'EMBUTIDOS']
    fuertes = [p for p in inventario if p['Cat'] in ['RES', 'POLLO', 'CERDO', 'PESCADO']]
    random.shuffle(fuertes) # Mezclar para que no sea siempre el mismo orden
    
    # Crear el rango de fechas
    rango_fechas = pd.date_range(fecha_inicio, fecha_fin)
    calendario = []
    
    ultima_cat_dia_anterior = ""

    for i, fecha in enumerate(rango_fechas):
        # --- REGLA DESAYUNO ---
        desayuno = ""
        cat_des = ""
        
        # A) Huevo cada dos días
        if i % 2 == 0:
            desayuno = "🍳 HUEVOS AL GUSTO"
            cat_des = "HUEVO"
        # B) Si no toca huevo, buscar Embutido
        elif embutidos:
            item = embutidos.pop(0)
            desayuno = f"🥪 {item['Platillo']}"
            cat_des = "EMBUTIDOS"
        # C) Si no hay nada de lo anterior, usar uno fuerte que no sea igual al del día anterior
        else:
            for idx, p in enumerate(fuertes):
                if p['Cat'] != ultima_cat_dia_anterior:
                    item = fuertes.pop(idx)
                    desayuno = f"🌅 {item['Platillo']}"
                    cat_des = p['Cat']
                    break

        # --- REGLA COMIDA ---
        comida = ""
        cat_com = ""
        
        # Buscar una proteína que NO sea la misma del desayuno de hoy
        for idx, p in enumerate(fuertes):
            if p['Cat'] != cat_des:
                item = fuertes.pop(idx)
                comida = f"🍲 {item['Platillo']}"
                cat_com = p['Cat']
                break
        
        if not comida: # Si se acaban los fuertes
            comida = "🔄 Recalentado / Libre"
            cat_com = "LIBRE"

        calendario.append({
            "Día": fecha.strftime('%d/%m'),
            "Nombre Día": fecha.strftime('%A'),
            "DESAYUNO": desayuno,
            "COMIDA (ALMUERZO)": comida
        })
        
        ultima_cat_dia_anterior = cat_com

    # --- RESULTADO ---
    st.markdown("---")
    st.subheader("📋 Tu Menú Programado")
    df_cal = pd.DataFrame(calendario)
    
    # Estilo para la tabla
    st.table(df_cal)
    
    # Opción de descarga
    csv = df_cal.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Calendario", csv, "calendario_comidas.csv", "text/csv")
