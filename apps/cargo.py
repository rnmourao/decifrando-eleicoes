# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Event, Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from cepesp import *
import numpy
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

from app import app

print('entrou cargo')

estilo = {
            'card-pessoas' : {'background': '#6284f7',
                              'color': '#ffffff',
                              'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                              'transition': '0.3s',
                              'padding': '2px 16px',
                            #   'border-spacing': 5px,
                              'width': '15%',
                              'display': 'table-cell'                          }, #8ca9f9
            'card-1-turno' : {'background': '#d92171',
                              'color': '#ffffff',
                              'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                              'transition': '0.3s',
                              'padding': '2px 16px',
                              'width': '15%',
                              'display': 'table-cell'                         }, #e45d9b
            'card-2-turno' : {'background': '#f9be05',
                              'color': '#ffffff',
                              'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                              'transition': '0.3s',
                              'padding': '5px 16px',
                              'width': '15%',
                              'display': 'table-cell'
                              }, #f5da76
            'card-custos' : {'background': '#63b82a',
                              'color': '#ffffff',
                              'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                              'transition': '0.3s',
                              'padding': '5px 16px',
                              'width': '15%',
                              'display': 'table-cell'
                              } #93cf68
}

# combos
cargos = [{'label': 'Presidente', 'value': CARGO.PRESIDENTE},
          {'label': 'Governador', 'value': CARGO.GOVERNADOR},
          {'label': 'Senador', 'value': CARGO.SENADOR},
          {'label': 'Deputado Federal', 'value': CARGO.DEPUTADO_FEDERAL},
          {'label': 'Deputado Estadual', 'value': CARGO.DEPUTADO_ESTADUAL},
          {'label': 'Deputado Distrital', 'value': CARGO.DEPUTADO_DISTRITAL},
          {'label': 'Prefeito', 'value': CARGO.PREFEITO},
          {'label': 'Vereador', 'value': CARGO.VEREADOR}]

ufs = [
# {'label': 'Brasil', 'value': 'BR'},
{'label': 'Acre', 'value': 'AC'},
{'label': 'Alagoas', 'value': 'AL'},
{'label': 'Amapá', 'value': 'AP'},
{'label': 'Amazonas', 'value': 'AM'},
{'label': 'Bahia', 'value': 'BA'},
{'label': 'Ceará', 'value': 'CE'},
{'label': 'Distrito Federal ', 'value': 'DF'},
{'label': 'Espírito Santo', 'value': 'ES'},
{'label': 'Goiás', 'value': 'GO'},
{'label': 'Maranhão', 'value': 'MA'},
{'label': 'Mato Grosso', 'value': 'MT'},
{'label': 'Mato Grosso do Sul', 'value': 'MS'},
{'label': 'Minas Gerais', 'value': 'MG'},
{'label': 'Pará', 'value': 'PA'},
{'label': 'Paraíba', 'value': 'PB'},
{'label': 'Paraná', 'value': 'PR'},
{'label': 'Pernambuco', 'value': 'PE'},
{'label': 'Piauí', 'value': 'PI'},
{'label': 'Rio de Janeiro ', 'value': 'RJ'},
{'label': 'Rio Grande do Norte ', 'value': 'RN'},
{'label': 'Rio Grande do Sul', 'value': 'RS'},
{'label': 'Rondônia', 'value': 'RO'},
{'label': 'Roraima', 'value': 'RR'},
{'label': 'Santa Catarina', 'value': 'SC'},
{'label': 'São Paulo', 'value': 'SP'},
{'label': 'Sergipe', 'value': 'SE'},
{'label': 'Tocantins', 'value': 'TO'}]


mun = pd.read_csv('data/municipios.csv')
municipios = []

anos = []
for i in numpy.arange(2016, 1998, -2):
    anos.append({'label': i, 'value': i})

# layout principal
layout_pagina = [html.Div([
                           html.H1('Informações Gerais sobre as  Eleições'),
                           html.H3('Neste Dashboard, é possível fazer pesquisas descritivas sobre os cargos em todos os pleitos disponíveis na base de dados da CEPESP.', style={'font-style': 'italic'}),
                           html.Label('Cargo:', style={'display': 'inline'}),
                           dcc.Dropdown(id='lista-cargos', options=cargos),
                           html.Label('Ano:'),
                           dcc.Dropdown(id='lista-anos'),
                           html.Label('Estado:'),
                           dcc.Dropdown(id='lista-ufs', options=ufs),
                           html.Label('Município:'),
                           dcc.Dropdown(id='lista-municipios'),
                           html.Button('Pesquisar', id='botao-pesquisar'),
                           html.Button('Limpar', id='botao-limpar'),
                          ], id='head'),
                html.Div(id='cg-body')
               ]

