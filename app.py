import streamlit as st
import pandas as pd
import numpy as np
import influxdb_client
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Posture Tracker App", page_icon="🩺", layout="centered")

if 'started' not in st.session_state:
    st.session_state['started'] = False

st.markdown("""
<style>
    .stApp { background-color: #f2f7fb; }
    
    .block-container {
        max-width: 430px !important;
        padding: 2rem !important;
        background-color: #ffffff;
        border-radius: 40px;
        box-shadow: 0 10px 30px rgba(153, 192, 222, 0.3);
        margin: auto;
        border: 8px solid #d4e6f4;
        min-height: 80vh;
    }
    
    h1, h2, h3 { color: #5c8cb3; text-align: center; }
    
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #d4e6f4;
        color: #5c8cb3;
        border: 2px solid #b5d1e8;
        padding: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #5c8cb3;
        color: white;
    }
    
    div[data-testid="stMetric"] {
        background-color: #f0f6fc;
        border-radius: 20px;
        padding: 15px !important;
        border: 2px solid #e1eef7;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state['started']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 40px;'>🩺</h1>", unsafe_allow_html=True)
    st.markdown("<h1>Posture Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9bbcd8;'>Cuida tu espalda de forma inteligente y aesthetic.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.button("Comenzar"):
        st.session_state['started'] = True
        st.rerun()

else:
    # Fuerza un refresco de toda la app cada 2000 milisegundos (2 segundos)
    st_autorefresh(interval=2000, key="datarefresh")
    
    url = "https://us-east-1-1.aws.cloud2.influxdata.com/"
    token = "hFiRK2sGAD4uMuyGl1cXxApTtrPuoIlbrc8ERykxqQJB56gyzCEpcWiGL4tXjQGkit6lHeTPaJSDyVPPn6R-7Q=="
    org = "Jojo"
    bucket = "postura_ergonomia"

    try:
        client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, timeout=3000)
        query_api = client.query_api()
        
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -1h)
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
            
        es_datos_reales = True
    except Exception:
        es_datos_reales = False
        registros = 20
        # Simula una fluctuación leve en tiempo real si el servidor de Influx está vacío
        base_dist = np.random.randint(42, 48)
        df = pd.DataFrame({
            'distancia': [base_dist + np.random.randint(-2, 3) for _ in range(registros)],
            'alerta': np.random.choice([0, 1], size=registros, p=[0.9, 0.1])
        })

    st.markdown("<h2 style='font-size: 22px;'>🩺 PostureCare</h2>", unsafe_allow_html=True)
    
    ultima_distancia = int(df['distancia'].iloc[-1])
    
    if ultima_distancia < 40:
        st.markdown("<div style='background-color: #fff0f0; padding: 12px; border-radius: 15px; text-align: center; border: 2px solid #ffd6d6; color: #c97d7d; font-size: 13px;'>⚠️ <b>¡Cuidado!</b> Recupera tu postura.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color: #f0fcf4; padding: 12px; border-radius: 15px; text-align: center; border: 2px solid #d6f7e1; color: #6db384; font-size: 13px;'>✨ <b>Todo bien.</b> Estás derecho.</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    c1.metric("Distancia Actual", f"{ultima_distancia} cm")
    
    if es_datos_reales:
        c2.metric("Conexión", "En Vivo 📡")
    else:
        c2.metric("Conexión", "Simulado 🔄")

    st.markdown("<h3 style='font-size: 16px; text-align: left; margin-top: 20px;'>📊 Historial Reciente</h3>", unsafe_allow_html=True)
    st.line_chart(df['distancia'].tail(15), color="#7da0bf")

    st.markdown(f"""
    <div style='background-color: #ffffff; padding: 15px; border-radius: 20px; border: 2px solid #e1eef7; margin-top: 15px;'>
        <p style='color: #5c8cb3; font-size: 12px; margin: 0; text-align: justify;'>
            <b>📊 Diagnóstico Clínico:</b> De acuerdo con el análisis de tendencias, los usuarios reducen la distancia de visión por debajo del umbral de 40 cm tras periodos prolongados, lo que justifica el uso de alertas para mitigar la fatiga visual.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Cerrar Sesión"):
        st.session_state['started'] = False
        st.rerun()

    st.markdown("<p style='text-align: center; color: #b5cddf; font-size: 10px; margin-top: 20px;'>Clínica de Ergonomía IoT • 2026</p>", unsafe_allow_html=True)
