# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import css

from app import app

print('entrou capital eleitoral')

# razao entre a populacao brasileira em 2018 e 2014
projecao = 1.0205680705

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

# recuperar arquivo com dados dos deputados estaduais de 2010
ce_14 = pd.read_csv('data/capital_eleitoral_2014.csv')

# recuperar arquivo com dados dos deputados estaduais de 2014
ce_18 = pd.read_csv('data/capital_eleitoral_2018.csv')

# recuperar deputados federais de 2014
df_14 = pd.read_csv('data/centis_deputados_federais_2014.csv')

# recuperar informacoes sobre federais em 2014
qe_uf = pd.read_csv('data/qe_federal_2014.csv')

layout = html.Div([
               html.H1('Será que é hora de virar Federal?'),
               html.H3('Fizemos uma projeção da quantidade de votos que um candidato a Deputado Estadual conseguiria se resolvesse se candidatar a Deputado Federal.', style={'font-style': 'italic'}),
               html.Div([html.Div([html.P('Estado: ', style={'width' : '15%'}),
                         html.Div(dcc.Dropdown(options=ufs, id='capital-combo-ufs'), style={'width': '40%'})], style={'display': 'flex', 'align-items': 'center'}),

                         html.Div([html.P('Candidato: ', style={'width' : '15%'}),
                         html.Div(dcc.Dropdown(options=[], id='capital-combo-candidatos'), style={'width': '40%'})], style={'display' : 'flex', 'align-items': 'center'})
                       ], id='head'),
               html.Div(id='ce-body')
              ])


@app.callback(Output('capital-combo-candidatos', 'value'),
              [Input('capital-combo-ufs', 'value')])
def limpa_combo_candidatos(uf):
    return []


@app.callback(Output('capital-combo-candidatos', 'options'),
              [Input('capital-combo-ufs', 'value')])
def preenche_combo_candidatos(uf):
    candidatos = ce_18[ce_18['SIGLA_UF'] == uf].sort_values(by='NOME_URNA_CANDIDATO')
    return [{'label': c['NOME_URNA_CANDIDATO'], 'value': c['CPF_CANDIDATO']} for i, c in candidatos.iterrows()]


@app.callback(Output('ce-body', 'children'),
              [Input('capital-combo-candidatos', 'value')])
def preenche_capital_eleitoral(cpf):
    leiaute = []

    if not cpf:
        return leiaute

    candidato = ce_18[ce_18['CPF_CANDIDATO'] == cpf]

    return [card_candidato_capital(candidato), pizza_sucesso_capital(candidato['SIGLA_UF'].iloc[0])]


def card_candidato_capital(candidato):
    uf = candidato['SIGLA_UF'].iloc[0]

    # calculara projecao da evolucao para federal
    qe = qe_uf['QUOCIENTE_ELEITORAL'][qe_uf['SIGLA_UF'] == uf].iloc[0]
    projecao_candidato = int(qe * candidato['TARGET'] * projecao)

    card_candidato = card_menos = html.Div([html.H2('Projeção de Votos em 2018 como Federal: ' + str(projecao_candidato))
                                            ], style={'background-color' : '#3971b3',
                                                      'color' : 'white'})


    # dados sobre deputados federais eleitos em 2014
    eleitos = df_14[(df_14['SIGLA_UE'] == uf) & ((df_14['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') |
                    (df_14['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')) ]
    eleitos = eleitos.sort_values(by='QTDE_VOTOS').reset_index(drop=True)

    # identificar deputado federal menos votado
    menos = eleitos.head(1)

    card_menos = html.Div([html.H2('Federal Menos Votado em 2014'),
                           html.H3(menos['NOME_URNA_CANDIDATO'].iloc[0]),
                           html.H3(menos['DESC_SIT_TOT_TURNO'].iloc[0] + ' (' + str(int(menos['QTDE_VOTOS'].iloc[0])) + ' votos)')
                           ], style={'float' : 'left',
                                     'background-color' : '#d0342e',
                                     'color' : 'white',
                                     'height' : '150px',
                                     'width' : '45%'})


    # identificar deputado federal mais votado
    mais = eleitos.tail(1)

    card_mais  = html.Div([html.H2('Federal Mais Votado em 2014'),
                           html.H3(mais['NOME_URNA_CANDIDATO'].iloc[0]),
                           html.H3(mais['DESC_SIT_TOT_TURNO'].iloc[0] + ' (' + str(int(mais['QTDE_VOTOS'].iloc[0])) + ' votos)')
                           ], style={'float' : 'right',
                                     'background-color' : '#2e9d2d',
                                     'color' : 'white',
                                     'height' : '150px',
                                     'width' : '45%'})

    card_outros = html.Div([card_menos, card_mais], style={'height' : '150px'})

    return html.Div([html.Br(), card_candidato, card_outros])


def pizza_sucesso_capital(uf):
    resultados = ce_14[ce_14['SIGLA_UF'] == uf]

    grupo = resultados.groupby('RESULTADO_FEDERAL').size().reset_index(name='QUANTIDADE')

    return dcc.Graph(figure={
            'data': [go.Pie(labels=grupo['RESULTADO_FEDERAL'].values.tolist(), values=grupo['QUANTIDADE'].values.tolist(), hole=0.5)],
            'layout': go.Layout(
                {'title': 'Taxa de Sucesso no Upgrade para Federal em 2010',
                 'annotations': [{'font': {'size': 20}, 'showarrow': False, 'text': 'Resultado', 'x': 0.50, 'y': 0.5}]}
            )
        }, id='pizza-sucesso-capital')