layout = html.Div(layout_pagina, id='cg-content')

# criar anos
@app.callback(
    Output('lista-anos', 'options'),
    [Input('lista-cargos', 'value')])
def atualiza_ano(cargo):
    anos = []
    if cargo in [CARGO.PREFEITO, CARGO.VEREADOR]:
        for i in numpy.arange(2016, 1998, -4):
            anos.append({'label': i, 'value': i})
    else:
        for i in numpy.arange(2014, 1996, -4):
            anos.append({'label': i, 'value': i})
    return anos

# criar municipios
@app.callback(
    Output('lista-municipios', 'options'),
    [Input('lista-cargos', 'value'),
     Input('lista-anos', 'value'),
     Input('lista-ufs', 'value')])
def atualiza_municipios(cargo, ano, uf):
    if (uf is None):
        return []

    municipios = mun[(mun['CODIGO_CARGO'] == cargo) & (mun['ANO_ELEICAO'] == ano) & (mun['UF'] == uf)]['NOME_MUNICIPIO'].tolist()
    municipios.sort()

    return [{'label': m, 'value': m} for m in municipios]

# limpar pagina
@app.callback(Output('cg-content', 'children'),
              [Input('botao-limpar', 'n_clicks')])
def limpa_pesquisa(botao):
    return layout_pagina

# efetuar pesquisa
@app.callback(
    Output('cg-body', 'children'),
    [Input('botao-pesquisar', 'n_clicks')],
    [State('lista-cargos', 'value'),
    State('lista-anos', 'value'),
    State('lista-ufs', 'value'),
    State('lista-municipios', 'value')])
def atualiza_pesquisa(botao, cargo, ano, uf, municipio):
    if (cargo is None) or (ano is None):
        return None

    if (uf is None):
        regional = AGR_REGIONAL.BRASIL
        estado = ''
    else:
        estado = uf
        if (municipio is None):
            regional = AGR_REGIONAL.UF
        else:
            regional = AGR_REGIONAL.MUNICIPIO

    df = votos_x_candidatos(cargo=cargo, ano=ano, agregacao_politica=1, agregacao_regional=regional, estado=estado)

    if df.empty:
        return None

    if (municipio is None):
        pass
    else:
        df = df[df['NOME_MUNICIPIO'] == municipio.encode('utf-8')]

    # converte campos para formato numerico
    df['QTDE_VOTOS'] = pd.to_numeric(df['QTDE_VOTOS'], errors='coerce')
    df['DESPESA_MAX_CAMPANHA'] = pd.to_numeric(df['DESPESA_MAX_CAMPANHA'], errors='coerce')
    df['NUMERO_CANDIDATO'] = pd.to_numeric(df['NUMERO_CANDIDATO'], errors='coerce')

    # brancos e nulos
    b_n = df[(df['NUMERO_CANDIDATO'] == 95) | (df['NUMERO_CANDIDATO'] == 96)][['NUMERO_CANDIDATO', 'NUM_TURNO', 'QTDE_VOTOS']].groupby(['NUMERO_CANDIDATO', 'NUM_TURNO']).sum().reset_index()
    b_n['NOME_URNA_CANDIDATO'] = ''
    b_n['NOME_URNA_CANDIDATO'][b_n['NUMERO_CANDIDATO'] == 95] = 'BRANCOS'
    b_n['NOME_URNA_CANDIDATO'][b_n['NUMERO_CANDIDATO'] == 96] = 'NULOS'

    # soma repetidos, criando lista consistente, sem repeticoes
    df = df.groupby(['NUM_TURNO',
                     'NUMERO_CANDIDATO',
                     'NOME_URNA_CANDIDATO',
                     'SIGLA_PARTIDO',
                     'NOME_COLIGACAO',
                     'DESCRICAO_OCUPACAO',
                     'IDADE_DATA_ELEICAO',
                     'DESCRICAO_SEXO',
                     'DESCRICAO_GRAU_INSTRUCAO',
                     'DESCRICAO_ESTADO_CIVIL',
                     'SIGLA_UF_NASCIMENTO',
                     'NOME_MUNICIPIO_NASCIMENTO',
                     'SIGLA_UF',
                     'DESC_SIT_TOT_TURNO'], as_index=False).sum().reset_index(drop=True)
    df = pd.concat([b_n, df])
    del b_n

    # se ha mais de um eleito, deve apresentar layout_varios
    numero_eleitos = len(df[(df['DESC_SIT_TOT_TURNO'] == 'ELEITO') | (df['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') | (df['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')])

    if numero_eleitos == 1:
        return preenche_layout_um(df)
    else:
        return preenche_layout_varios(df)


def preenche_layout_um(df):
    # retira brancos e nulos
    df_candidatos = df[(df['NUMERO_CANDIDATO'] != 95) & (df['NUMERO_CANDIDATO'] != 96)]

    layout = []

    resultado = card_eleito(df_candidatos)
    if resultado:
        layout.append(html.Div(resultado, id='card-eleito', style=estilo['card-pessoas']))

    resultado = card_1_turno(df_candidatos)
    if resultado:
        layout.append(html.Div(resultado, id='card-1-turno', style=estilo['card-1-turno']))

    resultado = card_2_turno(df_candidatos)
    if resultado:
        layout.append(html.Div(resultado, id='card-2-turno', style=estilo['card-2-turno']))

    resultado = card_custos(df_candidatos)
    if resultado:
        layout.append(html.Div(resultado, id='card-custos', style=estilo['card-custos']))

    resultado = pizza_1_turno(df)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='pizza-1-turno'))

    resultado = pizza_2_turno(df)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='pizza-2-turno'))

    resultado = histograma_idade(df_candidatos)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='histograma-idade'))

    resultado = pizza_sexo(df_candidatos)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='pizza-sexo'))

    resultado = pizza_estado_civil(df_candidatos)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='pizza-estado-civil'))

    resultado = pizza_grau_instrucao(df_candidatos)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='pizza-grau-instrucao'))

    resultado = pizza_ocupacao(df_candidatos)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='pizza-ocupacao'))

    return layout

