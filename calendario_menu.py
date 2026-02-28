import streamlit as st
import pandas as pd
import random  # <--- ESTO ES LO QUE FALTABA
from datetime import timedelta

st.set_page_config(page_title="Calendario de Ejecución", layout="wide")

st.title("📅 DISTRIBUIDOR INTELIGENTE DE COMIDAS")
st.info("Reglas: Huevo cada 2 días, Embutidos en desayuno, No repetir proteína el mismo día.")

# 1. CONFIGURACIÓN DEL PERIODO
st.sidebar.header("Configuración")
fecha_inicio = st.sidebar.date_input("Fecha de Inicio", value=pd.to_datetime("today"))
dias_plan = st.sidebar.number_input("Días a planear", min_value=1, value=15)
fecha_fin = fecha_inicio + timedelta(days=dias_plan-1)

# 2. CARGA DE DATOS
st.subheader("1. Pega aquí tu lista de la App anterior")
st.write("Formato: Platillo, CATEGORÍA (Ej: Milanesa, RES)")
datos_input = st.text_area("Lista de Platillos:", height=200)

if st.button("GENERAR CALENDARIO"):
    if datos_input:
        # Procesar texto a lista
        lineas = datos_input.strip().split('\n')
        inventario = []
        for l in lineas:
            if ',' in l:
                p, c = l.split(',')
                inventario.append({"Platillo": p.strip(), "Cat": c.strip().upper()})

        # --- LÓGICA DE DISTRIBUCIÓN POR BLOQUES (MITAD Y MITAD) ---
        huevos = [p for p in inventario if p['Cat'] == 'HUEVO']
        embutidos = [p for p in inventario if p['Cat'] == 'EMBUTIDOS']
        fuertes = [p for p in inventario if p['Cat'] in ['RES', 'POLLO', 'CERDO', 'PESCADO']]
        
        # Mezclamos los fuertes para que no sea siempre el mismo orden
        random.shuffle(fuertes)
        
        # Dividimos en dos bloques (Semana 1 y Semana 2)
        mitad = len(fuertes) // 2
        bloque1 = fuertes[:mitad]
        bloque2 = fuertes[mitad:]
        
        rango_fechas = pd.date_range(fecha_inicio, fecha_fin)
        calendario = []
        ultima_cat_dia_anterior = ""

        for i, fecha in enumerate(rango_fechas):
            # Usar bloque 1 los primeros 7 días, luego bloque 2
            pool_actual = bloque1 if i < 7 else bloque2
            
            # --- REGLA DESAYUNO ---
            if i % 2 == 0:
                desayuno = "🍳 HUEVOS AL GUSTO"
                cat_des = "HUEVO"
            elif embutidos:
                item = embutidos.pop(0)
                desayuno = f"🥪 {item['Platillo']}"
                cat_des = "EMBUTIDOS"
            else:
                # Si no hay embutidos, tomamos uno fuerte
                if pool_actual:
                    item = pool_actual.pop(0)
                    desayuno = f"🌅 {item['Platillo']}"
                    cat_des = item['Cat']
                else:
                    desayuno = "Libre / Recalentado"
                    cat_des = "LIBRE"

            # --- REGLA COMIDA (Evitar repetición) ---
            comida = "Pendiente"
            cat_com = ""
            
            for idx, p in enumerate(pool_actual):
                if p['Cat'] != cat_des: # Que no sea la misma del desayuno
                    item = pool_actual.pop(idx)
                    comida = f"🍲 {item['Platillo']}"
                    cat_com = item['Cat']
                    break
            
            if comida == "Pendiente":
                comida = "🔄 Recalentado o Complemento"

            calendario.append({
                "Fecha": fecha.strftime('%d/%m'),
                "Día": fecha.strftime('%A'),
                "DESAYUNO": desayuno,
                "COMIDA": comida
            })
            ultima_cat_dia_anterior = cat_com

        # --- MOSTRAR TABLA ---
        st.markdown("---")
        df_final = pd.DataFrame(calendario)
        st.table(df_final)
        
        # Descarga
        st.download_button("Descargar Calendario (CSV)", df_final.to_csv(index=False).encode('utf-8'), "calendario.csv")
    else:
        st.error("Por favor, pega la lista de platillos primero.")
