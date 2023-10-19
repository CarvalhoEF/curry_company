#Libraries
import plotly.express as px
import folium as folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static


import subprocess

# Comando para instalar o pacote haversine
comando = "pip install haversine"

# Executar o comando usando o subprocess
subprocess.check_call(comando, shell=True)

st.set_page_config(page_title='Visão Entregadores', page_icon='', layout='wide')

# -----------------------------------------------------------------------------
# Funções
# -----------------------------------------------------------------------------

def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe:
        Tipos de limpeza:
        1. Remoção dos NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de Datas
        5. Limpeza da coluna de tempo (remoção do texto da variável númerica)

        Input:Dataframe
        Output:Dataframe
    """
    #1ª limpeza -> converter a coluna Age de texto para número
    
    linhas_selecionadas = df1["Delivery_person_Age"] != 'NaN '  # (!=) é o sinal de diferente
    
    df1 = df1.loc[linhas_selecionadas, :]
    
    df1 ["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)
    
    #2ª limpeza -> converter a coluna Delivery_person_Ratings  que está como string para float
    
    df1["Delivery_person_Ratings"] = df1[ "Delivery_person_Ratings"].astype(float)
    
    #3ª limpeza -> convertendo a coluna order_date de texto para data
    
    df1["Order_Date"] = pd.to_datetime( df1["Order_Date"], format="%d-%m-%Y")   #esse código é uma mascara para o formato da data
    
    #4ª limpeza -> convertenndo multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = df1["multiple_deliveries"] != "NaN "
    df1 =df1.loc[linhas_selecionadas,:]
    df1["multiple_deliveries"] = df1["multiple_deliveries"].astype(int)
    
    linhas_selecionadas = df1["Road_traffic_density"] != "NaN "
    df1 = df1.loc[linhas_selecionadas,:]
    
    linhas_selecionadas = df1["City"] != "NaN "
    df1 = df1.loc[linhas_selecionadas,:]
    
    #5ª limpeza -> Removendo os espaços denro de strings/texto/object
    df1.loc[:, "ID"] = df1.loc[:, "ID"].str.strip()
    df1.loc[:, "Road_traffic_density"] = df1.loc[:, "Road_traffic_density"].str.strip()
    df1.loc[:, "Type_of_order"] = df1.loc[:, "Type_of_order"].str.strip()
    df1.loc[:, "Type_of_vehicle"] = df1.loc[:, "Type_of_vehicle"].str.strip()
    df1.loc[:, "City"] = df1.loc[:, "City"].str.strip()
    
    
    #6ª limpeza -> Comando para remover o texto de números
    df1 = df1.reset_index( drop=True )
    
    #7ª limpeza -> Retirando os numeros da coluna Time_taken(min)
    df1["Time_taken(min)"] = df1["Time_taken(min)"].apply(lambda x: x.split("(min)")[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
           
    #8ª limpeza -> Retirando os espaços da coluna Festival
    df1['Festival'] = df1['Festival'].str.strip()

    return df1

def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ["Delivery_person_ID", "City", "Time_taken(min)"] ]
              .groupby( ["City", "Delivery_person_ID"] )
              .mean()
              .sort_values( ['City', 'Time_taken(min)'], ascending=top_asc )
              .reset_index())
    
    df_aux01 = df2.loc[df2["City"] == "Metropolitian", :].head(10)
    df_aux02 = df2.loc[df2["City"] == "Urban", :].head(10)
    df_aux03 = df2.loc[df2["City"] == "Semi-Urban", :].head(10)
    
    df3 = pd.concat( [df_aux01,df_aux02,df_aux03] ).reset_index(drop=True)
    
    return df3

#------------------------------------------------------------------Início da Estruturra Lógica do Código----------------------------------------------------------------------------------------------

#=============================================================================
#Import o Dataset:
#=============================================================================


df = pd.read_csv("train_ftc.csv")


#=============================================================================
#Limpando os dados:
#=============================================================================

df1 = clean_code(df)



#Visão Entregadores:

#===============================================================
#Barra lateral no Streamlit
#===============================================================
st.header('Markeplace - Visão Entregadores')

image_path = 'logo.png'
image = Image.open ( image_path )
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '# Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value = datetime(2023, 4, 13),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')



st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""---""")

conditions = st.sidebar.multiselect(
    'Quais as condições climáticas',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default = ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Cloudy', 'conditions Fog', 'conditions Windy'] )


st.sidebar.markdown("""---""")
st.sidebar.markdown( '### Powered by Comunidade DS')


#Filtro de data
#(date_slider é a variavel que vai recebero o valor do usúario)
linhas_selecionadas= df1['Order_Date'] < date_slider 
df1=df1.loc[linhas_selecionadas,:]

#filtro de trânsito
linhas_selecionadas= df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]


#filtro condições climáticas
linhas_selecionadas= df1['Weatherconditions'].isin(conditions)
df1 = df1.loc[linhas_selecionadas,:]



#===============================================================
#Layout no Streamlit
#===============================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #A maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age' ].max()
            col1.metric("Maior idade", maior_idade)
        
        with col2:
            #A menor idade dos entregadores
            
            menor_idade = df1.loc[:, 'Delivery_person_Age' ].min()
            col2.metric("Menor idade", menor_idade)
            
        with col3:
            #A melhor condição de veículo
           
            melhor_vehicle = df1.loc[:, 'Vehicle_condition' ].max()
            col3.metric( "Melhor condição de veículo", melhor_vehicle)
        
        with col4:
            #A pior condição de veículo
           
            pior_vehicle = df1.loc[:, 'Vehicle_condition' ].min()
            col4.metric( "Pior condição de veículo", pior_vehicle)

    
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregdor:')
            df_avg_ratings_per_deliver =( df1.loc[:, ["Delivery_person_Ratings", "Delivery_person_ID"]]
                                             .groupby("Delivery_person_ID")
                                             .mean()
                                             .reset_index() )
            st.dataframe(df_avg_ratings_per_deliver)
                  
            
        with col2:         
            st.markdown('##### Avaliação média por trânsito:')
            
            avaliacao_trafico =(df1.loc[:,["Delivery_person_Ratings","Road_traffic_density"]]
                                   .groupby("Road_traffic_density")
                                   .agg( {"Delivery_person_Ratings": ["mean","std"]}) )
            #renomear coluna
            avaliacao_trafico.columns = ["delivery_mean","delivery_std"]
                        
            #reset do index
            avaliacao_trafico = avaliacao_trafico.reset_index()

            st.dataframe(avaliacao_trafico)


           
            st.markdown('##### Avaliação média por clima:')
            avaliacao_condicoes_clima =(df1.loc[:,["Delivery_person_Ratings","Weatherconditions"]]
                                           .groupby("Weatherconditions")
                                           .agg( {"Delivery_person_Ratings": ["mean","std"]}) )

            #renomear coluna
            avaliacao_condicoes_clima.columns = ["delivery_mean","delivery_std"]
                        
            #reset do index
            avaliacao_condicoes_clima = avaliacao_condicoes_clima.reset_index()
            st.dataframe(avaliacao_condicoes_clima)

    

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1,col2 = st.columns(2)
        with col1:
            st.markdown('##### Top 10 - Entregadores mais rápidos:')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)

        
        with col2:
            st.markdown('##### Top 10 - Entregadores mais lentos:')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
    

            

    
























    