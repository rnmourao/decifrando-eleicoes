# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from cepesp import *
import numpy as np
import datetime as dt

from app import app

print('entrou calculadora')

# tempos totais em minutos
programa = 25
insercao = 70
partidos = []

# recuperar eleitos para deputado federal 2014
raw = votos_x_candidatos(cargo=CARGO.DEPUTADO_FEDERAL, ano=2014, agregacao_politica=AGR_POLITICA.CANDIDATO, agregacao_regional=AGR_REGIONAL.BRASIL)

# recuperar todos os partidos
todos_partidos = pd.DataFrame({'SIGLA_PARTIDO': list(set(raw[['SIGLA_PARTIDO']]['SIGLA_PARTIDO'].tolist()))})
todos_partidos = todos_partidos.dropna().reset_index(drop=True)

# agrupar eleitos por partido
raw = raw[['DESC_SIT_TOT_TURNO', 'SIGLA_PARTIDO']]
raw = raw[(raw['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') | (raw['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')]

raw = raw.groupby('SIGLA_PARTIDO').size().reset_index(name='QUANTIDADE')

# acrescentar partidos novos
todos = pd.merge(raw, todos_partidos, on='SIGLA_PARTIDO', how='right')
todos['QUANTIDADE'][pd.isnull(todos['QUANTIDADE'])] = 0

# conforme consulta ao site http://www.tse.jus.br/partidos/partidos-politicos/registrados-no-tse, constatou-se a existencia de tres partidos politicos registrados apos a eleicao de 2014, incluidos manualmente para fins de manuseio da calculadora.
todos = pd.concat([todos, pd.DataFrame({'SIGLA_PARTIDO': ['NOVO', 'REDE', 'PMB'], 'QUANTIDADE': [0, 0 , 0]})]).reset_index(drop=True)


# atualizar nome dos partidos que mudaram de nome
todos['SIGLA_PARTIDO'][todos['SIGLA_PARTIDO'] == 'PTN'] = 'PODE'
todos['SIGLA_PARTIDO'][todos['SIGLA_PARTIDO'] == 'PEN'] = 'PATRIOTA'
todos['SIGLA_PARTIDO'][todos['SIGLA_PARTIDO'] == 'PT do B'] = 'AVANTE'

partidos = [i[0] for i in todos[['SIGLA_PARTIDO']].astype(str).values.tolist()]

# montar partidos participantes da eleicao
partidos.sort()
checks = [{'label': p, 'value': p} for p in partidos]

layout = html.Div([
                html.Div(id='resultado', style={'display': 'block'}),
                html.Div([
                            html.Div([
                                      html.H2('Quais partidos participarão desta eleição?'),
                                      dcc.Checklist(options=checks, values=partidos,
                                                    labelStyle={'display': 'inline-block'}, id='participantes'),
                                      dcc.Checklist(options=[{'label': 'Todos', 'value': 'Todos'}], values=['Todos'], id='todos-participantes')
                                     ], style={'flex': '0 0 50%'}),
                            html.Div([
                                      html.H2('Monte a coligação:'),
                                      dcc.Checklist(options=checks, values=[],
                                                    labelStyle={'display': 'inline-block'}, id='coligacao')
                                     ], style={'flex': '1'}),
                         ], style={'display': 'flex'})
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

    return [html.H1('Tempo Disponível em Programas de Rádio e TV'),
            html.H2('Coligação ' + parts),
            html.P(),
            html.H2('1º Turno:'),
            html.P(),
            html.H2('Tempo Total de Programa por dia: ' + str(dt.timedelta(seconds=(tp_ttl)))),
            html.H3('Tempo para Presidente:' + str(dt.timedelta(seconds=(tp_pres)))),
            html.H3('Tempo para Governador:' + str(dt.timedelta(seconds=(tp_gov)))),
            html.H3('Tempo para Senador (2/3):' + str(dt.timedelta(seconds=(tp_sen)))),
            html.H3('Tempo para Deputado Federal:' + str(dt.timedelta(seconds=(tp_dep_f)))),
            html.H3('Tempo para Deputado Estadual:' + str(dt.timedelta(seconds=(tp_dep_e)))),
            html.P(),
            html.H2('Para o 2º Turno, Presidente e Governador terão 10 minutos por dia.'),
            html.P(),
            html.H2('Tempo Total de Inserções por dia: ' + str(dt.timedelta(seconds=(ti))))]


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
