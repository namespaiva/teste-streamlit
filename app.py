import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Acidentes", page_icon="🚗", layout='wide')
st.title("Dados de Acidentes")

with st.expander("Sobre"):
    st.markdown('''
             Dados de acidentes em Santos de 2015 a 2024. A partir de 2017 a quantidade de dados 
             anuais cai drasticamente, por isso o ano inicial padrão é 2017. 

             Muitos acidentes aconteceram no mesmo endereço/cruzamento, por isso os pontos ficam 
             sobrepostos no mapa. Recomendo usar (clicar) a legenda do próprio gráfico para ocultar 
             alguns pontos e ver quais estão acima de quais.
             
             Os filtros já estão razoavelmente dinâmicos, mas alguns acabam limpando as seleções 
             anteriores.

             Os dias da semana estão representados em números, de 1, domingo até 7, sábado.
             
             Planos posteriores: adicionar alguns gráficos interativos e um mapa de calor.
             ''')

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

@st.cache_data
def apply_filters(df, filters):
    for filter_value, column in filters:
        if filter_value: 
            if column == 'data_hora_year':
                # Especificamente para a coluna de data (pois é tipo datetime)
                df = df[df['data_hora'].dt.year.isin(filter_value)]
            elif isinstance(filter_value, list):  # Para mais de um valor (multiselect)
                df = df[df[column].isin(filter_value)]
            else:  # Para só um valor (multiselect)
                df = df[df[column] == filter_value]
    
    return df

df = load_data()
filters = []

anos = st.slider(
    "Escolha um Período",
    df['data_hora'].dt.year.min(),
    df['data_hora'].dt.year.max(),
    (2017,2024) 
    )
filters.append((anos, 'data_hora_year'))
df = apply_filters(df, filters)

# Filtros
with st.container():
    st.header('Filtros')
    
    #filters.append((ano, 'data_hora'.dt.year))

    colGrav, colTipo, colTempo = st.columns(3)

    with colGrav:
        selected_gravidade = st.multiselect(
            label='Gravidade(s)',
            options=df['gravidade'].unique(),
            placeholder='Escolha a(s) gravidade(s)'
        )
        filters.append((selected_gravidade, 'gravidade'))
        df = apply_filters(df, filters)

        selected_logras = st.multiselect(
            label='Logradouro',
            options=df['logradouro'].unique(),
            placeholder='Escolha o(s) Logradouro(s)'
            )
        filters.append((selected_logras, 'logradouro'))
        df = apply_filters(df, filters)

    with colTipo:
        selected_tipo = st.multiselect(
            label='Tipo(s) de acidente',
            options=df['tipo_acidente'].unique(),
            placeholder='Escolha o(s) tipo(s) de acidente'
        )
        filters.append((selected_tipo, 'tipo_acidente'))
        df = apply_filters(df, filters)

        selected_nums = st.multiselect(
            label='Número',
            options=df['numero'].unique(),
            placeholder='Escolha um número'
        )
        filters.append((selected_nums, 'numero'))
        df = apply_filters(df, filters)

    with colTempo:
        selected_tempo = st.multiselect(
            label='Tempo(s)',
            options=df['tempo'].unique(),
            placeholder='Escolha o(s) tempo(s)'
        )
        filters.append((selected_tempo, 'tempo'))
        df = apply_filters(df, filters)

        selected_cruz = st.multiselect(
            label='Cruzamento',
            options=df['cruzamento'].unique(),
            placeholder = 'Escolha o(s) cruzamento(s)'
            )
        filters.append((selected_cruz, 'cruzamento'))
        df = apply_filters(df, filters)

    df = apply_filters(df, filters)

gravidade_colors = {
    'C/ VÍTIMAS LEVES': 'green',
    'C/ VÍTIMAS GRAVES': 'orange',
    'C/ VÍTIMAS FATAIS': 'red',
    'S/ LESÃO': 'blue'
}

# Criar o Plotly
config = {'displayModeBar': True}
fig = go.Figure()

gravidades = df['gravidade'].unique()
for gravidade in gravidades:
    df_gravidades = df[df['gravidade'] == gravidade]
    
    hover_text = df_gravidades.apply(
        lambda row: f"Logradouro: {row['logradouro']}<br>Número: {row['numero']}<br>Cruzamento: {row['cruzamento']}",
        axis=1
    )

    fig.add_trace(go.Scattermapbox(
        lat=df_gravidades.lat,
        lon=df_gravidades.lon,
        mode='markers',
        marker=dict(
            size=8,
            opacity=0.7,
            color=gravidade_colors.get(gravidade, 'gray')
        ),
        name=f'{gravidade}',
        hovertext=hover_text, 
        hoverinfo='text' 
    ))

fig.update_layout(
    mapbox=dict(
        style="carto-darkmatter",
        center=dict(lat=-23.959, lon=-46.342),
        zoom=12
    ),
    height=450,
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(
        x=0.0,
        y=0.925,
        xanchor='left', 
        yanchor='middle',
        font=dict(size=14),
        orientation='v' 
    ),
    showlegend=True
)

tabMap, tabGraphs = st.tabs(['Mapa', 'Gráficos'])

# Visualização
with tabMap:
    colMap, colDF = st.columns(2)
    with colMap:
        st.write('Mapa de Acidentes por Gravidade')
        selected_points = st.plotly_chart(fig, use_container_width=True,
                        on_select='rerun',
                        selection_mode=['box','lasso'])

    if selected_points:
        selected_coords = [(p['lon'], p['lat']) for p in selected_points.get('selection', {}).get('points', [])]
        
        if selected_coords:
            df_filtered = df[df[['lon', 'lat']].apply(tuple, axis=1).isin(selected_coords)]
        else:
            df_filtered = pd.DataFrame() 
    else:
        df_filtered = df

    with colDF:
        st.write("Dados")
        st.dataframe(df_filtered, hide_index=True,
                        column_order=['data_hora','dia_semana','logradouro','numero',
                                    'cruzamento','tipo_acidente','gravidade','tempo'])

        #st.write(df.columns)

with tabGraphs:
    st.header("Nada por aqui ainda. 🚧") 