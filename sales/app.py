from http import server
from re import template
from tokenize import group
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template

load_figure_template("pulse")

import pandas as pd
import numpy as np
import dash
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

df_data = pd.read_csv("supermarket_sales.csv")
df_data["Date"] = pd.to_datetime(df_data["Date"])


app = dash.Dash(
    external_stylesheets=[dbc.themes.PULSE]
)
server = app.server


# =========  Layout  =========== #

#A estrutura começa com um html.Div que recebe uma lista de children. Essa lista contém uma única dbc.Row com duas dbc.Col, cada uma contendo elementos diferentes da interface.
app.layout = html.Div(children=[
#A primeira coluna contém um dbc.Card com um título, uma linha horizontal (html.Hr()) e dois elementos html.H5 para selecionar as cidades e a variável de análise. 
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H2("Sales",style = {"font-family":"Voltaire","font-size":"60px","margin-left":"50px"}),
                            html.Hr(),

# O dcc.Checklist é utilizado para selecionar as cidades, exibindo uma lista com todas as cidades presentes no dataframe df_data. 

                            html.H5("Cidades:"),
                            dcc.Checklist(df_data["City"].value_counts().index,
                            df_data["City"].value_counts().index, id="check_city",
                            inputStyle = {"margin-right":"5px","margin-left":"20px"}),
#Já o dcc.RadioItems é utilizado para escolher a variável de análise, que pode ser "gross income" ou "Rating".
                            html.H5("Variável de análise:",style = {"margin-top":"30px"}),
                            dcc.RadioItems(["gross income", "Rating"],"gross income", id="main_variable",
                            inputStyle = {"margin-right":"5px","margin-left":"20px"}),
                        ],style = {"height":"90vh","margin":"20px","padding":"15px"})

                    ],sm=2),
#A primeira linha possui três colunas com um gráfico cada uma. Os gráficos são identificados por seus respectivos ids: "city_fig", "gender_fig" e "pay_fig". Cada coluna tem tamanho "sm=4", indicando que cada uma deve ocupar 4 das 12 colunas disponíveis para a coluna atual.

#A segunda linha possui apenas uma coluna que contém um único gráfico identificado pelo id "income_per_date_fig".

#A terceira linha também possui apenas uma coluna com um único gráfico identificado pelo id "income_per_product_fig". Esta coluna também deve ocupar todo o espaço disponível para a coluna atual.

                    dbc.Col([
                        dbc.Row([
                            dbc.Col([dcc.Graph(id="city_fig"),],sm=4),
                            dbc.Col([dcc.Graph(id="gender_fig"),],sm=4),
                            dbc.Col([dcc.Graph(id="pay_fig"),],sm=4)
                        ]),
                        dbc.Row([dcc.Graph(id="income_per_date_fig")]),
                        dbc.Row([dcc.Graph(id="income_per_product_fig")]),
                    ],sm=10)
                ])
            ])
        


# =========  Layout  =========== #

#Os outputs são cinco figuras: "city_fig", "gender_fig", "pay_fig", "income_per_date_fig" e "income_per_product_fig". Essas figuras são atualizadas sempre que há uma alteração nos inputs.
@app.callback([
                Output("city_fig", "figure"),
                Output("gender_fig", "figure"),
                Output("pay_fig", "figure"),
                Output("income_per_date_fig", "figure"),
                Output("income_per_product_fig", "figure"),
            ], #Os inputs "check_city" e "main_variable" são passados como argumentos para a função de retorno de chamada.
                [
                    Input("check_city", "value"),
                    Input("main_variable", "value"),
                ])



def render_page_content(cities, main_variable):

#A primeira linha define uma variável operation que recebe a função np.sum se main_variable for igual a "gross income" e np.mean caso contrário.

#Em seguida, é criado um DataFrame chamado df_filtered, que recebe apenas as linhas do DataFrame original df_data cujas cidades estejam presentes na lista cities.
    operation = np.sum if main_variable == "gross income" else np.mean
    df_filtered = df_data[df_data["City"].isin(cities)]

#São então criados mais três DataFrames: df_city, df_gender e df_payment.  

#df_city agrupa as informações por cidade e calcula a soma ou média da variável principal (main_variable).

#df_gender agrupa as informações por gênero e cidade e calcula a soma ou média da variável principal.

#df_payment agrupa as informações por método de pagamento e calcula a soma ou média da variável principal.

    df_city = df_filtered.groupby("City")[main_variable].apply(operation).to_frame().reset_index()
    df_gender = df_filtered.groupby(["Gender","City"])[main_variable].apply(operation).to_frame().reset_index()
    df_payment = df_filtered.groupby(["Payment"])[main_variable].apply(operation).to_frame().reset_index()


#df_income_per_time: é agrupado por data e cidade e calcula a operação definida pela variável operation (que é uma soma se a variável principal for "gross income" e uma média caso contrário) na coluna main_variable. Depois o resultado é armazenado em um novo dataframe df_income_per_time com as colunas Date, City e main_variable.

#df_product_income: é agrupado por linha de produto e cidade e calcula a operação definida pela variável operation na coluna main_variable. Depois o resultado é armazenado em um novo dataframe df_product_income com as colunas Product line, City e main_variable.

    df_income_per_time= df_filtered.groupby(["Date", "City"])[[main_variable]].apply(operation).reset_index()

    df_product_income = df_filtered.groupby(["Product line", "City"])[[main_variable]].apply(operation).reset_index()

#fig_city: um gráfico de barras que mostra a variável principal para cada cidade no dataframe df_city. O eixo x representa as cidades e o eixo y representa a variável principal.

#fig_gender: um gráfico de barras agrupadas que mostra a variável principal para cada combinação de gênero e cidade no dataframe df_gender. O eixo x representa os gêneros, o eixo y representa a variável principal e as barras são coloridas pela cidade.

#fig_payment: um gráfico de barras horizontal que mostra o método de pagamento no eixo y e a variável principal no eixo x.

    fig_city = px.bar(df_city, x="City", y=main_variable)
    fig_gender = px.bar(df_gender, y=main_variable, x="Gender",color="City",barmode="group")
    fig_payment = px.bar(df_payment, y="Payment", x=main_variable, orientation="h")

#fig_income_per_date: um gráfico de barras que mostra a variável principal ao longo do tempo para cada cidade presente no dataframe df_income_per_time. O eixo x representa as datas e o eixo y representa a variável principal.
#fig_product_income: um gráfico de barras horizontal que mostra a receita total ou média para cada linha de produto em cada cidade presente no dataframe df_product_income. O eixo x representa a variável principal e o eixo y representa as linhas de produto, com as barras coloridas por cidade.

    fig_income_per_date = px.bar(df_income_per_time, x="Date", y=main_variable)

    fig_product_income = px.bar(df_product_income, x=main_variable, y="Product line", color="City", orientation="h")

    
#Esse bloco de código atualiza a aparência dos gráficos criados anteriormente. Ele percorre uma lista de gráficos [fig_city, fig_payment, fig_gender, fig_income_per_date] e atualiza o layout de cada um deles, definindo margens, altura e template. Além disso, ele também atualiza o layout do gráfico fig_product_income com valores diferentes de margem e altura. Por fim, ele retorna todos os cinco gráficos.
    for fig in [fig_city, fig_payment,fig_gender,fig_income_per_date]:
        fig.update_layout(margin=dict(l=0, r=20, t=20, b=20), height=200,template="pulse")
    fig_product_income.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=500)
    
    return fig_city,fig_gender,fig_payment,fig_income_per_date,fig_product_income



if __name__ == "__main__":
    app.run_server(debug=False,use_reloader=False)
