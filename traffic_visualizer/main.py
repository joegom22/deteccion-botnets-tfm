import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IoT Botnet Analysis Visualization", layout="wide")
st.title("Visualización de análisis de tráfico red IoT")

csv_path = "/app/shared/predictions.csv"

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)

    total = len(df)
    botnets = (df['prediction'] == 1).sum()
    st.metric("Total flujos", total)
    st.metric("Botnets detectadas", botnets)
    st.metric("Porcentaje", f"{(botnets / total) * 100:.2f}%")

    counts = df['prediction'].value_counts().reset_index()
    counts.columns = ['Clase', 'Frecuencia']

    fig = px.pie(counts, names='Clase', values='Frecuencia', title='Distribución del tráfico')

    st.plotly_chart(fig)

    st.subheader("Tabla de flujos clasificados")
    st.dataframe(df)

    st.subheader("Distribución de probabilidades")
    st.bar_chart(df['probability'])

else:
    st.error(f"No se encontró el archivo: {csv_path}")