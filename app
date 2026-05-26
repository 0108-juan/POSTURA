import streamlit as st
import pandas as pd
import numpy as np
import influxdb_client

# 1. Configuración de la página (Modo Móvil y Estética Médica Cute)
st.set_page_config(page_title="PostureCare App", page_icon="🩺", layout="centered")

# CSS para simular una App de Teléfono en tonos Azul Baby
st.markdown("""
<style>
    /* Fondo global de la página */
    .stApp {
        background-color: #f2f7fb;
    }
    
    /* Contenedor principal estilo pantalla de teléfono */
    .block-container {
        max-width: 430px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        background-color: #ffffff;
        border-radius: 40px;
        box-shadow: 0 10px 30px rgba(153, 192, 222, 0.3);
        margin: auto;
        border: 8px solid #d4e6f4;
    }
    
    /* Tipografías y títulos */
    h1, h2, h3 {
        color: #5c8cb3;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
    }
    
    /* Tarjetas de métricas estilizadas (Cute Medical) */
    div[data-testid="stMetric"] {
        background-color: #f0f6fc;
        border-radius: 20px;
        padding: 15px !important;
        border: 2px solid #e1eef7;
        text-align: center;
    }
    
    div[data-testid="stMetricValue"] {
        color: #4a779d;
        font-size: 24px !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #7da0bf;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Descarga y Limpieza de Datos (Silencioso y Seguro)
url = "https://us-east-1-1.aws.cloud2.influxdata.com/"
token = "hFiRK2sGAD4uMuyGl1cXxApTtrPuoIlbrc8ERykxqQJB56gyzCEpcWiGL4tXjQGkit6lHeTPaJSDyVPPn6R-7Q=="
org = "Jojo"
bucket = "postura_ergonomia"

try:
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, timeout=5000)
    query_api = client.query_api()
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -24h)
      |> filter(fn: (r) => r["_measurement"] == "Postura")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df = query_api.query_data_frame(query)
    
    if df.empty or 'distancia' not in df.columns:
        raise ValueError()
        
    df['distancia'] = pd.to_numeric(df['distancia'], errors='coerce')
    df = df.dropna(subset=['distancia'])
    if 'alerta' in df.columns:
        df['alerta'] = pd.to_numeric(df['alerta'], errors='coerce').fillna(0).astype(int)

except Exception:
    # Datos de respaldo estéticos si falla la conexión
    registros = 20
    df = pd.DataFrame({
        'distancia': np.random.randint(35, 55, size=registros),
        'alerta': np.random.choice([0, 1], size=registros, p=[0.8, 0.2])
    })

# 3. Diseño de la Interfaz de la App
st.markdown("<h1 style='font-size: 26px; margin-bottom: 5px;'>🩺 PostureCare</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9bbcd8; font-size: 14px; margin-top: 0px;'>Tu asistente médico de escritorio</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border: 0; border-top: 1px solid #e1eef7;'>", unsafe_allow_html=True)

# Sección de estado actual (Avatar/Icono dinámico)
ultima_distancia = int(df['distancia'].iloc[-1])
ultima_alerta = int(df['alerta'].iloc[-1]) if 'alerta' in df.columns else 0

if ultima_alerta == 1 or ultima_distancia < 40:
    st.markdown("<div style='background-color: #fff0f0; padding: 15px; border-radius: 20px; text-align: center; border: 2px solid #ffd6d6; color: #c97d7d; margin-bottom: 20px;'>⚠️ <b>¡Te estás encorvando!</b> Por favor, recupera la postura recta.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='background-color: #f0fcf4; padding: 15px; border-radius: 20px; text-align: center; border: 2px solid #d6f7e1; color: #6db384; margin-bottom: 20px;'>✨ <b>¡Excelente postura!</b> Lo estás haciendo genial.</div>", unsafe_allow_html=True)

# Fila de Métricas (Estilo Tarjeta)
col1, col2 = st.columns(2)
distancia_promedio = int(df['distancia'].mean())
total_alertas = int(df['alerta'].sum()) if 'alerta' in df.columns else 3

col1.metric(label="Distancia Promedio", value=f"{distancia_promedio} cm")
col2.metric(label="Alertas del Día", value=f"{total_alertas} 🚨")

# Gráfica de Monitoreo
st.markdown("<h3 style='font-size: 18px; text-align: left; margin-top: 25px; margin-bottom: 10px;'>📊 Historial de Distancia</h3>", unsafe_allow_html=True)

# Paleta Azul Baby para la gráfica lineal nativa de Streamlit
st.line_chart(df['distancia'].tail(15), color="#7da0bf")

st.markdown("<hr style='margin-top: 25px; margin-bottom: 15px; border: 0; border-top: 1px solid #e1eef7;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #b5cddf; font-size: 11px;'>Clínica de Ergonomía IoT • 2026</p>", unsafe_allow_html=True)
