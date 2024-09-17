import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json


st.set_page_config(page_title="Acidentes", page_icon="🗿")
st.title("Teste Acidentes")

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

colGrav, colTipo, colTempo = st.columns(3)

with colGrav:
    selected_gravidade = st.multiselect(
        'Escolha a(s) gravidade(s)',
        list(df['gravidade'].unique())
    )

with colTipo:
    selected_tipo = st.multiselect(
        'Escolha o(s) tipo(s) de acidente',
        list(df['tipo_acidente'].unique())
    )
with colTempo:
    selected_tempo = st.multiselect(
        'Escolha o(s) tempo(s)',
        list(df['tempo'].unique())
    )

if selected_gravidade or selected_tipo or selected_tempo:
    df = df[(df['gravidade'].isin(selected_gravidade)) 
            | (df['tipo_acidente'].isin(selected_tipo)) 
            | (df['tempo'].isin(selected_tempo))]
else:
    df = df

gravidade_colors = {
    'C/ VÍTIMAS LEVES': 'green',
    'C/ VÍTIMAS GRAVES': 'orange',
    'C/ VÍTIMAS FATAIS': 'red',
    'S/ LESÃO': 'blue'
}

fig = go.Figure()

gravidades = df['gravidade'].unique()
for gravidade in gravidades:
    df_gravidades = df[df['gravidade'] == gravidade]
    fig.add_trace(go.Scattermapbox(
        lat=df_gravidades.lat,
        lon=df_gravidades.lon,
        mode='markers',
        marker=dict(
            size=8,
            opacity=0.7,
            color=gravidade_colors.get(gravidade, 'gray')
        ),
        name=f'{gravidade}'
    ))

fig.update_layout(
    title='Acidentes por gravidade',
    mapbox=dict(
        style="carto-darkmatter",
        center=dict(lat=df.lat.mean(), lon=df.lon.mean()),
        zoom=12
    ),
    showlegend=True
)

selected_points = st.plotly_chart(fig, use_container_width=True,
                on_select='rerun',
                selection_mode=['box','lasso'])

# try:
#     selected_points = json.loads(selected_points)
# except json.JSONDecodeError:
#     selected_points = []

if selected_points:
    # Extract coordinates from selected points
    selected_coords = [(p['lon'], p['lat']) for p in selected_points.get('selection', {}).get('points', [])]
    
    if selected_coords:
        # Ensure DataFrame columns match the coordinates
        df_filtered = df[df[['lon', 'lat']].apply(tuple, axis=1).isin(selected_coords)]
    else:
        df_filtered = pd.DataFrame()  # No coordinates selected
else:
    df_filtered = pd.DataFrame()  # No points selected

st.write("Dados:")
st.dataframe(df_filtered, hide_index=True)