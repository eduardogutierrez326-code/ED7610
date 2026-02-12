import streamlit as st
import pandas as pd

st.set_page_config(page_title="Agenda de Sobres", layout="wide")

st.title("💰 MI AGENDA DE PRESUPUESTO (SOBRES)")
st.markdown("---")

sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
nombre_pestaña = "PRESUPUESTO"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(url)
        # Limpiar nombres de columnas: quitar espacios y pasar a mayúsculas
        df.columns = df.columns.str.strip().str.upper()
        
        # Estandarizar el nombre de la columna de fecha
        if 'FECHA DE PAGO' in df.columns:
            df = df.rename(columns={'FECHA DE PAGO': 'FECHA_REF'})
        elif 'FECHA' in df.columns:
            df = df.rename(columns={'FECHA': 'FECHA_REF'})
        else:
            df['FECHA_REF'] = "Sin fecha" # Por si se olvida poner la columna
            
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return pd.DataFrame()

df_presupuesto = cargar_datos()

# Solo avanzar si el DataFrame no está vacío
if not df_presupuesto.empty:
    # Verificar que exista la columna DP
    if 'DP' in df_presupuesto.columns:
        opciones_dp = sorted(df_presupuesto['DP'].unique())
        dp_seleccionado = st.selectbox("📅 ¿PARA QUÉ DÍA DE PAGO VAS A PREPARAR SOBRES?", opciones_dp)

        df_filtrado = df_presupuesto[df_presupuesto['DP'] == dp_seleccionado].copy()
        
        st.subheader(f"📋 Gastos para {dp_seleccionado}")
        
        gastos_finales = []
        
        with st.form("form_gastos"):
            for index, row in df_filtrado.iterrows():
                col_info, col_monto = st.columns([3, 1])
                
                with col_info:
                    # Mostramos Fecha, Concepto y Categoría en una sola línea
                    fecha_mostrar = row['FECHA_REF']
                    st.write(f"📅 **{fecha_mostrar}** | {row['CONCEPTO']} ({row['CATEGORIA']})")
                
                with col_monto:
                    # Si la cantidad es 0 o está vacía, pedimos el dato
                    monto_base = 0.0 if pd.isna(row['CANTIDAD']) else float(row['CANTIDAD'])
                    
                    if monto_base == 0:
                        nuevo_monto = st.number_input(f"Monto para {row['CONCEPTO']}", min_value=0.0, step=1.0, key=f"in_{index}")
                    else:
                        st.write(f"${monto_base:,.2f}")
                        nuevo_monto = monto_base
                
                gastos_finales.append({
                    "FECHA": fecha_mostrar,
                    "CONCEPTO": row['CONCEPTO'],
                    "CATEGORIA": row['CATEGORIA'],
                    "CANTIDAD": nuevo_monto
                })
                
            boton_calcular = st.form_submit_button("📊 GENERAR TOTALES")

        if boton_calcular:
            df_final = pd.DataFrame(gastos_finales)
            
            st.markdown("---")
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.subheader("📑 Lista Detallada")
                st.table(df_final)
                
            with c2:
                st.subheader("🛍️ Por Sobre")
                resumen = df_final.groupby("CATEGORIA")["CANTIDAD"].sum().reset_index()
                for _, r in resumen.iterrows():
                    st.metric(label=r['CATEGORIA'], value=f"${r['CANTIDAD']:,.2f}")
                
                total = df_final['CANTIDAD'].sum()
                st.divider()
                st.success(f"**RETIRAR DEL BANCO: ${total:,.2f}**")
    else:
        st.error("No encontré la columna 'DP' en tu Excel. Revisa que esté en la celda A1.")
else:
    st.info("Esperando datos del Excel...")
