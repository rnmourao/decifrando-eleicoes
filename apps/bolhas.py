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

from app import app

print('entrou bolhas')

PARADO = 60 * 60 * 1000
TEMPO = 2 * 1000
MENOR_ANO = 1998
MAIOR_ANO = 2016

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

visao = [
{'label': 'Estado', 'value': 'Estado'},
{'label': 'Partido', 'value': 'Partido'}
]

anos = [i for i in np.arange(1998, 2020, 2)]

# recuperar arquivo com votacoes
df = pd.read_csv('data/bolhas.csv')
df[['QTDE_VOTOS','QTDE_ELEITOS', 'QTDE_CANDIDATOS']] = df[['QTDE_VOTOS','QTDE_ELEITOS', 'QTDE_CANDIDATOS']].apply(pd.to_numeric)

# criar lista de partidos
ps = [p for p in df['SIGLA_PARTIDO'].unique()]
ps.sort()
partidos = [{'label': p, 'value': p} for p in ps]

layout = html.Div([
               html.H1('Como está a eficiência dos partidos?'),
               html.H3('Quais partidos elegem mais tendo menos candidatos? Será que a eficiência de um partido é igual em todos os estados?', style={'font-style': 'italic'}),
               html.Div([
                         html.Div([
                                     html.Div([html.P('Visão: '),
                                               dcc.RadioItems(options=visao, value='Estado', id='visao')],
                                              style={'display': 'flex',
                                                     'align-items': 'center'}),
                                     html.Div(dcc.Checklist(options=ufs, values=['SP'], id='check-visao',
                                                            style=css.checkbox),
                                              style={'display' : 'flex', 'align-items': 'center'})]),

                         html.Div([html.P('Cargo:'), dcc.Checklist(options=cargos, values=[CARGO.DEPUTADO_FEDERAL],
                                  id='cargos',)], style={'display' : 'flex', 'align-items': 'center'})
                       ], id='head', style={'display' : 'flex', 'flex-direction' : 'column'}),
               html.Div([
                         dcc.Graph(id='bolhas', style={'height' : '300px'}),
                         html.Div([
                                     html.Div([
                                               html.Button('>', id='play'),
                                               html.Button('II', id='pause', hidden=True)
                                              ], style={'display' : 'flex', 'align-items' : 'center', 'width' : '5%'}),
                                     html.Div(
                                              dcc.Slider(min=np.min(anos),
                                                         max=np.max(anos),
                                                         marks={str(i): str(i) for i in anos},
                                                         value=MENOR_ANO,
                                                         id='passador'), style={'display': 'flex', 'width': '80%'})], style={'display' : 'flex'})
                        ], id='body', style={'display' : 'flex', 'height' : '350px', 'flex-direction' : 'column', 'justify-content': 'space-between'}),
                        # , style={'width': '80%', 'position': 'fixed', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)'}
               dcc.Interval(id='intervalo', interval=PARADO)
              ])

@app.callback(Output('check-visao', 'values'),
              [Input('visao', 'value')])
def limpa_valores(visao):
    if visao == 'Estado':
        return ['SP']
    else:
        return ['PMDB']

@app.callback(Output('check-visao', 'options'),
              [Input('visao', 'value')])
def atualiza_opcoes(visao):
    if visao == 'Estado':
        return ufs
    else:
        return partidos

@app.callback(Output('bolhas', 'figure'),
              [Input('passador', 'value'),
               Input('visao', 'value'),
               Input('cargos', 'values'),
               Input('check-visao', 'values')])
def atualiza_pelo_passador(ano, visao, cargos, opcoes):
    if visao == 'Estado':
        return grafico_por_estado(ano, cargos, opcoes)
    else:
        return grafico_por_partido(ano, cargos, opcoes)


