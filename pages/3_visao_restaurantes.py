#Libraries
import plotly.express as px
import folium as folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import numpy as np

from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
from haversine import haversine

import subprocess

# Comando para instalar o pacote haversine
comando = "pip install haversine"

# Executar o comando usando o subprocess
subprocess.check_call(comando, shell=True)

st.set_page_config(page_title='Visão Restaurantes', page_icon='', layout='wide')

# -----------------------------------------------------------------------------
# Funções
# -----------------------------------------------------------------------------

def clean_code(df1):

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
    
    
    #df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: re.findall( r'\d+', x))
    #df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    #8ª limpeza -> Retirando os espaços da coluna Festival
    df1['Festival'] = df1['Festival'].str.strip()
    return df1

def distance(df1):
    #Distância média das entregas
    cols = ['Restaurant_latitude', 'Restaurant_longitude',	'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols].apply( lambda x: 
                               haversine( ( x["Restaurant_latitude"], x["Restaurant_longitude"]),
                                          ( x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
    
    avg_distance = np.round(df1['distance'].mean(),2)
    return avg_distance


def  avg_std_time_delivery(df1, festival, op):
    """ 
        Esta funççao calcula o tempo médiro e o desvio padrão do tempo de entrega. 
        Parâmetros:
            Input:
            -df:Dataframe com os dados necessarios para o cálculo
            -op/:Tipo de operação que precisa ser calculado
            'avg_time': Calcula o tempo médio
            'std_time': Calcula o desvio padrão do tempo.
            Output:
            -df: Dataframe com a 2 colunas e 1 linha.
    """
    #Tempo médio de entrega por festival
    cols = ['Time_taken(min)', 'Festival']
    
    df_aux = df1.loc[:, cols].groupby("Festival").agg({'Time_taken(min)':['mean', 'std']})
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    
    df_aux = np.round(df_aux.loc[df_aux["Festival"] == festival, op ],2)
    return df_aux

def avg_std_time_graph(df1):
    cols = ['Time_taken(min)', 'City']
    
    df_aux = df1.loc[:,cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    
    df_aux.columns = ['avg_time','std_time']
    
    df_aux = df_aux.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                         x=df_aux['City'],
                         y=df_aux['avg_time'],
                         error_y=dict(type='data', array= df_aux['std_time'] ), marker=dict(color= 'blue' )))
    return fig


def avg_std_time_on_traffic(df1):
    cols = ['Time_taken(min)', 'City', 'Road_traffic_density']
    
    df_aux = df1.loc[:,cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    
    df_aux.columns = ['avg_time','std_time']
    
    df_aux = df_aux.reset_index()
    
    fig = px.sunburst( df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='Viridis', color_continuous_midpoint=np.average(df_aux['std_time']))
   
    return fig


def distanci_vga_city(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude',	'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols].apply( lambda x: 
              haversine( ( x["Restaurant_latitude"], x["Restaurant_longitude"]),
                         ( x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
    
    avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City').mean().reset_index()
    cores = ['blue', 'green', 'red']
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0],  marker=dict(colors=cores, line=dict(color='white', width=2) ) )])
    
    return fig



#------------------------------------------------------------------Início da Estruturra Lógica do Código----------------------------------------------------------------------------------------------

#=============================================================================
#Import o Dataset:
#=============================================================================

df = pd.read_csv("train_ftc.csv")

# Fazer uma cópia do dataframe lido

df1 = clean_code(df)


#Visão Restaurantes:

#===============================================================
#Barra lateral no Streamlit
#===============================================================

st.header('Markeplace - Visão Restaurantes')

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
       st.markdown("""---""")
       st.title('Overal Metrics')

       col1, col2, col3 = st.columns(3)
       #Quantidade de entregadores únicos
       with col1:  
           entregadores_unicos= len(df1['Delivery_person_ID'].unique())
           col1.metric( 'Entregadores únicos:', entregadores_unicos)
           
       with col2:
           avg_distance = distance(df1)
           col2.metric('A distância media das entregas(Km):', avg_distance)        
          
           
       with col3:
           df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
           col3.metric('Tempo médio Entrega/Festival', df_aux)
         

           
    with st.container():
       st.markdown("""---""")
              
       col1, col2, col3 = st.columns(3)
       with col1:
           #Desvio padrão do Tempo médio de entrega por festival
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col1.metric('STD entrega/Festival', df_aux)
           
           
       with col2:
           #Tempo médio de entrega quando NÂO é  festival
           df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
           col2.metric('Tempo médio Não Festival', df_aux)
           
                     
       with col3:
           #Desvio padrão do Tempo médio de entrega quando NÂO é festival
           df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
           col3.metric('STD Não Festival', df_aux)
           
                    
    with st.container():
        st.markdown("""---""")
        st.title('Tempo médio de entrega por cidade')

        fig = avg_std_time_graph(df1)
        st.plotly_chart( fig)

            
    with st.container():
       st.markdown("""---""") 
       st.title('Distribuição do Tempo')

        
       st.markdown('##### Distribuição da distância média por cidade:')
       fig = distanci_vga_city(df1)         
       st.plotly_chart( fig)
        
           
    with st.container():
       st.markdown("""---""") 
           
       st.markdown('##### Distribuição de entrega por cidade e tipo de tráfego:')
       fig = avg_std_time_on_traffic(df1)
       st.plotly_chart(fig)
                        
        
    with st.container():
       st.markdown("""---""") 
       st.title('Distribuição da Distância')
        
       cols = ['Time_taken(min)', 'City', 'Type_of_order']

       aux01 = df1.loc[:,cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
        
       aux01.columns = ['avg_time','std_time']
        
       aux01.reset_index()
       st.dataframe(aux01)


































