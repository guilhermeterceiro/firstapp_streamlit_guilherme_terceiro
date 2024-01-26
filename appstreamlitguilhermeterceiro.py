import pandas as pd 
import numpy as np 
import plotly.express as px 
import streamlit as st
import datetime
import hvplot.pandas
import panel as pn
pn.extension()

#### Carregar o dados ####
df_hapvida = pd.read_csv("RECLAMEAQUI_HAPVIDA.csv")
df_ibyte = pd.read_csv("RECLAMEAQUI_IBYTE.csv")
df_nagem = pd.read_csv("RECLAMEAQUI_NAGEM.csv")

#### Acrescentar coluna empresa ####
df_hapvida['EMPRESA']='Hapvida'
df_ibyte['EMPRESA']='Ibyte'
df_nagem['EMPRESA']='Nagem'

#### CONCATENAÇAO ####
# Igualar as colunas para concatenação
colunas_ordenadas=df_hapvida.columns.sort_values()
df_hapvida=df_hapvida[colunas_ordenadas]
df_ibyte=df_ibyte[colunas_ordenadas]
df_nagem=df_nagem[colunas_ordenadas]

# Concatenar os dataframes
df = pd.concat([df_hapvida,df_ibyte,df_nagem])


#### Série temporal do número de reclamações
# Datatime
df['TEMPO']=pd.to_datetime(df['TEMPO'])


### Criar DataFrame
df_time = pd.pivot_table(df,values='ID',index='TEMPO',columns='EMPRESA',aggfunc=pd.Series.nunique)
df_time = df_time.reset_index()

#### Frequência de reclamações por estado.
# Criar coluna com UF
estado_lista=[]
for i in range(len(df)):
    estado_lista.append(df['LOCAL'].iloc[i][-2:])
df['ESTADO']=estado_lista

# Criar DataFrame
df_estado = pd.pivot_table(df,values='ID',index='ESTADO',columns='EMPRESA',aggfunc=pd.Series.nunique,fill_value=0)
df_estado = df_estado.reset_index()
df_estado = df_estado[~(df_estado['ESTADO']==' C')]
df_estado = df_estado[~(df_estado['ESTADO']==' P')]
df_estado = df_estado[~(df_estado['ESTADO']=='--')]
df_estado = df_estado[~(df_estado['ESTADO']=='ta')]
df_estado['Total'] = df_estado['Hapvida'] + df_estado['Ibyte'] + df_estado['Nagem']
df_estado.sort_values(by='Total', ascending=False, inplace = True)

#### Frequência de cada tipo de STATUS
df_status = df.STATUS.value_counts()
df_status.sort_values(ascending=False, inplace = True)

## Distribuição do tamanho do texto (coluna DESCRIÇÃO)
df['CONT_DESC'] = [len(i) for i in df['DESCRICAO']]




#### STREAMLIT###

# streamlit run appstreamlitguilhermeterceiro.py
st.title('RECLAME AQUI')


st.write('Informações sobre os dados brutos')
col1, col2, col3, col4= st.columns(4)
col1.metric(label="Número de colunas", value=len(df.columns))
col2.metric(label="Número de linhas", value=len(df))
col3.metric(label="Descrição mínima", value=df['CONT_DESC'].min())
col4.metric(label="Descrição máxima", value=df['CONT_DESC'].max())

col1, col2= st.columns(2)
col1.metric(label="Primeira data", value=df['TEMPO'].min().strftime("%Y-%m-%d"))
col2.metric(label="Última data", value=df['TEMPO'].max().strftime("%Y-%m-%d"))

with st.sidebar:
        st.title('Filtros')

        seletor_empresa=st.selectbox('Selecione a empresa', 
                                     list(df['EMPRESA'].unique()), 
                                     index=None, 
                                     placeholder='Selecione a empresa',
                                     label_visibility='collapsed')
        
        seletor_estado=st.selectbox('Selecione o estado',
                                    list(df_estado['ESTADO'].unique()), 
                                    index=None, 
                                    placeholder='Selecione o estado',
                                    label_visibility='collapsed')
        
        seletor_status=st.selectbox('Selecione a status',
                                    list(df['STATUS'].unique()), 
                                    index=None, 
                                    placeholder='Selecione a status',
                                    label_visibility='collapsed')
        
        start_desc, end_desc = st.select_slider(
            'Selecione o intervalo do tamanho do texto da coluna Descrição',
            options=list(range(df['CONT_DESC'].min(),df['CONT_DESC'].max()+1,1)),
            value=(df['CONT_DESC'].min(), df['CONT_DESC'].max()))

        st.write('Selecione o período de análise')
        #col1, col2= st.columns(2)
        ini=st.date_input("Data inicial", value=df['TEMPO'].min())
        fim=st.date_input("Data final", value=df['TEMPO'].max())

        options = st.multiselect(
            'Selecione as colunas',
            list(df.columns),
            list(df.columns))




#### Após os Filtros

