# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from cepesp import *
import numpy as np
import pandas as pd
import css
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
centis = pd.read_csv('data/centis_deputados_federais_2014.csv')

## recuperar deputados federais com votos mais expressivos
# contar eleitos por uf, multiplicando por 5
por_uf = centis[(centis['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') | (centis['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')].groupby('SIGLA_UE').size().reset_index(name='QTDE_ELEITOS')
por_uf['TAMANHO'] = por_uf['QTDE_ELEITOS'] * 5

# ordenar por uf e quantidade de votos
centis = centis.sort_values(by=['SIGLA_UE', 'QTDE_VOTOS'], ascending=[True, False])

# selecionar grupo
expressivos = pd.DataFrame()
for i, u in por_uf.iterrows():
    expressivos = pd.concat([expressivos, centis[centis['SIGLA_UE'] == u['SIGLA_UE']].head(u['TAMANHO'])])


layout = html.Div([
               html.Div([
                         dcc.Dropdown(options=ufs, id='perfil-combo-ufs'),
                         dcc.Dropdown(options=[], id='perfil-combo-candidatos')
                       ], id='head'),
               html.Div(id='pf-body')
              ])

@app.callback(Output('perfil-combo-candidatos', 'value'),
              [Input('perfil-combo-ufs', 'value')])
def limpa_combo_candidatos(uf):
    return []

@app.callback(Output('perfil-combo-candidatos', 'options'),
              [Input('perfil-combo-ufs', 'value')])
def preenche_combo_candidatos(uf):
    candidatos = centis[centis['SIGLA_UE'] == uf].sort_values(by='NOME_URNA_CANDIDATO')
    return [{'label': c['NOME_URNA_CANDIDATO'], 'value': c['CPF_CANDIDATO']} for i, c in candidatos.iterrows()]

@app.callback(Output('pf-body', 'children'),
              [Input('perfil-combo-candidatos', 'value')])
def preenche_perfil(cpf):
    leiaute = []

    if not cpf:
        return leiaute

    candidato = centis[centis['CPF_CANDIDATO'] == cpf]

    resultado = card_candidato_perfil(candidato)
    if resultado:
        leiaute.append(resultado)

    resultado = card_resumo_perfil(candidato)
    if resultado:
        leiaute.append(resultado)

    resultado = card_menos_votado_perfil(candidato)
    if resultado:
        leiaute.append(resultado)

    resultado = card_mais_votado_perfil(candidato)
    if resultado:
        leiaute.append(resultado)

    resultado = pizza_eleitos_perfil(candidato)
    if resultado:
        leiaute.append(resultado)

    resultado = barra_resultado_perfil(candidato)
    if resultado:
        leiaute.append(resultado)

    resultado = tabela_similares_perfil(candidato)
    if resultado:
        leiaute.append(resultado)

    return leiaute


def card_candidato_perfil(candidato):
    nome = candidato['NOME_URNA_CANDIDATO']
    partido = candidato['SIGLA_PARTIDO']
    coligacao = candidato['NOME_COLIGACAO']
    idade = str(candidato['IDADE_DATA_ELEICAO'].iloc[0]) + " anos"
    natural = "Natural de " + candidato['NOME_MUNICIPIO_NASCIMENTO'] + " (" + candidato['SIGLA_UF_NASCIMENTO'] + ")"
    profissao = candidato['DESCRICAO_OCUPACAO']
    eleito = candidato['DESC_SIT_TOT_TURNO']
    return html.Div([html.H2(nome + " (" + partido + ")"),
                     html.H3(coligacao),
                     html.P(idade),
                     html.P(natural),
                     html.P(profissao),
                     html.P(eleito)])


def card_resumo_perfil(candidato):
    return


def card_menos_votado_perfil(candidato):
    return


def card_mais_votado_perfil(candidato):
    return


def pizza_eleitos_perfil(candidato):
    return


def barra_resultado_perfil(candidato):
    return


def tabela_similares_perfil(candidato):
#   identificar candidatos com votacao expressiva que sao similares ao candidato selecionado
    centil = candidato['CENTIL'].iloc[0]
    similares = expressivos[expressivos['CPF_CANDIDATO'] != cpf]
    similares['DIFERENCA'] = abs(similares['CENTIL'] - centil)
    similares = similares.sort_values(by='DIFERENCA').head(6)
    similares = similares.sort_values(by='QTDE_VOTOS', ascending=False).reset_index(drop=True)

    dados_similares = [html.Tr([html.Th('Nome', style=css.tabela['td']),
                                html.Th('Partido', style=css.tabela['td']),
                                html.Th('Estado', style=css.tabela['td']),
                                html.Th('Quantidade de Votos', style=css.tabela['td']),
                                html.Th('Último Resultado', style=css.tabela['td'])])]
    for i, s in similares.iterrows():
        if i % 2 == 0:
            cor = 'escuro'
        else:
            cor = 'claro'
        dados_similares += [html.Tr([html.Td(s['NOME_URNA_CANDIDATO'], style=css.tabela['td']),
                                     html.Td(s['SIGLA_PARTIDO'], style=css.tabela['td']),
                                     html.Td(s['DESCRICAO_UE'], style=css.tabela['td']),
                                     html.Td(s['QTDE_VOTOS'], style=css.tabela['td-num']),
                                     html.Td(s['DESC_SIT_TOT_TURNO'], style=css.tabela['td'])], style=css.tabela[cor])]

    return html.Table(dados_similares, style=css.tabela['table'])
