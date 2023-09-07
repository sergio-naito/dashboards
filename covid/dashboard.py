import plotly.graph_objs as go # Biblioteca utilizada para criação de gráficos
import dash # Biblioteca utilizada para criação do dashboard
import pandas as pd # Biblioteca utilizada para manipulação de dados em formato de tabela
import dash_core_components as dcc # Componentes do Dash para criação do layout
import dash_html_components as html # Componentes do Dash para criação do layout
from dash.dependencies import Input, Output # Dependências do Dash para criação de callbacks

# Carregando os dados
df = pd.read_csv('https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv')
df.columns
# Criando a aplicação do Dash
app = dash.Dash(__name__)
#Essa linha de código converte a coluna 'date' do dataframe 'df' para o tipo datetime, utilizando o formato ano-mês-dia.
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Criando as opções do dropdown com as siglas dos estados
options = [{'label': uf, 'value': uf} for uf in df['state'].unique()]

#Título: "Dashboard COVID-19 no Brasil"
#Dois gráficos de linha, um para casos confirmados e outro para óbitos confirmados, com IDs "graph_casos" e "graph_obitos", respectivamente
#Dois componentes de entrada: um menu suspenso para selecionar o estado e um seletor de data para escolher a data final para o intervalo de tempo dos dados. Esses componentes têm IDs "dropdown_estado" e "datepicker_data", respectivamente
#Um painel com informações resumidas do estado selecionado com IDs "estado_selecionado", "data_selecionada", "num_casos", "num_obitos", "num_recuperados" e "num_acompanhamento". Essas informações são atualizadas de acordo com o estado selecionado e a data final escolhida.
app.layout = html.Div([
    html.H1('Dashboard COVID-19 no Brasil'),
    html.Div([
        dcc.Graph(id='graph_casos', style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='graph_obitos', style={'width': '49%', 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Dropdown(id='dropdown_estado', options=options, placeholder='Selecione um estado'),
        dcc.DatePickerSingle(id='datepicker_data', date=df['date'].max(), max_date_allowed=df['date'].max()),
    ], style={'width': '30%', 'margin': 'auto'}),
    html.Div([
        html.H2('Resumo do estado'),
        html.P('Estado: ', style={'display': 'inline-block'}),
        html.P(id='estado_selecionado', style={'display': 'inline-block', 'fontWeight': 'bold'}),
        html.Br(),
        html.P('Data: ', style={'display': 'inline-block'}),
        html.P(id='data_selecionada', style={'display': 'inline-block', 'fontWeight': 'bold'}),
        html.Br(),
        html.P('Número de casos confirmados: ', style={'display': 'inline-block'}),
        html.P(id='num_casos', style={'display': 'inline-block', 'fontWeight': 'bold'}),
        html.Br(),
        html.P('Número de óbitos confirmados: ', style={'display': 'inline-block'}),
        html.P(id='num_obitos', style={'display': 'inline-block', 'fontWeight': 'bold'}),
        html.Br(),
        html.P('Número de casos recuperados: ', style={'display': 'inline-block'}),
        html.P(id='num_recuperados', style={'display': 'inline-block', 'fontWeight': 'bold'}),
        html.Br(),
        html.P('Número de casos em acompanhamento: ', style={'display': 'inline-block'}),
        html.P(id='num_acompanhamento', style={'display': 'inline-block', 'fontWeight': 'bold'}),
        html.Br(),
    ], style={'width': '30%', 'margin': 'auto'}),
])

#Ambas as funções recebem um DataFrame, um estado (uf) e uma data como parâmetros e retornam um DataFrame filtrado com as informações desejadas. A primeira função (filter_data) filtra o DataFrame por estado e data, enquanto a segunda (filter_data2) filtra por estado e intervalo de datas. Em ambas, se o parâmetro correspondente não for informado, não haverá filtragem por ele. O DataFrame filtrado é retornado ao final de cada função
def filter_data(df, uf, date):
    if uf:
        df = df[df['state'] == uf]
    if date:
        df = df[df['date'] == date]
    return df

def filter_data2(df, uf, start_date, end_date):
    if uf:
        df = df[df['state'] == uf]
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    return df

# define a primeira data disponível no dataframe
start_date = df['date'].min()
#Essa função é um callback que recebe dois inputs: o valor do dropdown de estado e a data selecionada no datepicker. Com base nesses inputs, ela chama a função filter_data2 para filtrar o dataframe df e obter um dataframe filtrado df_filtered.
@app.callback([Output('graph_casos', 'figure'), Output('graph_obitos', 'figure')],
              [Input('dropdown_estado', 'value'), Input('datepicker_data', 'date')])
#Em seguida, ela cria duas figuras usando o plotly: uma para representar o número de novos casos confirmados por data e outra para representar o número de novos óbitos confirmados por data. Para cada figura, é adicionado um trace do tipo scatter com os valores de data e novos casos/novos óbitos confirmados. Também são adicionados títulos aos gráficos e rótulos aos eixos x e y.
def update_graph_casos(uf, end_date):
    df_filtered = filter_data2(df, uf, start_date, end_date)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['newCases'], name='Novos casos confirmados'))
    fig1.update_layout(title='Novos casos confirmados', xaxis_title='Data', yaxis_title='Número de casos')
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['newDeaths'], name='Novos óbitos confirmados'))
    fig2.update_layout(title='Novos óbitos confirmados', xaxis_title='Data', yaxis_title='Número de óbitos na data')
    return fig1, fig2
    