if seletor_empresa!=None:
    df = df[df['EMPRESA'] == seletor_empresa] 
if seletor_estado!=None:
    df = df[df['ESTADO'] == seletor_estado]
if seletor_status!=None:
    df = df[df['STATUS'] == seletor_status]
df = df[(df['CONT_DESC']>=start_desc) & (df['CONT_DESC']<=end_desc)]
df = df[(df['TEMPO']>=(pd.to_datetime(ini))) & (df['TEMPO']<=(pd.to_datetime(fim)))]

# Verificação se existe dado selecionado 
if len(df) == 0:
    st.write('Nenhum dado para visualizar.')
else:
    
    ### Criar DataFrame
    df_time = pd.pivot_table(df,values='ID',index='TEMPO',columns='EMPRESA',aggfunc=pd.Series.nunique)
    df_time = df_time.reset_index()

    #### Frequência de reclamações por estado.
    # Criar coluna com UF
    estado_lista=[]
    for i in range(len(df)):
        estado_lista.append(df['LOCAL'].iloc[i][-2:])
    df['ESTADO']=estado_lista

    # Criar DataFrame
    df_estado = pd.pivot_table(df,values='ID',index='ESTADO',columns='EMPRESA',aggfunc=pd.Series.nunique,fill_value=0)
    df_estado = df_estado.reset_index()
    df_estado = df_estado[~(df_estado['ESTADO']==' C')]
    df_estado = df_estado[~(df_estado['ESTADO']==' P')]
    df_estado = df_estado[~(df_estado['ESTADO']=='--')]
    df_estado = df_estado[~(df_estado['ESTADO']=='ta')]

    if seletor_empresa!=None:
        df_estado.sort_values(by=seletor_empresa, ascending=False, inplace = True)
    else:
        for i in list(df['EMPRESA'].unique()):
            df_estado['Total'] = df_estado[i]
        df_estado.sort_values(by='Total', ascending=False, inplace = True)

    #### Frequência de cada tipo de STATUS
    df_status = df.STATUS.value_counts()
    df_status.sort_values(ascending=False, inplace = True)

    ## Distribuição do tamanho do texto (coluna DESCRIÇÃO)
    df['CONT_DESC'] = [len(i) for i in df['DESCRICAO']]

    st.markdown('---')
    st.write('Dados após aplicação dos filtros')
    st.dataframe(df[options][(df['TEMPO'] >= pd.to_datetime(ini)) & (df['TEMPO'] <= pd.to_datetime(fim))],
                column_config={"ANO":st.column_config.NumberColumn(format='%f'),
                                "ID":st.column_config.NumberColumn(format='%f'),
                                "CONT_DESC":st.column_config.NumberColumn(format='%f'),},
                                hide_index=True)

    st.markdown('---')
    if seletor_empresa!=None:
        fig1=px.line(df_time,x='TEMPO',y=seletor_empresa,title='Série temporal do número de reclamações',
                labels={'TEMPO':'Data','value':'Reclamações'})
    else:
        fig1=px.line(df_time,x='TEMPO',y=list(df['EMPRESA'].unique()),title='Série temporal do número de reclamações',
                labels={'TEMPO':'Data','value':'Reclamações'})
    st.plotly_chart(fig1)

    st.markdown('---')
    st.write('Frequência de reclamações por Estado')
    col1, col2= st.columns(2,gap="small")
    col1.dataframe(df_estado,hide_index=True)
    #             column_config={"Hap":st.column_config.NumberColumn(format='%f'),
    #                            "ID":st.column_config.NumberColumn(format='%f'),
    #                            "CONT_DESC":st.column_config.NumberColumn(format='%f'),})

    if seletor_empresa!=None:
        fig2=px.bar(df_estado.sort_values(by=seletor_empresa, ascending=True),
                y='ESTADO',x=seletor_empresa,labels={'ESTADO':'Estado',seletor_empresa:'Frequência'})
    else:
        fig2=px.bar(df_estado.sort_values(by='Total', ascending=True),
                y='ESTADO',x='Total',labels={'ESTADO':'Estado','Total':'Frequência Total'})
    col2.plotly_chart(fig2,use_container_width=True)

    st.markdown('---')

    st.write('Frequência de reclamações por Status')
    col1, col2 = st.columns([0.3, 0.7],gap="small")
    col1.dataframe(df_status)
    fig3=px.bar(df_status,x=df_status.index,y=df_status.values,labels={'index':'Status','y':'Frequência'})
    col2.plotly_chart(fig3,use_container_width=True)

    st.markdown('---')
    st.write('Distribuição do tamanho do texto da coluna Descrição')
    fig4=px.histogram(df,x=['CONT_DESC'],labels={'value':'Tamanho da descrição'})
    fig4.update_layout(yaxis_title='Frequência',showlegend=False)
    st.plotly_chart(fig4)

col1, col2= st.columns([0.7, 0.3])

col2.write('by Guilherme Terceiro')