def preenche_layout_varios(df):
    ## tabela e graficos aqui comparam eleitos e nao eleitos

    nome_eleitos = df[(df['DESC_SIT_TOT_TURNO'] == 'ELEITO') | (df['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') | (df['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')]['NOME_URNA_CANDIDATO'].tolist()
    nome_nao_eleitos = df[(df['DESC_SIT_TOT_TURNO'] == 'NÃO ELEITO') | (df['DESC_SIT_TOT_TURNO'] == 'SUPLENTE')]['NOME_URNA_CANDIDATO'].tolist()

    eleitos = df[(df['NOME_URNA_CANDIDATO'].isin(nome_eleitos)) & (df['NUM_TURNO'] == '1')]
    nao_eleitos = df[(df['NOME_URNA_CANDIDATO'].isin(nome_nao_eleitos)) & (df['NUM_TURNO'] == '1')]

    # retira brancos e nulos
    candidatos = df[(df['NUMERO_CANDIDATO'] != 95) & (df['NUMERO_CANDIDATO'] != 96)]
    candidatos['ELEITO'] =  'Não'
    candidatos['ELEITO'][candidatos['NOME_URNA_CANDIDATO'].isin(nome_eleitos)] = 'Sim'

    layout = []

    # tabela candidatos (coluna eleitos)
    # resultado = tabela_candidatos(candidatos)
    # if resultado:
    #     layout.append(html.Div(resultado))

    # histograma-candidatos-custos
    resultado = histograma_candidatos_custos(eleitos, nao_eleitos)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='histograma-candidatos-custos'))

    # histograma-candidatos-votos
    resultado = histograma_candidatos_votos(eleitos, nao_eleitos)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='histograma-candidatos-votos'))

    # histograma-candidatos-idade
    resultado = histograma_candidatos_idade(eleitos, nao_eleitos)
    if resultado:
        layout.append(dcc.Graph(figure=resultado, id='histograma-candidatos-idade'))

    # pizza-candidatos-sexo
    resultado = pizza_candidatos_sexo(eleitos, nao_eleitos)
    if resultado:
        layout.append(html.Div(resultado))

    # pizza-candidatos-estado-civil
    resultado = pizza_candidatos_estado_civil(eleitos, nao_eleitos)
    if resultado:
        layout.append(html.Div(resultado))

    # pizza-candidatos-grau-instrucao
    resultado = pizza_candidatos_grau_instrucao(eleitos, nao_eleitos)
    if resultado:
        layout.append(html.Div(resultado))

    # pizza-candidatos-ocupacao
    resultado = pizza_candidatos_ocupacao(eleitos, nao_eleitos)
    if resultado:
        layout.append(html.Div(resultado))

    return layout

