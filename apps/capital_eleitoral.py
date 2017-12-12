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
ce_14 = pd.read_csv('data/capital_eleitoral_2018.csv')

# recuperar arquivo com dados dos deputados estaduais de 2014
ce_18 = pd.read_csv('data/capital_eleitoral_2018.csv')

# recuperar informacoes sobre federais em 2014
qe_uf = pd.read_csv('data/qe_federal_2014.csv')

layout = html.Div([
               html.Div([
                         dcc.Dropdown(options=ufs, id='capital-combo-ufs'),
                         dcc.Dropdown(options=[], id='capital-combo-candidatos')
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
              [Input('capital-combo-candidatos', 'value'),
               Input('capital-combo-ufs', 'value')])
def preenche_capital_eleitoral(nome, uf):
    leiaute = []

    if not nome:
        return leiaute

    candidato = ce_18[(ce_18['NOME_URNA_CANDIDATO'] == nome) & (ce_18['SIGLA_UF'] == uf)]

    resultado = card_candidato_capital(candidato)
    if resultado:
        leiaute.append(resultado)

    resultado = card_menos_votado_capital(uf)
    if resultado:
        leiaute.append(resultado)

    resultado = card_mais_votado_capital(uf)
    if resultado:
        leiaute.append(resultado)

    resultado = pizza_sucesso_capital(uf)
    if resultado:
        leiaute.append(resultado)

    return leiaute


def card_candidato_capital(candidato):
    return


def card_menos_votado_capital(candidato):
    return


def card_mais_votado_capital(candidato):
    return


def pizza_sucesso_capital(uf):
    return


    # qe = qe_uf['QUOCIENTE_ELEITORAL'][qe_uf['SIGLA_UF'] == uf].iloc[0]
    #
    # ce_18_uf = ce_18[ce_18['SIGLA_UF'] == uf]
    # ce_18_uf = ce_18_uf.sort_values(by='TARGET', ascending=False)
    # ce_18_uf = ce_18_uf.reset_index(drop=True)
    #
    # dados_ce_18_uf = [html.Tr([html.Th('Nome', style=css.tabela['td']),
    #                                html.Th('Votos Estadual (2014)', style=css.tabela['td']),
    #                                html.Th('Projeção Votos Federal (2018)', style=css.tabela['td'])])]
    # for i, s in ce_18_uf.iterrows():
    #     if i % 2 == 0:
    #         cor = 'escuro'
    #     else:
    #         cor = 'claro'
    #     dados_ce_18_uf += [html.Tr([html.Td(s['NOME_URNA_CANDIDATO'], style=css.tabela['td']),
    #                                     html.Td(s['VOTOS_ESTADUAL'], style=css.tabela['td-num']),
    #                                     html.Td(int(qe * s['TARGET'] * projecao), style=css.tabela['td-num'])], style=css.tabela[cor])]
    # dados_ce_18_uf = html.Table(dados_ce_18_uf, style=css.tabela['table'])
    #
    # return html.Div(dados_ce_18_uf)
