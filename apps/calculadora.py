# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from cepesp import *
import numpy as np
import pandas as pd
import datetime as dt
import css

from app import app

print('entrou calculadora')

# tempos totais em minutos
programa = 25
insercao = 70
partidos = []

# arquivo com deputados federais eleitos em 2014, agrupados por partido
todos = pd.read_csv('data/calculadora.csv')

partidos = [i[0] for i in todos[['SIGLA_PARTIDO']].astype(str).values.tolist()]

# montar partidos participantes da eleicao
partidos.sort()
checks = [{'label': p, 'value': p} for p in partidos]

layout = html.Div([
                html.H1('Tempo Disponível em Programas de Rádio e TV'),
                html.H3('No mundo dos negócios, Time is Money, mas na política, Tempo é Voto. Com quem coligar para maximizar o tempo de rádio e tv? Modelo inédito de calculadora totalmente baseado na lei 13.488/2017 que alterou a Lei das Eleições.', style={'font-style': 'italic'}),
                html.Div([
                            html.Div([
                                      html.H2('Quais partidos participarão desta eleição?'),
                                      dcc.Checklist(options=checks, values=partidos, id='participantes', style=css.checkbox),
                                      dcc.Checklist(options=[{'label': 'Todos', 'value': 'Todos'}], values=['Todos'], id='todos-participantes')
                                     ], style={'display' : 'flex', 'flex-direction' : 'column','height' : '150px'}),
                            html.Div([
                                      html.H2('Monte a coligação:'),
                                      dcc.Checklist(options=checks, values=[], id='coligacao', style=css.checkbox)
                                     ], style={'display' : 'flex', 'flex-direction' : 'column','height' : '150px'}),
                         ]),
               html.H2('Resultado:'),
               html.Div(id='resultado', style=css.div_centralizada)
              ])

# montar partidos da coligacao
@app.callback(
    dash.dependencies.Output('coligacao', 'options'),
    [dash.dependencies.Input('participantes', 'values')])
def atualiza_coligacao(participantes):
    participantes.sort()
    return [{'label': p, 'value': p} for p in participantes]


# controle marcar todos os participantes ou nao
@app.callback(
    dash.dependencies.Output('participantes', 'values'),
    [dash.dependencies.Input('todos-participantes', 'values')])
def todos_participantes(marcado):
    if marcado:
        return partidos
    else:
        return []


# efetuar calculo
@app.callback(
    dash.dependencies.Output('resultado', 'children'),
    [dash.dependencies.Input('participantes', 'values'),
     dash.dependencies.Input('coligacao', 'values')])
