import streamlit as st
import pandas as pd
import numpy as np
import influxdb_client
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Posture Tracker App",
    page_icon="🩺",
    layout="centered"
)

if 'started' not in st.session_state:
    st.session_state['started'] = False

st.markdown("""
<style>
    .stApp {
        background-color: #f2f7fb;
    }

    .block-container {
        max-width:430px !important;
        padding:2rem !important;
        background-color:#ffffff;
        border-radius:40px;
        box-shadow:0 10px 30px rgba(153,192,222,0.3);
        margin:auto;
        border:8px solid #d4e6f4;
        min-height:80vh;
    }

    h1,h2,h3{
        color:#5c8cb3;
        text-align:center;
    }

    .stButton>button{
        width:100%;
        border-radius:20px;
        background-color:#d4e6f4;
        color:#5c8cb3;
        border:2px solid #b5d1e8;
        padding:10px;
        font-weight:bold;
    }

    .stButton>button:hover{
        background-color:#5c8cb3;
        color:white;
    }

    div[data-testid="stMetric"]{
        background-color:#f0f6fc;
        border-radius:20px;
        padding:15px !important;
        border:2px solid #e1eef7;
    }

</style>
""", unsafe_allow_html=True)

if not st.session_state['started']:

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1>🩺</h1>", unsafe_allow_html=True)
    st.markdown("<h1>Posture Tracker</h1>", unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align:center;color:#9bbcd8;'>Cuida tu espalda de forma inteligente.</p>",
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("Comenzar"):
        st.session_state['started']=True
        st.rerun()

else:

    st_autorefresh(
        interval=2000,
        key="refresh"
    )

    url="https://us-east-1-1.aws.cloud2.influxdata.com/"
    token="hFiRK2sGAD4uMuyGl1cXxApTtrPuoIlbrc8ERykxqQJB56gyzCEpcWiGL4tXjQGkit6lHeTPaJSDyVPPn6R-7Q=="
    org="Jojo"
    bucket="postura_ergonomia"

    try:

        client=influxdb_client.InfluxDBClient(
            url=url,
            token=token,
            org=org
        )

        query_api=client.query_api()

        query=f'''
        from(bucket: "{bucket}")
          |> range(start: -24h)
        '''

        df=query_api.query_data_frame(query)

        if isinstance(df,list):
            df=pd.concat(
                df,
                ignore_index=True
            )

        if df.empty:
            raise ValueError()

        # toma el valor real enviado desde influx
        df['distancia']=pd.to_numeric(
            df['_value'],
            errors='coerce'
        )

        df=df.dropna(
            subset=['distancia']
        )

        es_datos_reales=True

    except Exception as e:

        st.write(e)

        es_datos_reales=False

        df=pd.DataFrame({

            'distancia':
            [42]*20,

            'alerta':
            [0]*20
        })

    st.markdown(
        "<h2 style='font-size:22px;'>🩺 PostureCare</h2>",
        unsafe_allow_html=True
    )

    ultima_distancia=int(
        df['distancia'].iloc[-1]
    )

    if ultima_distancia<40:

        st.markdown(
        """
        <div style='background-color:#fff0f0;
        padding:12px;
        border-radius:15px;
        text-align:center;
        border:2px solid #ffd6d6;
        color:#c97d7d;'>

        ⚠️ <b>¡Cuidado!</b>
        Recupera tu postura

        </div>
        """,
        unsafe_allow_html=True
        )

    else:

        st.markdown(
        """
        <div style='background-color:#f0fcf4;
        padding:12px;
        border-radius:15px;
        text-align:center;
        border:2px solid #d6f7e1;
        color:#6db384;'>

        ✨ <b>Todo bien.</b>
        Estás derecho.

        </div>
        """,
        unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    c1,c2=st.columns(2)

    c1.metric(
        "Distancia Actual",
        f"{ultima_distancia} cm"
    )

    if es_datos_reales:

        c2.metric(
            "Conexión",
            "En Vivo 📡"
        )

    else:

        c2.metric(
            "Conexión",
            "Simulado 🔄"
        )

    st.markdown(
    "<h3 style='font-size:16px;text-align:left;'>📊 Historial Reciente</h3>",
    unsafe_allow_html=True
    )

    st.line_chart(
        df['distancia'].tail(15)
    )

    st.markdown(f"""
    <div style='background-color:#ffffff;
    padding:15px;
    border-radius:20px;
    border:2px solid #e1eef7;
    margin-top:15px;'>

    <p style='color:#5c8cb3;
    font-size:12px;
    margin:0;
    text-align:justify;'>

    <b>📊 Diagnóstico Clínico:</b>
    De acuerdo con el análisis de tendencias,
    los usuarios reducen la distancia
    por debajo del umbral de 40 cm.

    </p>

    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "Cerrar Sesión"
    ):

        st.session_state['started']=False
        st.rerun()

    st.markdown(
    "<p style='text-align:center;color:#b5cddf;font-size:10px;margin-top:20px;'>Clínica de Ergonomía IoT • 2026</p>",
    unsafe_allow_html=True
    )
