import streamlit as st
import pandas as pd

st.set_page_config(page_title="Agenda de Sobres", layout="wide")

# Título y Estilo
st.title("💰 MI AGENDA DE PRESUPUESTO (SOBRES)")
st.markdown("---")

# 1. CONEXIÓN A LA PESTAÑA DE PRESUPUESTO
sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
nombre_pestaña = "PRESUPUESTO"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(url)
        # Limpiamos nombres de columnas por si hay espacios
        df.columns = df.columns.str.strip()
        return df
    except:
        st.error("No pude leer la pestaña 'PRESUPUESTO'. Revisa el nombre en tu Excel.")
        return pd.DataFrame()

df_presupuesto = cargar_datos()

if not df_presupuesto.empty:
    # 2. SELECCIÓN DE DÍA DE PAGO (DP)
    opciones_dp = sorted(df_presupuesto['DP'].unique())
    dp_seleccionado = st.selectbox("📅 ¿PARA QUÉ DÍA DE PAGO VAS A PREPARAR SOBRES?", opciones_dp)

    # Filtrar datos por el DP elegido
    df_filtrado = df_presupuesto[df_presupuesto['DP'] == dp_seleccionado].copy()
    
    st.subheader(f"📋 Gastos programados para {dp_seleccionado}")
    st.info("Si un gasto aparece en $0.0, ingresa la cantidad actual abajo.")

    # 3. FORMULARIO PARA AJUSTAR CANTIDADES (Variables)
    gastos_finales = []
    
    with st.form("form_gastos"):
        for index, row in df_filtrado.iterrows():
            col_fecha, col_con, col_cat, col_monto = st.columns([1.5, 2, 2, 1.5])
            
            with col_fecha:
                st.write(f"📅 {row['FECHA DE PAGO']}")
            with col_con:
                st.write(f"**{row['CONCEPTO']}**")
            with col_cat:
                st.caption(f"📁 {row['CATEGORIA']}")
            with col_monto:
                # Si el monto es 0, pedimos la cantidad. Si no, usamos la del Excel.
                if row['CANTIDAD'] == 0:
                    nuevo_monto = st.number_input(f"Monto para {row['CONCEPTO']}", min_value=0.0, step=10.0, key=f"input_{index}")
                else:
                    st.write(f"${row['CANTIDAD']:,.2f}")
                    nuevo_monto = row['CANTIDAD']
            
            gastos_finales.append({
                "FECHA": row['FECHA DE PAGO'],
                "CONCEPTO": row['CONCEPTO'],
                "CATEGORIA": row['CATEGORIA'],
                "CANTIDAD": nuevo_monto
            })
            
        boton_calcular = st.form_submit_button("📊 CALCULAR TOTALES PARA SOBRES")

    # 4. RESULTADOS Y RESUMEN POR SOBRE
    if boton_calcular:
        df_final = pd.DataFrame(gastos_finales)
        
        st.markdown("---")
        col_res1, col_res2 = st.columns([2, 1])
        
        with col_res1:
            st.subheader("📑 Detalle de Salidas")
            st.table(df_final.sort_values(by="FECHA"))
            
        with col_res2:
            st.subheader("🛍️ Llenado de Sobres")
            resumen_sobres = df_final.groupby("CATEGORIA")["CANTIDAD"].sum().reset_index()
            for i, r in resumen_sobres.iterrows():
                st.metric(label=r['CATEGORIA'], value=f"${r['CANTIDAD']:,.2f}")
            
            gran_total = df_final['CANTIDAD'].sum()
            st.warning(f"### **TOTAL A SACAR DEL BANCO: ${gran_total:,.2f}**")

        # 5. BOTÓN DE DESCARGA
        txt_output = f"AGENDA DE GASTOS - {dp_seleccionado}\n"
        txt_output += "="*40 + "\n"
        for i, r in df_final.iterrows():
            txt_output += f"[{r['FECHA']}] {r['CONCEPTO']} ({r['CATEGORIA']}): ${r['CANTIDAD']:,.2f}\n"
        txt_output += "="*40 + "\n"
        txt_output += f"TOTAL GENERAL: ${gran_total:,.2f}"
        
        st.download_button("📥 Descargar Guía para Sobres", txt_output, f"presupuesto_{dp_seleccionado}.txt")

else:
    st.warning("Aún no hay datos en la pestaña 'PRESUPUESTO'. Agrega tus gastos fijos primero.")
