import os
import streamlit as st
import pandas as pd
import plotly.express as px
from prometheus_client import start_http_server, Gauge

st.set_page_config(page_title="IoT Botnet Analysis Visualization", layout="wide")
st.title("Visualización de análisis de tráfico red IoT")

csv_path = "/app/shared/predictions.csv"

if "prom_started" not in st.session_state:
    start_http_server(9100)
    st.session_state.prom_started = True

if "dashboard_gauge" not in st.session_state:
    st.session_state.dashboard_gauge = Gauge(
        "dashboard_operational",
        "1 si el dashboard está operativo, 0 si no"
    )

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)

    total = len(df)
    botnets = (df['Prediction'] == 1).sum()
    st.metric("Total flujos", total)
    st.metric("Botnets detectadas", botnets)
    st.metric("Porcentaje", f"{(botnets / total) * 100:.2f}%")

    counts = df['Prediction'].value_counts().reset_index()
    counts.columns = ['Clase', 'Frecuencia']

    fig = px.pie(counts, names='Clase', values='Frecuencia', title='Distribución del tráfico')

    st.plotly_chart(fig)

    st.subheader("Tabla de flujos clasificados")
    st.dataframe(df)

    st.subheader("Distribución de probabilidades")
    st.bar_chart(df['Probability'])

    st.session_state.dashboard_gauge.set(1)
else:
    st.error(f"No se encontró el archivo: {csv_path}")