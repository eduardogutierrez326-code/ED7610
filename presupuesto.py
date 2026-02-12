import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Agenda de Sobres", layout="wide")

st.title("💰 MI AGENDA DE PRESUPUESTO (SOBRES)")
st.markdown("---")

sheet_id = "16QwtVN98phyUd-O1piuR9GnM0BLlcdtjEMM_ozhiXew"
nombre_pestaña = "PRESUPUESTO"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"

def cargar_datos():
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.upper()
        if 'DP' in df.columns:
            df['DP'] = df['DP'].astype(str).str.strip().str.upper()
        
        # Estandarizar columna de FECHA
        if 'FECHA DE PAGO' in df.columns:
            df = df.rename(columns={'FECHA DE PAGO': 'FECHA_REF'})
        elif 'FECHA' in df.columns:
            df = df.rename(columns={'FECHA': 'FECHA_REF'})
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return pd.DataFrame()

df_presupuesto = cargar_datos()

if not df_presupuesto.empty:
    if 'DP' in df_presupuesto.columns:
        opciones_dp = sorted([x for x in df_presupuesto['DP'].unique() if str(x) != 'nan'])
        dp_seleccionado = st.selectbox("📅 SELECCIONA TU DÍA DE PAGO", opciones_dp)

        df_filtrado = df_presupuesto[df_presupuesto['DP'] == dp_seleccionado].copy()
        
        if df_filtrado.empty:
            st.warning(f"No hay datos para {dp_seleccionado}")
        else:
            st.subheader(f"📋 Ajusta Fechas y Montos para {dp_seleccionado}")
            
            gastos_finales = []
            with st.form("form_gastos"):
                for index, row in df_filtrado.iterrows():
                    col_fecha, col_concepto, col_monto = st.columns([2, 3, 2])
                    
                    with col_fecha:
                        # Intentamos leer la fecha del Excel, si falla usamos hoy
                        try:
                            fecha_default = pd.to_datetime(row['FECHA_REF'], dayfirst=True)
                        except:
                            fecha_default = datetime.now()
                        
                        nueva_fecha = st.date_input(f"Fecha para {row['CONCEPTO']}", value=fecha_default, key=f"date_{index}")
                    
                    with col_concepto:
                        st.write(f"**{row['CONCEPTO']}**")
                        st.caption(f"Categoría: {row['CATEGORIA']}")
                    
                    with col_monto:
                        try:
                            monto_base = float(row['CANTIDAD']) if pd.notnull(row['CANTIDAD']) else 0.0
                        except:
                            monto_base = 0.0
                        
                        if monto_base == 0:
                            valor_monto = st.number_input(f"Monto para {row['CONCEPTO']}", min_value=0.0, step=1.0, key=f"in_{index}")
                        else:
                            st.write(f"Fijo: ${monto_base:,.2f}")
                            valor_monto = monto_base
                    
                    gastos_finales.append({
                        "FECHA": nueva_fecha.strftime('%d/%m/%Y'),
                        "CONCEPTO": row['CONCEPTO'],
                        "CATEGORIA": row['CATEGORIA'],
                        "CANTIDAD": valor_monto
                    })
                
                boton_calcular = st.form_submit_button("📊 GENERAR TOTALES Y SOBRES")

            if boton_calcular:
                df_final = pd.DataFrame(gastos_finales)
                st.markdown("---")
                c1, c2 = st.columns([2, 1])
                
                with c1:
                    st.subheader("📑 Agenda Final de Pagos")
                    # Ordenar por fecha para que sea una agenda real
                    df_final['FECHA_DT'] = pd.to_datetime(df_final['FECHA'], dayfirst=True)
                    st.table(df_final.sort_values('FECHA_DT')[['FECHA', 'CONCEPTO', 'CATEGORIA', 'CANTIDAD']])
                
                with c2:
                    st.subheader("🛍️ Llenado de Sobres")
                    resumen = df_final.groupby("CATEGORIA")["CANTIDAD"].sum().reset_index()
                    for _, r in resumen.iterrows():
                        st.metric(label=r['CATEGORIA'], value=f"${r['CANTIDAD']:,.2f}")
                    
                    total = df_final['CANTIDAD'].sum()
                    st.divider()
                    st.success(f"**TOTAL BANCO: ${total:,.2f}**")
    else:
        st.error("No se encontró la columna 'DP'.")
else:
    st.info("Actualiza tu Excel y recarga la App.")
