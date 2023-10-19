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

st.set_page_config(page_title='Visão Empresa', page_icon='', layout='wide')

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


def order_metric(df1):
    """ Recebe um dataframe,
        executa o dataframe e
        gera uma figura (gráfico)""" 
     
    df_aux = df1.loc[:,["ID", "Order_Date"]].groupby("Order_Date").count().reset_index()
        
    #Desenhando o grafico de barras:
            
    fig = px.bar(df_aux, x="Order_Date", y="ID")
    return fig


def traffic_order_share(df1):
    df_aux = df1.loc[:, ["ID", "Road_traffic_density"]].groupby("Road_traffic_density").count().reset_index()
    
    #É necessario fazer um cálculo para tranformar a quantidade em percentual:
    df_aux["entregas_perc"] = df_aux["ID"]/df_aux["ID"].sum()
    
    #Importar o gráfico de pizza:
    fig =  px.pie(df_aux, values="entregas_perc", names="Road_traffic_density")
    return fig


def traffic_order_city(df1):
     df_aux = df1.loc[:, ["ID","City","Road_traffic_density"] ].groupby(["City","Road_traffic_density"]).count().reset_index()
        
     #Importar gráfico de bolhas:
     fig = px.scatter(df_aux, x="City", y="Road_traffic_density", size="ID", color="City")
        
     return fig

def order_by_week(df1):
    #Criar a coluna de semana dentro do DataFrame:
    df1["Week_of_year"] = df1["Order_Date"].dt.strftime("%U")   #( %U o domingo sendo o primeiro dia da semana / %W a segunda sendo o primeiro dia da semana)
    
    #selecionar as linhas e agrupar pela coluna semana.
    df_aux = df1.loc[:, ["ID","Week_of_year"]].groupby("Week_of_year").count().reset_index()
    
    #Importar o gráfico de linhas.
    fig = px.line(df_aux, x="Week_of_year", y="ID")
    return fig

def order_share_by_week(df1):
    #Criar a coluna de semana dentro do datafreme
    df1["week_of_year"] = df1["Order_Date"].dt.strftime( '%U')    #( %U o domingo sendo o primeiro dia da semana / %W a segunda sendo o primeiro dia da semana)
    
    #Quantidade de pedidos por semana/Número único de entregadores por semana.
    df_aux01 = df1.loc[:,["ID","week_of_year"]].groupby("week_of_year").count().reset_index()
    df_aux02 = df1.loc[:, ["Delivery_person_ID","week_of_year"]].groupby("week_of_year").nunique().reset_index()
    
    #Juntar dois dataframe:
    df_aux = pd.merge(df_aux01, df_aux02, how="inner", on="week_of_year")
    
    #dividir os dataframe:
    df_aux["order_by_deliver"] = df_aux["ID"]/df_aux["Delivery_person_ID"]
    
    #Importar o gráfico de linhas:
    fig = px.line(df_aux, x="week_of_year",y="order_by_deliver")
    return fig

def country_maps(df1):
   
    df_aux = df1.loc[:,["City","Road_traffic_density","Delivery_location_latitude","Delivery_location_longitude"]].groupby(["City","Road_traffic_density"]).median().reset_index()
    
    #A mediana usa o proprio valor do conjunto de dados, diferente da média. Por isso nesse caso é usado a mediana.
    
    #Para desenhar o mapa é preciso das informações da latitude e longitude.
    
    map_restaurants = folium.Map()
    for index, location_info in df_aux.iterrows():
          folium.Marker([location_info["Delivery_location_latitude"],
                         location_info["Delivery_location_longitude"]],
                         popup=location_info[['City', 'Road_traffic_density']] ).add_to(map_restaurants)
    folium_static( map_restaurants, width=1024, height=600 )
    
    return None




#------------------------------------------------------------------Início da Estruturra Lógica do Código----------------------------------------------------------------------------------------------

#=============================================================================
#Import o Dataset:
#=============================================================================

df = pd.read_csv("train_ftc.csv")

#=============================================================================
#Limpando os dados:
#=============================================================================

df1 = clean_code(df)


#Visão Empresa:

df_aux = df1.loc[:,["ID", "Order_Date"]].groupby("Order_Date").count().reset_index()

#Desenhando o grafico de barras:
#Matiplotlib / plotly / Seaborn / Bokeh (tem várias opções de bibliotecas para criação de graficos)

px.bar(df_aux, x="Order_Date", y="ID")


#=============================================================================
#Barra lateral no Stremlit
#=============================================================================
st.header('Markeplace - Visão Empresa')

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
st.sidebar.markdown( '### Powered by Comunidade DS')

#Filtro de data
linhas_selecionadas= df1['Order_Date']< date_slider
df1=df1.loc[linhas_selecionadas,:]

#filtro de trânsito
linhas_selecionadas= df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

#===================================================================================
#Layout no Stremlit
#===================================================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
           
   
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)                 

        
        with col2:
            fig = traffic_order_city(df1)
            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width=True)
               

with tab2:
    with st.container():
        st.markdown( '# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
          

    with st.container():
        st.markdown("# Order Share by Week")
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        


with tab3:
    st.markdown( '# Country Maps')
    country_maps(df1)

   










