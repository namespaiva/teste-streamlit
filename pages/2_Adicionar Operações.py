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

colMapa, colForm = st.columns(2)
with colMapa:
    tl = folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        attr='Map data © OpenStreetMap contributors',
        name='OpenStreetMap HOT',
        overlay=True,
        control=True
    )
    m = folium.Map(tiles=tl, location=(-23.953469450472493, -46.34634017944336), zoom_start=13)
    Draw(export=False,draw_options={'polyline': True,
                                    'polygon': False,
                                    'rectangle': False,
                                    'circle': False,
                                    'marker': True,
                                    'circlemarker': False
                                    }, position='bottomleft').add_to(m)
    Geocoder(position='topleft',add_marker=True).add_to(m)
    output = st_folium(m, height=500, width=700)

with colForm:
    with st.form('form_add', clear_on_submit=False):
        respform = []

        linha1 = st.columns([2,1,1])
        nomeOp = linha1[0].text_input('Nome da Operação')
        tipoOp = linha1[1].selectbox('Tipo de Operação',
                                        ['Obra', 'Evento', 'Escolta'],
                                        placeholder='Tipo')
        concOp = linha1[2].selectbox('Concessionária',
                                        ['CET', 'PMS', 'SABESP', 'VLT', 'CPFL', 'VIVO'],
                                        placeholder='Concessionária')

        linha2 = st.columns([1,1])
        respOp = linha2[0].text_input('Responsável pela operação')
        cttrespOp = linha2[1].number_input('Telefone do responsável', format='%1f')

        linha3 = st.columns([3,1,3])
        logOp = linha3[0].selectbox('Logradouro',['Lista de logradouros','da cidade',
                                                    'nao tenho ela',
                                                    'existe uma porrada'])
        numOp = linha3[1].number_input('Nº',format='%1f',)
        cruzOp = linha3[2].selectbox('Cruzamento',['Mesma','merda','que os logradouros'])

        linha4 = st.columns([1,1,1,1])
        dtIncioOp = linha4[0].date_input('Dt. de Início', datetime.date.today(),
                                            format='DD/MM/YYYY')
        hrIncioOp = linha4[1].time_input('Hr. de Início')

        dtFimPrevOp = linha4[2].date_input('Dt. previsão de fim', value=None,
                                            format='DD/MM/YYYY', min_value=datetime.date.today())
        hrFimPrevOp = linha4[3].time_input('Hr. previsão de Fim', value=None)

        linha5 = st.columns(1)
        descOp = linha5[0].text_area('Descrição')

        linha6 = st.columns(1)
        localOp = linha6[0].text_input(label='Local',
                                        value=str(output['last_active_drawing']), disabled=True)

        respform = [nomeOp, tipoOp, concOp, 
                    respOp, cttrespOp,
                    logOp, numOp, cruzOp,
                    dtIncioOp, hrIncioOp, dtFimPrevOp, hrFimPrevOp,
                    descOp, 
                    localOp]

        submitted = st.form_submit_button('Salvar')
        if submitted:
            if not nomeOp or not respOp or not localOp:
                st.warning("Preencha todos os campos obrigatórios!",icon='🚨')
            else:
                df = add_dados(df, respform)
                st.success("Dados salvos com sucesso!")
                st.cache_data.clear()
                df = load_data()

st.dataframe(df, hide_index=True)