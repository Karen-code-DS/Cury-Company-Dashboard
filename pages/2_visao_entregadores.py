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
from streamlit_folium import folium_static


st.set_page_config(
    page_title="Visão Entregadores",
    page_icon="🛵",
    layout="wide"
)




#____________________________________FUNÇÕES____________________________________________

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
# Dados limpos
df1 = clean_code(df)
#-------------------------------------------------------------------------------

st.header('Marketplace - Visão Entregador') 

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

#--------------------------------------------------------------------------------
# filtro de data
linhas_selecionadas= df1['Order_Date'] < selected_date
df1 = df1.loc[linhas_selecionadas, :]

#filtro de densidade de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1_filtrado = df1.loc[linhas_selecionadas, :]

#====================================================================
#Layout no streamlit
#====================================================================
tab1, tab2, tab3 = st.tabs(['Visão Geral', '_', '_'])

with tab1:
    with st.container(): 
        st.title('Métrica Geral')
    
    
    col1, col2, col3, col4 = st.columns(4, gap='large')
    
    with col1:
        st.subheader('Maior Idade:')
        maior = df1['Delivery_person_Age'].max()

        if pd.isna(maior):
            maior = "N/A"     
        col1.metric(label="", value=maior)
    
    with col2:
        st.subheader('Menor Idade:')
        menor = df1['Delivery_person_Age'].min()
        if pd.isna(menor):
            menor = "N/A"  
        col2.metric(label="", value=menor) 
    
    with col3:
        st.subheader('Melhor Veículos:')
        melhor = df1['Vehicle_condition'].max()
        col3.metric(label="", value=melhor)
    
    with col4:
        st.subheader('Pior Veículos:')
        pior = df1['Vehicle_condition'].min()
        col4.metric(label="", value=pior)

#___________________________________________________________________________________
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Avaliação Média por Entregador')
            entregador = df1_filtrado.groupby('Delivery_person_ID')['Delivery_person_Ratings'].mean().round(1).reset_index()
            entregador = entregador.sort_values('Delivery_person_Ratings', ascending=False).reset_index(drop=True)
            entregador.columns = ['Entregador', 'Avaliação Média']
            st.dataframe(entregador)
                
        with col2:
            st.subheader('Avaliação Média por Trânsito')
            avaliacao_trafego = df1_filtrado.groupby('Road_traffic_density')['Delivery_person_Ratings'].mean().round(1).reset_index()
            avaliacao_trafego.columns = ['Densidade de Tráfego', 'Avaliação Média']
            st.dataframe(avaliacao_trafego)         
            
            st.subheader('Avaliação Média por Clima')
            #condicao climatoca
            df_limpo = df1_filtrado[(df1_filtrado['Weatherconditions'] != 'conditions NaN')]
            avaliacao_clima = df_limpo.groupby('Weatherconditions')['Delivery_person_Ratings'].mean().round(1).reset_index()
            avaliacao_clima.columns = ['Condição Climática', 'Avaliação Média']
            st.dataframe(avaliacao_clima)

#__________________________________________________________________________________
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Top Entregadores Mais Rápidos')
            rapidos = df1_filtrado.groupby('Delivery_person_ID')['Time_taken(min)'].min().reset_index()
            rapidos = rapidos.sort_values('Time_taken(min)', ascending=True).reset_index(drop=True)
            rapidos.columns = ['Entregador', 'Tempo (min)']
            st.dataframe(rapidos.head(10))

        
        with col2:
            st.subheader('Top Entregadores Mais Lentos')
            lentos = df1_filtrado.groupby('Delivery_person_ID')['Time_taken(min)'].max().reset_index()
            lentos = lentos.sort_values('Time_taken(min)', ascending=False).reset_index(drop=True)
            lentos.columns = ['Entregador', 'Tempo (min)']
            st.dataframe(lentos.head(10))

#__________________________________________________________________________________




        
        