def efetua_calculo(participantes, coligacao):
    global todos, programa, insercao

    parts = ''
    for i in coligacao:
        parts += str(i) + ' / '
    parts = parts[:-3]

    tp_maj = calcula_tempo(todos, participantes, coligacao, programa, True)
    tp_min = calcula_tempo(todos, participantes, coligacao, programa)

    # tempos do programa por cargo
    tp_pres = np.trunc(tp_maj / float(2))
    tp_dep_f = np.trunc(tp_min / float(2))
    tp_sen = np.trunc(tp_maj * float(7 / float(programa)))
    tp_dep_e = np.trunc(tp_min * float(9 / float(programa)))
    tp_gov = np.trunc(tp_maj * float(9 / float(programa)))

    # tempo total do programa
    tp_ttl= tp_pres + tp_dep_f

    # tempo das insercoes
    ti = np.trunc(calcula_tempo(todos, participantes, coligacao, insercao))

    return html.Table([html.Tr([html.Th(html.Br()),
                                html.Th('Programa', colSpan=5, style=css.tabela['titulo']),
                                html.Th('Inserção', rowSpan=2, style=css.tabela['titulo'])]),
                       html.Tr([html.Td(),
                               html.Td('Presidente', style=css.tabela['titulo']),
                               html.Td('Governador', style=css.tabela['titulo']),
                               html.Td('Senador', style=css.tabela['titulo']),
                               html.Td([html.Span('Deputado'), html.Br(), html.Span('Federal')], style=css.tabela['titulo']),
                               html.Td([html.Span('Deputado'), html.Br(), html.Span('Estadual')], style=css.tabela['titulo'])]),
                       html.Tr([html.Td('1º Turno', style=css.tabela['titulo']),
                               html.Td(str(dt.timedelta(seconds=(tp_pres))), style=css.tabela['td-num']),
                               html.Td(str(dt.timedelta(seconds=(tp_gov))), style=css.tabela['td-num']),
                               html.Td(str(dt.timedelta(seconds=(tp_sen))), style=css.tabela['td-num']),
                               html.Td(str(dt.timedelta(seconds=(tp_dep_f))), style=css.tabela['td-num']),
                               html.Td(str(dt.timedelta(seconds=(tp_dep_e))), style=css.tabela['td-num']),
                               html.Td(str(dt.timedelta(seconds=(ti))), style=css.tabela['td-num'])]),
                       html.Tr([html.Td('2º Turno', style=css.tabela['titulo']),
                               html.Td('0:10:00', style=css.tabela['td-num']),
                               html.Td('0:10:00', style=css.tabela['td-num']),
                               html.Td('-', style=css.tabela['td-num']),
                               html.Td('-', style=css.tabela['td-num']),
                               html.Td('-', style=css.tabela['td-num']),
                               html.Td('-', style=css.tabela['td-num'])]),
                       html.Tr([html.Td('Máximo', style=css.tabela['titulo']),
                               html.Td('0:12:30', style=css.tabela['titulo']),
                               html.Td('0:09:00', style=css.tabela['titulo']),
                               html.Td('0:07:00', style=css.tabela['titulo']),
                               html.Td('0:12:30', style=css.tabela['titulo']),
                               html.Td('0:09:00', style=css.tabela['titulo']),
                               html.Td('1:10:00', style=css.tabela['titulo'])])], style=css.tabela['table'])


def calcula_tempo(todos, participantes, coligacao, tempo_disponivel, majoritaria=False):
    if not participantes:
        return 0

    # calcula os 10%
    p10 = 60 * tempo_disponivel * .1 / float(len(participantes))

    # recupera quantidade de deputados federais de cada partido que vai participar das eleicoes
    df_part = pd.merge(todos, pd.DataFrame({'SIGLA_PARTIDO': participantes}), on='SIGLA_PARTIDO').reset_index(drop=True)

    # calcula o total de deputados eleitos dos participantes
    deputados_eleitos = df_part['QUANTIDADE'].sum()

    # calcula o tempo proporcional por quantidade de deputados
    s = []
    q = []
    t = []
    for i, p in df_part.iterrows():
        s.append(p['SIGLA_PARTIDO'])
        q.append(p['QUANTIDADE'])
        if deputados_eleitos == 0:
            t.append(0)
        else:
            t.append(60 * tempo_disponivel * .9 * p['QUANTIDADE'] / float(deputados_eleitos))
    df_p90 = pd.DataFrame({'SIGLA_PARTIDO': s, 'QUANTIDADE': q, 'TEMPO': t})

    # filtra df_p90 para constar somente partidos da coligacao.
    # em caso de eleicao majoritaria, somente os seis primeiros partidos devem ser levados em conta.
    df_p90 = pd.merge(df_p90, pd.DataFrame({'SIGLA_PARTIDO': coligacao}), on='SIGLA_PARTIDO').reset_index(drop=True)
    df_p90 = df_p90.sort_values('QUANTIDADE', ascending=False)

    if majoritaria:
        df_p90 = df_p90.head(6)

    # soma os tempos de acordo com a coligacao
    p90 = np.sum(df_p90['TEMPO'].tolist())

    return p90 + p10 * len(coligacao)