# A função update_data é um callback que é acionado sempre que há uma alteração no valor do dropdown de estados ou na data selecionada no datepicker. Ele chama a função filter_data para filtrar o DataFrame de acordo com o estado e a data selecionados e, em seguida, atribui os valores correspondentes às variáveis estado, data, casos, obitos, recuperados e novos_Casos. Esses valores são então retornados como saídas para serem exibidos nos componentes correspondentes na interface do usuário.
@app.callback([Output('estado_selecionado', 'children'),
               Output('data_selecionada', 'children'),
               Output('num_casos', 'children'),
               Output('num_obitos', 'children'),
               Output('num_recuperados', 'children'),
               Output('num_acompanhamento', 'children')],
              [Input('dropdown_estado', 'value'), Input('datepicker_data', 'date')])
def update_data(uf, date):
    df_filtered = filter_data(df, uf, date)
    estado = ''
    data = ''
    casos = ''
    obitos = ''
    recuperados = ''
    novos_Casos = ''
#A função recebe um DataFrame filtrado e itera sobre cada linha dele. Em cada linha, a função verifica se o valor da coluna é nulo (pd.isnull) e, se for, atribui uma string vazia à variável correspondente. Se o valor não for nulo, a função atribui o valor da coluna à variável correspondente.
    for i, row in df_filtered.iterrows():
        if pd.isnull(row['state']):
            estado = ''
        else:
            estado = row['state']

        if pd.isnull(row['date']):
            data = ''
        else:
            data = row['date'].date()

        if pd.isnull(row['totalCases']):
            casos = ''
        else:
            casos = row['totalCases']

        if pd.isnull(row['deaths']):
            obitos = ''
        else:
            obitos = row['deaths']

        if pd.isnull(row['recovered']):
            recuperados = ''
        else:
            recuperados = row['recovered']

        if pd.isnull(row['newCases']):
            novos_Casos = ''
        else:
            novos_Casos = row['newCases']
   #A função retorna as variáveis estado, data, casos, obitos, recuperados e novos_Casos, que representam respectivamente o estado da federação, a data do registro, o número total de casos, o número total de óbitos, o número total de recuperados e o número de novos casos.         
    return estado, data, casos, obitos, recuperados, novos_Casos

if __name__ == '__main__':
    app.run_server(debug=False, port=8051)


  