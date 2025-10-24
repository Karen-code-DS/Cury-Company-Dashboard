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
import sys
from streamlit_folium import folium_static

#erro nos filtros de data e densidade de trafego

st.set_page_config(
    page_title="Visão Empresa",
    page_icon="🏣",
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

#--------------------------------------------------------------------------------
def order_metric(df1):
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux,
                 x='Order_Date',
                 y='ID',
                 labels={'Order_Date': 'Data', 'ID': 'Quantidade de Pedidos'})
    return fig

#--------------------------------------------------------------------------------
def pedidos_semana(df1):
    df_aux = df1.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN ", :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(
        df_aux,
        values='entregas_perc',
        names='Road_traffic_density')
    return fig

#--------------------------------------------------------------------------------
def cidade_trafego(df1):
    df_aux = df1_filtrado.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(
        df_aux, 
        x='City', 
        y='Road_traffic_density', 
        size='ID', 
        color='City')
    return fig

#--------------------------------------------------------------------------------
def entregas_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux = df_aux.sort_values('week_of_year')
    fig = px.line(
        df_aux, 
        x='week_of_year', 
        y='ID',
        labels={'week_of_year': 'Semana do Ano', 'ID': 'Quantidade de Pedidos'})
    return fig

#--------------------------------------------------------------------------------
def pedido_entregador_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    pedidos_por_semana = df1.groupby('week_of_year')['ID'].count().reset_index()
    entregadores_por_semana = df1.groupby('week_of_year')['Delivery_person_ID'].nunique().reset_index()
    df_aux = pd.merge(
        pedidos_por_semana,
        entregadores_por_semana,
        on='week_of_year',
        how='inner')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    df_aux = df_aux.sort_values('week_of_year')
    fig = px.line(
        df_aux, 
        x='week_of_year', 
        y='order_by_delivery',
        labels={'week_of_year': 'Semana do Ano', 'order_by_delivery': 'Pedidos por Entregador'})
    return fig
#--------------------------------------------------------------------------------

#_____________________________________________________________________

# Lendo o documento
df = pd.read_csv('train.crdownload')
df1 = df.copy()
#_____________________________________________________________________

# Limpeza dos dados
df1 = clean_code(df)


#====================================================================
#Barra lateral
#====================================================================

st.header('Marketplace - Visão Cliente') #mesma coisa que print

# inserindo imagem
# image_path = r'C:\Users\karen\OneDrive\Área de Trabalho\Cientista de Dados\Exercícios\Cury.png'
image = Image.open('Cury.png')
st.sidebar.image(image, width=200)

#_____________________________________________________________________

# inserindo a barra do lado
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Entregas mais rápidas da cidade')
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
st.header(f" Pedidos do dia: {selected_date.strftime('%d/%m/%Y')}")
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

linhas_selecionadas = df1['City'].isin(city_options)
df1_filtrado = df1.loc[linhas_selecionadas, :]
#st.dataframe(df1)

#====================================================================
#Layout no streamlit
#====================================================================

# criando abas
tab1, tab2, tab3 = st.tabs(['Visão Geral', 'Visão Tática', 'Visão Geográfica'])

#________________________________________________________________________________
with tab1:
    with st.container():
        st.markdown('## Entregas por Dia')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
           
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('## Pedidos por Semana')
            fig = pedidos_semana(df1)
            st.plotly_chart(fig, use_container_width=True)          
     
        with col2:
            st.markdown('## Volume de Pedidos por Cidade e Tipo de Trafego')
            fig = cidade_trafego(df1)
            st.plotly_chart(fig, use_container_width=True)

#________________________________________________________________________________
with tab2:
    with st.container():
        st.markdown("## Pedidos por Semana")
        fig = entregas_semana(df1)
        st.plotly_chart(fig, use_container_width=True)        
    
    with st.container():
        st.markdown("## A Quantidade de Pedidos por Entregador por Semana")
        fig = pedido_entregador_semana(df1)
        st.plotly_chart(fig, use_container_width=True)


       
#________________________________________________________________________________
with tab3:
    st.markdown("## Mapa da Cidade") 
    df_aux = df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux[df_aux['City'] != 'NaN ']
    df_aux = df_aux[df_aux['Road_traffic_density'] != 'NaN ']
    
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                   location_info['Delivery_location_longitude']],
                   popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600)
        