# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from cepesp import *
import numpy as np
import pandas as pd
# import difflib as dl

from app import app

print('entrou perfil')

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

# recuperar arquivo com dados dos deputados
deputados = pd.read_csv('data/centis_deputados_federais_2014.csv')

layout = html.Div([
               html.Div([
                         dcc.Dropdown(options=ufs, id='combo-ufs'),
                         dcc.Dropdown(options=[], id='combo-candidatos')
                       ], id='head'),
               html.Div(id='pf-body')
              ])

@app.callback(Output('combo-candidatos', 'value'),
              [Input('combo-ufs', 'value')])
def limpa_combo_candidatos(uf):
    return []

@app.callback(Output('combo-candidatos', 'options'),
              [Input('combo-ufs', 'value')])
def preenche_combo_candidatos(uf):
    candidatos = deputados[deputados['SIGLA_UE'] == uf].sort_values(by='NOME_URNA_CANDIDATO')
    return [{'label': c['NOME_URNA_CANDIDATO'], 'value': c['CPF_CANDIDATO']} for i, c in candidatos.iterrows()]

@app.callback(Output('pf-body', 'children'),
              [Input('combo-candidatos', 'value')])
def preenche_perfil(cpf):
    if not cpf:
        return []

    candidato = deputados[deputados['CPF_CANDIDATO'] == cpf]
    nome = candidato['NOME_URNA_CANDIDATO']
    partido = candidato['SIGLA_PARTIDO']
    coligacao = candidato['NOME_COLIGACAO']
    idade = str(candidato['IDADE_DATA_ELEICAO'].iloc[0]) + " anos"
    natural = "Natural de " + candidato['NOME_MUNICIPIO_NASCIMENTO'] + " (" + candidato['SIGLA_UF_NASCIMENTO'] + ")"
    profissao = candidato['DESCRICAO_OCUPACAO']
    eleito = candidato['DESC_SIT_TOT_TURNO']
    dados_candidato =  html.Div([html.H2(nome + " (" + partido + ")"),
                        html.H3(coligacao),
                        html.P(idade),
                        html.P(natural),
                        html.P(profissao),
                        html.P(eleito)])

    centil = candidato['CENTIL'].iloc[0]
    similares = deputados.sort_values(by='CENTIL')
    similares = similares.reset_index(drop=True)
    pos = similares.index[similares['CENTIL'] == centil][0]

    indices = [i for i in range(pos-3, pos+4) if i >= 0 and i < len(deputados) ]
    indices.remove(pos)
    similares = similares.loc[indices]

    dados_similares = html.Table(
        # Header
        [html.Tr([html.Td('Nome'), html.Td('Partido'), html.Td('Estado')])] +

        # pf-body
        [html.Tr([html.Td(s['NOME_URNA_CANDIDATO']), html.Td(s['SIGLA_PARTIDO']), html.Td(s['DESCRICAO_UE'])]) for i, s in similares.iterrows()]
    )

    return html.Div([dados_candidato, dados_similares])
