import streamlit as st
import pandas as pd

# Función para limpiar y convertir a número
def clean_currency(value):
    if isinstance(value, str):
        # Quita el signo $, las comas y espacios
        return value.replace('$', '').replace(',', '').strip()
    return value

# Cargar datos
@st.cache_data
def load_data():
    # URL de exportación de tu hoja
    sheet_id = "1K0oQeGA2T5hyd5CoAq6erWV-br0hQj_rdZe-HH3LMSw"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    df = pd.read_csv(url)
    # Limpia los nombres de las columnas (quita espacios invisibles)
    df.columns = df.columns.str.strip()
    
    # Convierte la columna de dinero a números reales
    if 'CANTIDAD' in df.columns:
        df['CANTIDAD'] = df['CANTIDAD'].apply(clean_currency)
        df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0)
    
    # Asegura que DP sea número entero
    if 'DP' in df.columns:
        df['DP'] = pd.to_numeric(df['DP'], errors='coerce').fillna(0).astype(int)
        
    return df

# ... resto del código de la App igual al anterior ...
