# Bibliotecas
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image
import warnings
import folium
import re
from math import radians, sin, cos, sqrt, atan2
from streamlit_folium import folium_static

#erro nos filtros de data e densidade de trafego

st.set_page_config(
    page_title="Visão Restaurante",
    page_icon="🍽️",
    layout="wide"
)

#____________________________LIMPEZA_DE_DADOS_____________________________

def clean_code(df1):
    """ Limpeza dos dados 
    
    Tipos de limpeza:
    1. Remoção de NaN
    2. Conversao de tipo
    3. Removendo (min) da coluna Time_taken(min)
    4. Removendo espaço dentro dos dados 
    
    """
    # 1. Remove linhas com valores ausentes nas colunas 
    df1 = df1.loc[(df1['Delivery_person_Age'] != 'NaN '), :]
    df1 = df1.loc[(df1['Road_traffic_density'] != 'NaN '), :]
    df1 = df1.loc[(df1['City'] != 'NaN '), :]
    df1 = df1.loc[(df1['Festival'] != 'NaN '), :]
    
    
    # 2. Conversão de tipo
    df1['Delivery_person_Age'] = pd.to_numeric(df1['Delivery_person_Age'], errors='coerce').astype('Int64')
    df1['Delivery_person_Ratings'] = pd.to_numeric(df1['Delivery_person_Ratings'], errors='coerce').astype('Float64')
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y')
    
    
    # 3. limpando dados da coluna time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min)', '').str.strip().astype('Int64') 
    # convertendo para formaro de data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y')
    
    
    # 4. removendo espaço dentro dos textos
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    return df1

#_____________________________________________________________________

# Lendo o documento
df = pd.read_csv('train.crdownload')
df1 = df.copy()
df1 = clean_code(df)
#_________________________________________________________________________
st.header('Marketplace - Visão Restaurante') 

# inserindo imagem
# image_path = r'C:\Users\karen\OneDrive\Área de Trabalho\Cientista de Dados\Exercícios\Cury.png'
image = Image.open('Cury.png')
st.sidebar.image(image, width=200)

# inserindo a barra do lado
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Indian Fast Food')
st.sidebar.markdown("""___""")

# colocando filtro de data
min_date = df1['Order_Date'].min().to_pydatetime()
max_date = df1['Order_Date'].max().to_pydatetime()

selected_date = st.sidebar.slider(
    "Selecione uma data",
    min_value=min_date,
    max_value=max_date,
    value=min_date, # data inicial padrão
    format='DD/MM/YYYY')

st.sidebar.markdown(f"### Data selecionada: {selected_date.strftime('%d/%m/%Y')}")
#st.header(f" Pedidos do dia: {selected_date.strftime('%d/%m/%Y')}")
st.sidebar.markdown("""___""")

# filtro de tipo de trafego
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""")

# filtro de cidade
city_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Metropolitian', 'Urban', 'Semi-Urban'],
    default=['Metropolitian', 'Urban', 'Semi-Urban'])
st.sidebar.markdown("""___""")

 #----------------------------------------------
# filtro de data
linhas_selecionadas= df1['Order_Date'] < selected_date
df1 = df1.loc[linhas_selecionadas, :]

#filtro de densidade de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1_filtrado = df1.loc[linhas_selecionadas, :]

# filtro de cidade
linhas_selecionadas = df1['City'].isin(city_options)
df1_filtrado = df1.loc[linhas_selecionadas, :]

#====================================================================
#Layout no streamlit
#====================================================================
tab1, tab2, tab3 = st.tabs(['Entregadores', 'Tempo de Entrega', "-"])

with tab1:
    
    with st.container():
        st.title('Visão Restaurante')
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader('Entregadores Ativos')
        unicos = df1_filtrado['Delivery_person_ID'].unique()
        contar_unicos = len(unicos)
        col1.metric(label='', value=contar_unicos)

    with col2:
        st.subheader('Entregas Normais')
        entrega_normal = df1_filtrado[df1_filtrado['Festival'] == 'No']
        contar_entrega = len(entrega_normal)
        col2.metric(label='', value=contar_entrega)
    
    with col3:
        st.subheader('Entregas Festival')
        entrega_festival = df1_filtrado[df1_filtrado['Festival'] == 'Yes']
        contar_festival = len(entrega_festival)
        col3.metric(label='', value=contar_festival)
    
        st.sidebar.markdown("""___""")
 
    with st.container():
        st.markdown("""___""")
        st.subheader('Distância Média entre os Restaurantes e Locais de Entrega')
        def calcular_distancia(lat1, lon1, lat2, lon2):
            R = 6371.0
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        df1_filtrado['Distancia_km'] = df1_filtrado.apply(
            lambda row: calcular_distancia(
                row['Restaurant_latitude'],
                row['Restaurant_longitude'],
                row['Delivery_location_latitude'],
                row['Delivery_location_longitude']
            ),
            axis=1
        )
        distancias_medias = {
            #'Media Geral': df_limpo['Distancia_km'].mean(),
            'Dinstância Media por Cidade (km)': df1_filtrado.groupby('City')['Distancia_km'].mean().round(2)
        }
        st.dataframe(distancias_medias)

    

with tab2:
    with st.container():
        st.title('Tempo Médio de Entregas')
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption('Entregas em dias normais')
        tempo_medio = df1_filtrado[df1_filtrado['Festival'] == 'No']['Time_taken(min)'].mean()
        st.subheader(f"{tempo_medio:.0f} minutos")
    
    with col2:
        st.caption('Entregas em dias de festival')
        tempo_medio_festival = df1_filtrado[df1_filtrado['Festival'] == 'Yes']['Time_taken(min)'].mean()
        st.subheader(f"{tempo_medio_festival:.0f} minutos")
                
    with st.container():
        st.markdown("""___""")
        st.subheader('Por Cidade')
        tempo_cidade = df1_filtrado.groupby('City')['Time_taken(min)'].mean().round(0).reset_index()
        tempo_cidade.columns = ['Cidade', 'Tempo Medio (min)']
        st.dataframe(tempo_cidade)

    with st.container():
        st.markdown("""___""")
        st.subheader('Por Tipo de Pedido')
        tempo_pedido = df1_filtrado.groupby('Type_of_order')['Time_taken(min)'].mean().round(0).reset_index()
        tempo_pedido.columns = ['Tipo de Pedido', 'Tempo Medio (min)']
        st.dataframe(tempo_pedido)

    with st.container():
        st.markdown("""___""")
        st.subheader('Por Densidade de Trafego')
        tempo_trafego = df1_filtrado.groupby('Road_traffic_density')['Time_taken(min)'].mean().round(0).reset_index()
        tempo_trafego.columns = ['Densidade do Trânsito', 'Tempo Médio (min)']
        st.dataframe(tempo_trafego)

        