# def tabela_candidatos(candidatos):
#     df = candidatos[['SIGLA_UF', 'NOME_URNA_CANDIDATO', 'SIGLA_PARTIDO', 'ELEITO', 'QTDE_VOTOS']]
#     df.columns = ['Estado', 'Candidato', 'Partido', 'Eleito', 'Votos']
#     df = df.sort_values(by=['Estado', 'Eleito', 'Votos'], ascending=[True, False, False])
#
#     tabela = dt.DataTable(
#             rows=df.to_dict('records'),
#
#             # optional - sets the order of columns
#             columns=df.columns,
#
#             row_selectable=False,
#             filterable=True,
#             sortable=True,
#             selected_row_indices=[],
#             id='tabela-candidatos'
#         )
#
#     return tabela
    #
    # max_rows = 50
    # return html.Table(
    #     # Header
    #     [html.Tr([html.Th(col) for col in df.columns])] +
    #
    #     # cg-body
    #     [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(min(len(df), max_rows))]
    # )


def histograma_candidatos_custos(eleitos, nao_eleitos):
    e = [int(i) for i in eleitos['DESPESA_MAX_CAMPANHA'].values.tolist()]
    ne = [int(i) for i in nao_eleitos['DESPESA_MAX_CAMPANHA'].values.tolist()]

    return {
            'data': [go.Histogram(x=e, name='Eleitos', opacity=0.75),
                     go.Histogram(x=ne, name='Não Eleitos', opacity=0.75)],
            'layout': go.Layout(
                {'title': 'Custos dos Eleitos e Não Eleitos'},
                barmode='overlay',
                xaxis={
                    'title': 'Despesa (R$)',
                    'type': 'linear'
                },
                yaxis={
                    'title': 'Número de Candidatos',
                    'type': 'linear'
                }
            )
        }


def histograma_candidatos_votos(eleitos, nao_eleitos):
    e = [int(i) for i in eleitos['QTDE_VOTOS'].values.tolist()]
    ne = [int(i) for i in nao_eleitos['QTDE_VOTOS'].values.tolist()]

    return {
            'data': [go.Histogram(x=e, name='Eleitos', opacity=0.75),
                     go.Histogram(x=ne, name='Não Eleitos', opacity=0.75)],
            'layout': go.Layout(
                {'title': 'Votos dos Eleitos e Não Eleitos'},
                barmode='overlay',
                xaxis={
                    'title': 'Votos',
                    'type': 'linear'
                },
                yaxis={
                    'title': 'Número de candidatos',
                    'type': 'linear'
                }
            )
        }


def histograma_candidatos_idade(eleitos, nao_eleitos):
    e = [int(i) for i in eleitos['IDADE_DATA_ELEICAO'].values.tolist()]
    ne = [int(i) for i in nao_eleitos['IDADE_DATA_ELEICAO'].values.tolist()]

    return {
            'data': [go.Histogram(x=e, name='Eleitos', opacity=0.75),
                     go.Histogram(x=ne, name='Não Eleitos', opacity=0.75)],
            'layout': go.Layout(
                {'title': 'Idade dos Eleitos e Não Eleitos'},
                barmode='overlay',
                xaxis={
                    'title': 'Idade',
                    'type': 'linear'
                },
                yaxis={
                    'title': 'Número de candidatos',
                    'type': 'linear'
                }
            )
        }


def pizza_candidatos_sexo(eleitos, nao_eleitos):
    ge = eleitos.groupby('DESCRICAO_SEXO').size().reset_index(name='QUANTIDADE')
    gne = nao_eleitos.groupby('DESCRICAO_SEXO').size().reset_index(name='QUANTIDADE')

    return [dcc.Graph(id='pizza-eleitos-sexo', figure={
            'data': [go.Pie(labels=ge['DESCRICAO_SEXO'].values.tolist(), values=ge['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Eleitos', 'x': 0.50, 'y': 0.5}]}
            )
        }), dcc.Graph(id='pizza-nao-eleitos-sexo', figure={
                'data': [go.Pie(labels=gne['DESCRICAO_SEXO'].values.tolist(), values=gne['QUANTIDADE'].values.tolist(), hole=0.5)],
                'layout': go.Layout(
                    {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Não Eleitos', 'x': 0.50, 'y': 0.5}]}
                )
            })]



