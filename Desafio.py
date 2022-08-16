import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import requests
import re
import datetime
import pandas as pd
r = requests.get('https://test.alertrack.com.br/api/test_web/profile/get/')

data = r.json()
ano = data['avancado']['nascimento'].split("/")
currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
year = date.strftime("%Y")
idade = int(year) - int(ano[2])
for e in range(len(data['avancado']['enderecos'])):
  cep = re.sub('[^\d]', '', data['avancado']['enderecos'][e]['cep'])
  CEP = requests.get('https://viacep.com.br/ws/'+cep+'/json/')
  data_cep = CEP.json()

servicos = {'NOME': [], 'STATUS': []}

for e in data['avancado']['servicos']:
    if data['avancado']['servicos'][e]['status'] == True:

        servicos['NOME'].append(e)
        servicos['STATUS'].append('ATIVADO')
    else:
        servicos['NOME'].append(e)
        servicos['STATUS'].append('DESATIVADO')
serv = pd.DataFrame(servicos)
serv.NOME = serv.NOME.str.upper()


















app = dash.Dash(external_stylesheets=[dbc.themes.MORPH])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [

        dbc.Nav(
            [
                dbc.Input(id="input", placeholder="DIGITE O CPF", type="text"),
                html.Br(),
                html.P(id="output"),
                html.Br(),
                dbc.Button("Buscar", color="dark", className="me-1"),
                html.Br(),
                dbc.NavLink("Info.Pessoais", href="/", active="exact"),
                dbc.NavLink("Endereços e Telefones", href="/page-1", active="exact"),
                dbc.NavLink("Info.Adicionais", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])





telefones = pd.DataFrame.from_dict(data['avancado']['telefones'])
telefones = telefones.drop(['parantesco'], axis=1)
telefones.rename(columns = {'telefone':'TELEFONE', 'tipo':'TIPO',
                              'nome':'NOME'}, inplace = True)
endereco = pd.DataFrame.from_dict(data['avancado']['enderecos'])
endereco['bairro'] = data_cep['bairro'].upper()
endereco.rename(columns = {'municipio':'MUNICIPIO', 'cep':'CEP',
                              'tipo_logradouro':'TIPO LOGRADOURO','logradouro':'LOGRADOURO','numero':'NUMERO','bairro':'BAIRRO'}, inplace = True)



table1 = dbc.Table.from_dataframe(
    endereco, striped=True, bordered=True, hover=True, index=False
)
table = dbc.Table.from_dataframe(
    telefones, striped=True, bordered=True, hover=True, index=False
)
table2 = dbc.Table.from_dataframe(
    serv, striped=True, bordered=True, hover=True, index=False
)



card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.CardImg(
                        src= data['avancado']['avatar'],

                    style={"position": "absolute", "top": 22, "right": 393, "width": 200}),
                    className="col-md-4",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [
                            dbc.ListGroup(
                            [
                                dbc.ListGroupItem("Nome :" + " "  +  data['avancado']['nome']),
                                dbc.ListGroupItem("Nascimento:" + " "  +  data['avancado']['nascimento']),
                                dbc.ListGroupItem("Idade:" + " "  + str(idade) + " ANOS"),
                                dbc.ListGroupItem("Sexo:" + " "  +  data['avancado']['sexo'].upper()),
                                dbc.ListGroupItem("Raça/Cor:" + " "  +  data['avancado']['raca_descricao'].upper()),
                                dbc.ListGroupItem("Nacionalidade:" + " "  +  data['avancado']['nacionalidade'].upper()),
                                dbc.ListGroupItem("Email:" + " "  +  data['avancado']['email_principal']),
                                dbc.ListGroupItem("Estado Civil:" + " "  +  data['avancado']['estado_civil'].upper()),
                                dbc.ListGroupItem("Escolaridade:" + " "  +  data['avancado']['escolaridade'].upper()),
                            ]),
                            #dbc.ListGroup(
                            #[
                              #  dbc.ListGroupItem("CPF"),
                              #  dbc.ListGroupItem("Titulo Eleitor"),
                              #  dbc.ListGroupItem("RG"),
                              #  dbc.ListGroupItem("RG UF"),
                           # ]),


                            html.Small(

                                className="card-text text-muted",
                            ),
                        ]
                    ),
                    className="col-md-8",
                ),
            ],
            className="g-0 d-flex align-items-center",
        )
    ],
    className="mb-3",
    style={"maxWidth": "600px"},
)

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return card
    elif pathname == "/page-1":


        return html.P("Endereço"),table1,html.P("Telefones"), table
    elif pathname == "/page-2":
        return html.P("Serviços Adquiridos"), table2
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


if __name__ == "__main__":
    app.run_server(port=8888)