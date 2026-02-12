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
        opciones_dp = sorted([x for x in df_presupuesto['DP'].unique() if str(x).lower() != 'nan'])
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
                        fecha_valida = datetime.now()
                        if 'FECHA_REF' in row and pd.notnull(row['FECHA_REF']):
                            try:
                                fecha_valida = pd.to_datetime(row['FECHA_REF'], dayfirst=True).to_pydatetime()
                            except:
                                fecha_valida = datetime.now()
                        nueva_fecha = st.date_input(f"Fecha: {row['CONCEPTO']}", value=fecha_valida, key=f"date_{index}")
                    
                    with col_concepto:
                        st.write(f"**{row['CONCEPTO']}**")
                        cat = row['CATEGORIA'] if pd.notnull(row['CATEGORIA']) else "Sin Categoría"
                        st.caption(f"Categoría: {cat}")
                    
                    with col_monto:
                        try:
                            valor_limpio = str(row['CANTIDAD']).replace('$', '').replace(',', '').strip()
                            monto_base = float(valor_limpio) if valor_limpio != 'nan' else 0.0
                        except:
                            monto_base = 0.0
                        
                        if monto_base <= 0:
                            valor_monto = st.number_input(f"Monto para {row['CONCEPTO']}", min_value=0.0, step=1.0, key=f"in_{index}")
                        else:
                            st.write(f"Fijo: ${monto_base:,.2f}")
                            valor_monto = monto_base
                    
                    gastos_finales.append({
                        "FECHA": nueva_fecha.strftime('%d/%m/%Y'),
                        "CONCEPTO": row['CONCEPTO'],
                        "CATEGORIA": cat,
                        "CANTIDAD": valor_monto,
                        "FECHA_OBJ": nueva_fecha
                    })
                
                boton_calcular = st.form_submit_button("📊 GENERAR TOTALES Y SOBRES")

            if boton_calcular:
                df_final = pd.DataFrame(gastos_finales).sort_values('FECHA_OBJ')
                total_general = df_final['CANTIDAD'].sum()
                
                st.markdown("---")
                st.success(f"### 💳 TOTAL A RETIRAR: ${total_general:,.2f}")
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.subheader("📑 Agenda de Pagos")
                    st.table(df_final[['FECHA', 'CONCEPTO', 'CATEGORIA', 'CANTIDAD']])
                
                with c2:
                    st.subheader("🛍️ Llenado de Sobres")
                    resumen = df_final.groupby("CATEGORIA")["CANTIDAD"].sum().reset_index()
                    for _, r in resumen.iterrows():
                        st.metric(label=r['CATEGORIA'], value=f"${r['CANTIDAD']:,.2f}")

                # --- GENERAR TEXTO PARA DESCARGA ---
                reporte = f"AGENDA DE GASTOS - {dp_seleccionado}\n"
                reporte += f"Fecha de creación: {datetime.now().strftime('%d/%m/%Y')}\n"
                reporte += "-"*40 + "\n"
                for _, r in df_final.iterrows():
                    reporte += f"[{r['FECHA']}] {r['CONCEPTO']} ({r['CATEGORIA']}): ${r['CANTIDAD']:,.2f}\n"
                reporte += "-"*40 + "\n"
                reporte += "RESUMEN DE SOBRES:\n"
                for _, r in resumen.iterrows():
                    reporte += f"- {r['CATEGORIA']}: ${r['CANTIDAD']:,.2f}\n"
                reporte += "-"*40 + "\n"
                reporte += f"TOTAL A RETIRAR: ${total_general:,.2f}"

                st.download_button(
                    label="📥 Descargar Agenda para Imprimir",
                    data=reporte,
                    file_name=f"Agenda_{dp_seleccionado}.txt",
                    mime="text/plain"
                )
    else:
        st.error("No encontré la columna 'DP'.")
else:
    st.info("Conectando con Google Sheets...")