def pizza_candidatos_estado_civil(eleitos, nao_eleitos):
    ge = eleitos.groupby('DESCRICAO_ESTADO_CIVIL').size().reset_index(name='QUANTIDADE')
    gne = nao_eleitos.groupby('DESCRICAO_ESTADO_CIVIL').size().reset_index(name='QUANTIDADE')

    return [dcc.Graph(id='pizza-eleitos-estado-civil', figure={
            'data': [go.Pie(labels=ge['DESCRICAO_ESTADO_CIVIL'].values.tolist(), values=ge['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Eleitos', 'x': 0.50, 'y': 0.5}]}
            )
        }), dcc.Graph(id='pizza-nao-eleitos-civil', figure={
                'data': [go.Pie(labels=gne['DESCRICAO_ESTADO_CIVIL'].values.tolist(), values=gne['QUANTIDADE'].values.tolist(), hole=0.5)],
                'layout': go.Layout(
                    {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Não Eleitos', 'x': 0.50, 'y': 0.5}]}
                )
            })]



def pizza_candidatos_grau_instrucao(eleitos, nao_eleitos):
    ge = eleitos.groupby('DESCRICAO_GRAU_INSTRUCAO').size().reset_index(name='QUANTIDADE')
    gne = nao_eleitos.groupby('DESCRICAO_GRAU_INSTRUCAO').size().reset_index(name='QUANTIDADE')

    return [dcc.Graph(id='pizza-eleitos-grau-instrucao', figure={
            'data': [go.Pie(labels=ge['DESCRICAO_GRAU_INSTRUCAO'].values.tolist(), values=ge['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Eleitos', 'x': 0.50, 'y': 0.5}]}
            )
        }), dcc.Graph(id='pizza-nao-eleitos-grau-instrucao', figure={
                'data': [go.Pie(labels=gne['DESCRICAO_GRAU_INSTRUCAO'].values.tolist(), values=gne['QUANTIDADE'].values.tolist(), hole=0.5)],
                'layout': go.Layout(
                    {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Não Eleitos', 'x': 0.50, 'y': 0.5}]}
                )
            })]



def pizza_candidatos_ocupacao(eleitos, nao_eleitos):
    ge = eleitos.groupby('DESCRICAO_OCUPACAO').size().reset_index(name='QUANTIDADE')
    gne = nao_eleitos.groupby('DESCRICAO_OCUPACAO').size().reset_index(name='QUANTIDADE')

    return [dcc.Graph(id='pizza-eleitos-ocupacao', figure={
            'data': [go.Pie(labels=ge['DESCRICAO_OCUPACAO'].values.tolist(), values=ge['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Eleitos', 'x': 0.50, 'y': 0.5}]}
            )
        }), dcc.Graph(id='pizza-nao-eleitos-ocupacao', figure={
                'data': [go.Pie(labels=gne['DESCRICAO_OCUPACAO'].values.tolist(), values=gne['QUANTIDADE'].values.tolist(), hole=0.5)],
                'layout': go.Layout(
                    {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Não Eleitos', 'x': 0.50, 'y': 0.5}]}
                )
            })]



def card_eleito(df):
    eleito = df[df['DESC_SIT_TOT_TURNO'] == 'ELEITO']
    nome = eleito['NOME_URNA_CANDIDATO']
    partido = eleito['SIGLA_PARTIDO']
    coligacao = eleito['NOME_COLIGACAO']
    idade = eleito['IDADE_DATA_ELEICAO'] + " anos"
    natural = "Natural de " + eleito['NOME_MUNICIPIO_NASCIMENTO'] + " (" + eleito['SIGLA_UF_NASCIMENTO'] + ")"

    return [html.H2(nome + " (" + partido + ")"),
            html.H3(coligacao),
            html.P(idade),
            html.P(natural)]

