import altair as alt
import pandas as pd
import streamlit as st
import numpy as np

# Show the page title and description.
st.set_page_config(page_title="Acidentes", page_icon="🗿")
st.title("Teste Acidentes")
st.write(
    """
    """
)

@st.cache_data
def load_data():
    dados = pd.read_csv("data/acidentes.csv")

    dados.sort_values(by=['data', 'hora'], inplace=True)
    dados.reset_index(drop=True, inplace=True)
    dados['data'] = pd.to_datetime(dados['data'])
    dados['data'] = pd.to_datetime(dados['data'].astype(str) + ' ' + dados['hora'])
    dados.drop(columns='hora', inplace=True)
    dados['dia_semana'] = (dados['data'].dt.dayofweek)
    dias = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 1}
    dados['dia_semana'] = dados['dia_semana'].map(dias)
    dados.rename(columns={'lng':'lon','data':'data_hora'}, inplace=True)
    return dados

df = load_data()

ano = st.slider(
    "Escolha o Período",
    2015, 2024, (2017,2024)
)

df = df[df['data_hora'].dt.year.isin(ano)]

option = st.multiselect(
    'Escolha um filtro',
     list(df['gravidade'].unique())
     )

if option:
    filter_df = df[df['gravidade'].isin(option)]
else:
    filter_df = df

st.map(filter_df)

st.dataframe(filter_df, hide_index=True)