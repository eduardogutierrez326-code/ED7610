import streamlit as st
import pandas as pd
import random
import re
from datetime import timedelta
import streamlit.components.v1 as components # Importante para el botón

st.set_page_config(page_title="Calendario de Ejecución", layout="wide")

# --- ESTILO PARA IMPRESIÓN ---
st.markdown("""
    <style>
    @media print {
        header, footer, .stSidebar, .stButton, .stTextArea, .stMarkdown, [data-testid="stHeader"], .print-btn-container {
            display: none !important;
        }
        .main .block-container {
            padding-top: 0rem !important;
            margin: 0 !important;
        }
        table { width: 100% !important; font-size: 12pt !important; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 DISTRIBUIDOR DE MENÚ")

# 1. ENTRADA DE FECHAS
st.sidebar.header("🗓️ Configuración")
fecha_inicio = st.sidebar.date_input("FECHA DE INICIO", value=pd.to_datetime("today"))
fecha_final = st.sidebar.date_input("FECHA FINAL", value=fecha_inicio + timedelta(days=13))

dias_totales = (fecha_final - fecha_inicio).days + 1
servicios_necesarios = dias_totales * 2

st.sidebar.metric("Días Totales", f"{dias_totales}")
st.sidebar.metric("Platos requeridos", f"{servicios_necesarios}")

# 2. CARGA DE DATOS
st.subheader("1. Pega tu lista de platillos")
datos_input = st.text_area("Copia y pega la lista aquí:", height=150)

if st.button("GENERAR CALENDARIO"):
    if datos_input:
        inventario = []
        lineas = datos_input.strip().split('\n')
        
        for linea in lineas:
            linea_upper = linea.upper()
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

        random.shuffle(inventario)
        desayunables = [p for p in inventario if p['Cat'] in ['HUEVO', 'EMBUTIDOS']]
        platos_fuertes = [p for p in inventario if p['Cat'] not in ['HUEVO', 'EMBUTIDOS']]
        
        rango_fechas = pd.date_range(fecha_inicio, fecha_final)
        calendario = []

        for i, fecha in enumerate(rango_fechas):
            desayuno = "Libre"; cat_des = "LIBRE"
            if desayunables:
                item = desayunables.pop(0); desayuno = item['Platillo']; cat_des = item['Cat']
            elif platos_fuertes:
                item = platos_fuertes.pop(0); desayuno = item['Platillo']; cat_des = item['Cat']

            comida = "Recalentado"
            encontrado = False
            for idx, p in enumerate(platos_fuertes):
                if p['Cat'] != cat_des:
                    item = platos_fuertes.pop(idx); comida = item['Platillo']; encontrado = True; break
            if not encontrado and platos_fuertes:
                item = platos_fuertes.pop(0); comida = item['Platillo']

            calendario.append({"Fecha": fecha.strftime('%d/%m'), "Día": fecha.strftime('%A'), "DESAYUNO": desayuno, "COMIDA": comida})

        st.markdown("---")
        st.markdown(f"## 📋 MENÚ DEL {fecha_inicio.strftime('%d/%m')} AL {fecha_final.strftime('%d/%m')}")
        
        df_final = pd.DataFrame(calendario)
        st.table(df_final)

        # --- BOTÓN DE IMPRESIÓN MEJORADO ---
        st.write("Presiona el botón de abajo para imprimir o guardar como PDF:")
        components.html("""
            <script>
                function imprimir() {
                    window.parent.print();
                }
            </script>
            <button onclick="imprimir()" style="background-color: #FF4B4B; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">
                🖨️ ABRIR VENTANA DE IMPRESIÓN (Ctrl+P)
            </button>
        """, height=70)
        
        st.download_button("📥 DESCARGAR EXCEL (CSV)", df_final.to_csv(index=False).encode('utf-8'), "menu.csv")
    else:
        st.error("Pega la lista para organizar.")
