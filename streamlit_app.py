 # Reemplazaríamos la sección 2 del código anterior con esto:

st.subheader("📊 Simulador de Cuotas (Ajusta para ahorrar)")

# Creamos controles para que tú mismo muevas los porcentajes
col_a, col_b = st.columns(2)
with col_a:
    p_res = st.slider("Porcentaje de RES", 0, 100, 30) / 100
    p_cerdo = st.slider("Porcentaje de CERDO", 0, 100, 25) / 100
    p_huevo = st.slider("Porcentaje de HUEVO", 0, 100, 15) / 100
with col_b:
    p_pollo = st.slider("Porcentaje de POLLO", 0, 100, 15) / 100
    p_embutidos = st.slider("Porcentaje de EMBUTIDOS", 0, 100, 10) / 100
    p_pescado = st.slider("Porcentaje de PESCADO", 0, 100, 5) / 100

total_p = p_res + p_cerdo + p_huevo + p_pollo + p_embutidos + p_pescado

if total_p != 1.0:
    st.error(f"⚠️ El total debe sumar 100%. Actualmente suma: {total_p*100:.0f}%")
else:
    st.success("✅ Distribución equilibrada.")

# Los nuevos porcentajes calculados
porc_config = {
    "RES": p_res, "CERDO": p_cerdo, "HUEVO": p_huevo, 
    "POLLO": p_pollo, "PESCADO": p_pescado, "EMBUTIDOS": p_embutidos
}