def grafico_por_estado(ano, cargos, ufs):
    # filtrar registros por ano, cargos e ufs
    mini = df[(df['ANO_ELEICAO'] == ano) & (df['CODIGO_CARGO'].isin(cargos)) & (df['UF'].isin(ufs))]
    mini_cargo = mini.groupby(['SIGLA_PARTIDO', 'CODIGO_CARGO'], as_index=False).agg({'QTDE_VOTOS': np.sum, 'QTDE_ELEITOS': np.sum, 'QTDE_CANDIDATOS': np.sum})
    mini_cargo = mini_cargo.fillna(0)

    # ajuste para presidente
    mini_cargo['QTDE_ELEITOS'][(mini_cargo['CODIGO_CARGO'] == 1) & (mini_cargo['QTDE_ELEITOS'] > 0)] = 1

    mini_cargo = mini_cargo.groupby(['SIGLA_PARTIDO'], as_index=False).agg({'QTDE_VOTOS': np.sum, 'QTDE_ELEITOS': np.sum, 'QTDE_CANDIDATOS': np.sum})

    # totais para normalizacao
    total_votos = mini_cargo['QTDE_VOTOS'].sum()
    total_eleitos = mini_cargo['QTDE_ELEITOS'].sum()
    total_candidatos = mini_cargo['QTDE_CANDIDATOS'].sum()

    # montar dados para cada partido
    tracos = []
    for p in mini_cargo['SIGLA_PARTIDO'].unique():
        mini_partido = mini_cargo[mini_cargo['SIGLA_PARTIDO'] == p]

        perc_votos = 100 * mini_partido['QTDE_VOTOS'] / float(total_votos)
        perc_eleitos = 100 * mini_partido['QTDE_ELEITOS'] / float(total_eleitos)
        perc_candidatos = 100 * mini_partido['QTDE_CANDIDATOS'] / float(total_candidatos)

        tracos.append(go.Scatter(
            x=perc_candidatos,
            y=perc_eleitos,
            text=str(mini_partido['QTDE_VOTOS'].values[0]) + " votos" + '<br>' +
                 str(mini_partido['QTDE_CANDIDATOS'].values[0]) + " candidatos" + '<br>' +
                 str(int(mini_partido['QTDE_ELEITOS'].values[0])) + " eleitos",
            mode='markers',
            opacity=0.7,
            marker={
                'size': perc_votos + 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=p
        ))
    return {
        'data': tracos,
        'layout': go.Layout(
            xaxis={'type': '-', 'title': 'Percentual de Candidatos', 'autorange': 'reversed'},
            yaxis={'title': 'Percentual de Eleitos', 'autorange': 'True'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            # legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


def grafico_por_partido(ano, cargos, partidos):
    # filtrar registros por ano, cargos e partidos
    mini = df[(df['ANO_ELEICAO'] == ano) & (df['CODIGO_CARGO'].isin(cargos)) & (df['SIGLA_PARTIDO'].isin(partidos))]
    mini_cargo = mini.groupby(['UF', 'CODIGO_CARGO'], as_index=False).agg({'QTDE_VOTOS': np.sum, 'QTDE_ELEITOS': np.sum, 'QTDE_CANDIDATOS': np.sum})
    mini_cargo = mini_cargo.fillna(0)

    # ajuste para presidente
    mini_cargo['QTDE_ELEITOS'][(mini_cargo['CODIGO_CARGO'] == 1) & (mini_cargo['QTDE_ELEITOS'] > 0)] = 1

    mini_cargo = mini_cargo.groupby(['UF'], as_index=False).agg({'QTDE_VOTOS': np.sum, 'QTDE_ELEITOS': np.sum, 'QTDE_CANDIDATOS': np.sum})

    # totais para normalizacao
    total_votos = mini_cargo['QTDE_VOTOS'].sum()
    total_eleitos = mini_cargo['QTDE_ELEITOS'].sum()
    total_candidatos = mini_cargo['QTDE_CANDIDATOS'].sum()

    # montar dados para cada partido
    tracos = []
    for uf in mini_cargo['UF'].unique():
        mini_uf = mini_cargo[mini_cargo['UF'] == uf]

        perc_votos = 100 * mini_uf['QTDE_VOTOS'] / float(total_votos)
        perc_eleitos = 100 * mini_uf['QTDE_ELEITOS'] / float(total_eleitos)
        perc_candidatos = 100 * mini_uf['QTDE_CANDIDATOS'] / float(total_candidatos)

        tracos.append(go.Scatter(
            x=perc_candidatos,
            y=perc_eleitos,
            text=str(mini_uf['QTDE_VOTOS'].values[0]) + " votos" + '<br>' +
                 str(mini_uf['QTDE_CANDIDATOS'].values[0]) + " candidatos" + '<br>' +
                 str(int(mini_uf['QTDE_ELEITOS'].values[0])) + " eleitos",
            mode='markers',
            opacity=0.7,
            marker={
                'size': perc_votos + 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=uf
        ))
    return {
        'data': tracos,
        'layout': go.Layout(
            xaxis={'type': '-', 'title': 'Percentual de Candidatos', 'autorange': 'reversed'},
            yaxis={'title': 'Percentual de Eleitos', 'autorange': 'True'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            # legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


@app.callback(
    Output('play', 'hidden'),
    [Input('play', 'n_clicks'),
     Input('pause', 'n_clicks')],
    [State('passador', 'value')])
def visibilidade_play(play, pause, ano):
    if ano >= MAIOR_ANO:
        return False
    else:
        if (play > pause):
            return True
        else:
            return False


@app.callback(
    Output('pause', 'hidden'),
    [Input('play', 'n_clicks'),
     Input('pause', 'n_clicks')],
    [State('passador', 'value')])
def visibilidade_pause(play, pause, ano):
    if ano >= MAIOR_ANO:
        return True
    else:
        if play > pause:
            return False
        else:
            return True


@app.callback(
    Output('intervalo', 'interval'),
    [Input('play', 'n_clicks'),
     Input('pause', 'n_clicks')],
    [State('passador', 'value')])
def controlar_intervalo(play, pause, ano):
    if ano >= MAIOR_ANO:
        return PARADO
    else:
        if play > pause:
            return TEMPO
        else:
            return PARADO


# atualiza passador
@app.callback(
    Output('passador', 'value'),
    events=[Event('intervalo', 'interval')],
    state=[State('passador', 'value')])
def atualiza_ano(ano):
    if ano < MAIOR_ANO:
        ano += 4
    return ano
