import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import datetime
import branca
from folium.plugins import Geocoder
import json


st.set_page_config(page_title="Mapa", page_icon="🌎", layout='wide',initial_sidebar_state="collapsed")
st.title("Mapa de Operações")

@st.cache_data
def load_data():
    dados = pd.read_csv('data/operacoes.csv')
    return dados
def add_dados(df, dados):
    dados_mapeados = {
        'nome': dados[0],
        'tipo': dados[1],
        'concessionaria': dados[2],
        'responsavel': dados[3],
        'ctt_responsavel': dados[4],
        'logradouro': dados[5],
        'numero': dados[6],  
        'cruzamento': dados[7],
        'dt_inicio': dados[8],  
        'hr_inicio': dados[9], 
        'dt_fim_prev': dados[10],
        'hr_fim_prev': dados[11],
        'dt_fim': None,
        'hr_fim': None,
        'descricao': dados[12],
        'local' : dados[13]
    }

    tempdf = pd.DataFrame([dados_mapeados])    
    tempdf.to_csv('data/operacoes.csv', mode='a', header=False, index=False)
    df = pd.concat([df, tempdf], ignore_index=True)
    # df['local'] = df['local'].apply(lambda x: x.replace('"', ''))
    # df['local'] = df['local'].apply(lambda x: x.replace("'", '"'))   
    # df['local'] = df['local'].apply(json.loads)
    return df
def convert_to_feature_collection(input_json):
    data = json.loads(input_json)
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            data
        ]
    }
    return json.dumps(feature_collection, indent=2)

df = load_data()

colMap, colDF = st.columns(2)

tl = folium.TileLayer(
    tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    attr='Map data © OpenStreetMap contributors',
    name='OpenStreetMap HOT',
    overlay=True,
    control=True
)
m2 = folium.Map(tiles=tl, location=(-23.953469450472493, -46.34634017944336), zoom_start=13)

for index, row in df.iterrows():
    nome = row['nome']
    dtInicio = row['dt_inicio']
    hrInicio = row['hr_inicio']
    responsavel = row['responsavel']
    endereco = f"{row['logradouro']} {row['numero']} {row['cruzamento']}"
    texto = row['descricao']
    
    css = """
        <style>
        .inline-block {
                text-align: center;
            }
            </style>
            """
    html = f"""
        {css}
        <p style="color: darkgreen; font-size: 16px; font-family: Arial, sans-serif;">
        {nome}</p>
        <p style="color: darkgreen; font-size: 16px; font-family: Arial, sans-serif;">
        Data e hora de início: {dtInicio} {hrInicio}</p>
        <p style="color: darkgreen; font-size: 16px; font-family: Arial, sans-serif;">
        Endereço: {endereco}</p>
        <p style="color: darkgreen; font-size: 16px; font-family: Arial, sans-serif;">
        Responsável: {responsavel}</p>
        <p class="inline-block" style="text-align: center; color: darkgreen; font-size: 16px; font-family: Arial, sans-serif;">
        Descrição da operaçao: {texto}
        </p>
        """

    iframe = branca.element.IFrame(html=html, width=200, height=300)
    popup = folium.Popup(iframe, max_width=300)

    geojson_string = str(row['local'])
    geojson_string = geojson_string.replace('"','')
    geojson_string = geojson_string.replace("'",'"')
    feature_data = convert_to_feature_collection(geojson_string)
    geojson_data = json.loads(feature_data)

    features_list = geojson_data['features']

    for feature in features_list:
        geom_type = feature['geometry']['type']
        coordinates = feature['geometry']['coordinates']

        if geom_type == "Point":
            folium.Marker(
                location=[coordinates[1], coordinates[0]], 
                icon=folium.Icon(color="green", prefix="fa", icon="person-digging"),
                popup=popup
            ).add_to(m2)
        elif geom_type == "LineString":
            folium.PolyLine(
                locations=[[coord[1], coord[0]] for coord in coordinates],
                color="blue",
                weight=2.5,
                opacity=0.7,
                popup=popup
            ).add_to(m2)

with st.container():           
    output2 = st_folium(m2, height=500, width=1000)

st.dataframe(df, hide_index=True)