def card_1_turno(df):
    nome = df[df['DESC_SIT_TOT_TURNO'] == 'ELEITO']['NOME_URNA_CANDIDATO'].iloc[0]
    v = "{0:n}".format(df['QTDE_VOTOS'][(df['NUM_TURNO'] == '1') & (df['NOME_URNA_CANDIDATO'] == nome)].iloc[0])

    return [html.H2(v),
            html.H3('votos no 1ª Turno')]

def card_2_turno(df):
    turno = df[df['DESC_SIT_TOT_TURNO'] == 'ELEITO']['NUM_TURNO'].iloc[0]
    if turno == '1':
        return None

    v = "{0:n}".format(df['QTDE_VOTOS'][(df['DESC_SIT_TOT_TURNO'] == 'ELEITO')].iloc[0])
    return [html.H2(v),
            html.H3('votos no 2ª Turno')]

def card_custos(df):
    nome = df[df['DESC_SIT_TOT_TURNO'] == 'ELEITO']['NOME_URNA_CANDIDATO'].iloc[0]
    df2 = df.groupby('NOME_URNA_CANDIDATO').sum().reset_index()
    v = locale.currency( df2['DESPESA_MAX_CAMPANHA'][(df2['NOME_URNA_CANDIDATO'] == nome)].iloc[0] / float(100), grouping=True )

    if v <= 0:
        return None

    return [html.H2(v),
            html.H3('para a Campanha')]

def pizza_1_turno(df):
    nomes = df[df['NUM_TURNO'] == '1']['NOME_URNA_CANDIDATO'].values.tolist()
    votos = df[df['NUM_TURNO'] == '1']['QTDE_VOTOS'].values.tolist()

    return {
            'data': [go.Pie(labels=nomes, values=votos, hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': '1º Turno', 'x': 0.50, 'y': 0.5}]}
            )
        }

def pizza_2_turno(df):
    nomes = df[df['NUM_TURNO'] == '2']['NOME_URNA_CANDIDATO'].values.tolist()

    if not nomes:
        return None

    votos = df[df['NUM_TURNO'] == '2']['QTDE_VOTOS'].values.tolist()

    return {
            'data': [go.Pie(labels=nomes, values=votos, hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': '2º Turno', 'x': 0.50, 'y': 0.5}]}
            )
        }

def histograma_idade(df):
    idades = [int(i) for i in df['IDADE_DATA_ELEICAO'][df['NUM_TURNO'] == '1'].values.tolist()]

    if not idades:
        return None

    return {
            'data': [go.Histogram(x=idades)],
            'layout': go.Layout(
                {'title': 'Distribuição por Idade'},
                xaxis={
                    'title': 'idade',
                    'type': 'linear'
                },
                yaxis={
                    'title': 'quantidade',
                    'type': 'linear'
                }
            )
        }

def pizza_sexo(df):
    grupo = df[df['NUM_TURNO'] == '1'].groupby('DESCRICAO_SEXO').size().reset_index(name='QUANTIDADE')

    return {
            'data': [go.Pie(labels=grupo['DESCRICAO_SEXO'].values.tolist(), values=grupo['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Sexo', 'x': 0.50, 'y': 0.5}]}
            )
        }

def pizza_estado_civil(df):
    grupo = df[df['NUM_TURNO'] == '1'].groupby('DESCRICAO_ESTADO_CIVIL').size().reset_index(name='QUANTIDADE')

    return {
            'data': [go.Pie(labels=grupo['DESCRICAO_ESTADO_CIVIL'].values.tolist(), values=grupo['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Estado Civil', 'x': 0.50, 'y': 0.5}]}
            )
        }

def pizza_grau_instrucao(df):
    grupo = df[df['NUM_TURNO'] == '1'].groupby('DESCRICAO_GRAU_INSTRUCAO').size().reset_index(name='QUANTIDADE')

    return {
            'data': [go.Pie(labels=grupo['DESCRICAO_GRAU_INSTRUCAO'].values.tolist(), values=grupo['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Instrução', 'x': 0.50, 'y': 0.5}]}
            )
        }

def pizza_ocupacao(df):
    grupo = df[df['NUM_TURNO'] == '1'].groupby('DESCRICAO_OCUPACAO').size().reset_index(name='QUANTIDADE')

    return {
            'data': [go.Pie(labels=grupo['DESCRICAO_OCUPACAO'].values.tolist(), values=grupo['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Ocupação', 'x': 0.50, 'y': 0.5}]}
            )
        }
