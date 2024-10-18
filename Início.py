import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="CPMU", page_icon="📈", layout='wide')
st.title("Testes do CPMU")

st.markdown("# Sobre")
st.markdown('''
            ### Aba 1: Dados Sobre Acidentes

            Dados de acidentes em Santos de 2015 a 2024. A partir de 2018 a quantidade de dados 
            anuais cai drasticamente, por isso o ano inicial padrão é 2018. 

            Muitos acidentes aconteceram no mesmo endereço/cruzamento, por isso os pontos ficam 
            sobrepostos no mapa. Recomendo usar (clicar) a legenda do próprio gráfico para ocultar 
            alguns pontos e ver quais estão acima de quais, ou usar o seletor do mapa.

            A ordem das ruas no cruzamento importa. Rua A x B vai mostrar resultados diferentes de 
            rua B x A.

            A legenda do mapa oculta os pontos apenas visualmente, ou seja, eles ainda aparecerão
            na tabela de dados. Para evitar isso, selecione a gravidade desejada no filtro de gravidade. 
            
            Os filtros já estão razoavelmente dinâmicos, mas alguns acabam limpando as seleções 
            anteriores.

            Os dias da semana estão representados em números, de 1, domingo até 7, sábado.

            ### Abas 2 e 3: Input de dados de operações em um mapa:

            A segunda aba (Adicionar Operações) insere dados em um "banco de dados", que podem ser vistos no mapa 
            como itens clicáveis na terceira aba (Mapa).

            Na aba de adicionar operações, é preciso usar uma das ferramentas de desenho 
            (canto inferior esquerdo)para preencher o local da operação. Para um ponto (marcador)
            basta um clique e para uma linha é necessário clicar em "Finish" ou no último ponto da
            linha para finalizar.

            É sempre o último desenho feito que é enviado para o "banco"

            Se a inserção não estiver funcionando, é porque o "banco" não está hospedado em lugar nenhum.
            Nesse caso você vai ter que confiar em mim que a inserção tá funcionando.

            A consulta ainda vai funcionar com ou sem hospedagem. 
            ''')
