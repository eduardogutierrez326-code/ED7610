import streamlit as st
import pandas as pd
import random
import re
from datetime import timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="Distribuidor 32 Platillos", layout="wide")

# --- ESTILO PARA IMPRESIÓN ---
st.markdown("""
    <style>
    @media print {
        html, body, .main, .block-container { background-color: white !important; color: black !important; }
        header, footer, .stSidebar, .stButton, .stTextArea, [data-testid="stHeader"] { display: none !important; }
        table { width: 100% !important; border-collapse: collapse !important; }
        th { background-color: #f0f0f0 !important; border: 1px solid #ddd !important; }
        td { border: 1px solid #ddd !important; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 DISTRIBUIDOR INTELIGENTE (Balance 32)")

# 1. CONFIGURACIÓN DE METAS (Lo que pidió tu esposa)
meta = {
    "RES": 6, "CERDO": 6, "POLLO": 6, 
    "EMBUTIDOS": 6, "HUEVO": 5, "PESCADO": 3
}

# 2. FECHAS
st.sidebar.header("🗓️ Rango de 16 días")
fecha_inicio = st.sidebar.date_input("INICIO", value=pd.to_datetime("today"))
fecha_final = fecha_inicio + timedelta(days=15) # Forzamos 16 días para los 32 platos
st.sidebar.write(f"Finaliza el: **{fecha_final.strftime('%d/%m/%Y')}**")

# 3. CARGA Y FILTRO
st.subheader("1. Pega tu lista completa aquí")
datos_input = st.text_area("Lista de la App de Presupuesto:", height=200)

if st.button("GENERAR CALENDARIO EQUILIBRADO"):
    if datos_input:
        pool_sucio = []
        lineas = datos_input.strip().split('\n')
        
        # Procesar cada línea y asignar categoría
        for linea in lineas:
            l = linea.upper()
            cat = "OTRO"
            if "RES" in l: cat = "RES"
            elif "CERDO" in l or "CHA " in l: cat = "CERDO"
            elif "POLLO" in l: cat = "POLLO"
            elif "CEMEX" in l or "EMBUTIDO" in l: cat = "EMBUTIDOS"
            elif "HUEVO" in l: cat = "HUEVO"
            elif "PES" in l or "CAMARON" in l or "ATUN" in l: cat = "PESCADO"
            
            nombre = linea.replace("[ ]", "").split("(")[0].strip()
            pool_sucio.append({"nombre": nombre, "cat": cat})

        # --- FILTRO ESTRICTO DE CANTIDADES ---
        inventario_final = []
        for categoria, limite in meta.items():
            platos_de_esta_cat = [p for p in pool_sucio if p['cat'] == categoria]
            # Solo tomamos hasta el límite que pidió tu esposa (6, 5 o 3)
            inventario_final.extend(platos_de_esta_cat[:limite])

        # Verificación
        if len(inventario_final) < 32:
            st.warning(f"⚠️ Tu lista solo tiene {len(inventario_final)} platos válidos. Faltan {32 - len(inventario_final)} para completar la meta de 32.")
        
        random.shuffle(inventario_final)
        
        # Separar para el orden de las comidas
        desayunos = [p for p in inventario_final if p['cat'] in ['HUEVO', 'EMBUTIDOS']]
        comidas = [p for p in inventario_final if p['cat'] not in ['HUEVO', 'EMBUTIDOS']]
        
        rango = pd.date_range(fecha_inicio, fecha_final)
        calendario = []

        for i, fecha in enumerate(rango):
            # Desayuno
            platillo_d = desayunos.pop(0) if desayunos else (comidas.pop(0) if comidas else {"nombre": "Libre", "cat": "X"})
            
            # Comida (que no sea la misma proteína)
            platillo_c = {"nombre": "Recalentado", "cat": "X"}
            for idx, p in enumerate(comidas):
                if p['cat'] != platillo_d['cat']:
                    platillo_c = comidas.pop(idx)
                    break
            if platillo_c['nombre'] == "Recalentado" and comidas:
                platillo_c = comidas.pop(0)

            calendario.append({
                "Fecha": fecha.strftime('%d/%m'),
                "Día": fecha.strftime('%A'),
                "DESAYUNO": platillo_d['nombre'],
                "COMIDA": platillo_c['nombre']
            })

        # MOSTRAR
        st.table(pd.DataFrame(calendario))
        
        components.html("""
            <script>function imprimir(){window.parent.print();}</script>
            <button onclick="imprimir()" style="background-color: #FF4B4B; color: white; padding: 15px; border: none; border-radius: 8px; width: 100%; cursor: pointer;">
               🖨️ IMPRIMIR MENÚ BALANCEADO (32 PLATOS)
            </button>
        """, height=80)
