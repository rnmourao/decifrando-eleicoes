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

# Bandeira < 0.31 <= Regional
RECORTE_PERFIL = 0.31
PERFIL_BANDEIRA = open('data/perfil_bandeira.txt', 'r').read()
PERFIL_REGIONAL = open('data/perfil_regional.txt', 'r').read()

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

# definir perfil dos candidatos
centis['PERFIL'] = 'Regional'
centis['PERFIL'][centis['CENTIL'] < RECORTE_PERFIL] = 'Bandeira'

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
               html.H1('"Cada homem que encontro é superior a mim em alguma coisa; e nisto posso aprender dele".'),
               html.Div(html.H3('Dale Carnegie', style={'width' : 'auto'}), style={'display' : 'flex', 'justify-content' : 'flex-end'}),
            #    html.H4('Dale Carnegie', style={'display' : 'flex', 'align-content' : 'flex-end', 'width' : 'auto'}),
                        html.H3(['Candidatos precisam conhecer suas características eleitorais para maximizar seus resultados nas urnas. A partir de um algoritmo de similaridade, identificamos os candidatos que mais se parecem no que tange à distribuição de sua votação no âmbito de uma Unidade Federativa e criamos uma classificação para eles inspiradas em um trabalho acadêmico dos membros da equipe Decipher, obtido em ', html.A('https://osf.io/8z88j', href='https://osf.io/8z88j', target='_blank')], style={'font-style': 'italic'}),
               html.Div([
                         html.Div([html.P('Estado: ', style={'width' : '15%'}),
                                   html.Div(dcc.Dropdown(options=ufs, id='perfil-combo-ufs'), style={'width': '40%'})], style={'display': 'flex', 'align-items': 'center'}),

                         html.Div([html.P('Candidato: ', style={'width' : '15%'}),
                                   html.Div(dcc.Dropdown(options=[], id='perfil-combo-candidatos'), style={'width': '40%'})],
                                  style={'display' : 'flex', 'align-items': 'center'})
                       ], id='head', style={'padding' : '25px'}),
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

    return [ card_resumo_perfil(candidato),
             html.Div([card_menos_votado_perfil(candidato),
                       card_candidato_perfil(candidato),
                       card_mais_votado_perfil(candidato)], style={'display' : 'flex', 'justify-content' : 'space-around'}),
             pizza_perfil(candidato),
             barra_resultado_perfil(candidato),
             tabela_similares_perfil(candidato)
           ]


def card_candidato_perfil(candidato):
    nome = candidato['NOME_URNA_CANDIDATO']
    partido = candidato['SIGLA_PARTIDO']
    coligacao = candidato['NOME_COLIGACAO']
    votos = str(int(candidato['QTDE_VOTOS']))
    idade = str(candidato['IDADE_DATA_ELEICAO'].iloc[0]) + " anos"
    natural = "Natural de " + candidato['NOME_MUNICIPIO_NASCIMENTO'] + " (" + candidato['SIGLA_UF_NASCIMENTO'] + ")"
    profissao = candidato['DESCRICAO_OCUPACAO']
    eleito = candidato['DESC_SIT_TOT_TURNO']
    return html.Div([html.H2('Candidato'),
                     html.H3(nome + " (" + partido + ")"),
                    #  html.H4(coligacao),
                     html.P(idade),
                     html.P(natural),
                    #  html.P(profissao),
                     html.P(eleito + ' (' + votos + ' votos)')], style={'background-color' : '#3971b3',
                                             'color' : 'white',
                                             'display': 'flex',
                                             'flex-direction': 'column',
                                             'flex-wrap' : 'wrap',
                                             'justify-content': 'center',
                                             'align-items': 'center',
                                             'height' : '350px',
                                             'padding': '5px'})


def card_menos_votado_perfil(candidato):
    uf = candidato['SIGLA_UE'].iloc[0]
    perfil = candidato['PERFIL'].iloc[0]

    # selecionar eleitos do estado
    eleitos = centis[(centis['SIGLA_UE'] == uf) & ((centis['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') |
                    (centis['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')) ]

    # ordenar eleitos do mesmo perfil
    eleitos_perfil = eleitos[eleitos['PERFIL'] == perfil]
    eleitos_perfil = eleitos_perfil.sort_values(by='QTDE_VOTOS').reset_index(drop=True)

    # identificar deputado federal menos votado
    menos = eleitos_perfil.head(1)
    nome = menos['NOME_URNA_CANDIDATO']
    partido = menos['SIGLA_PARTIDO']
    coligacao = menos['NOME_COLIGACAO']
    votos = str(int(menos['QTDE_VOTOS']))
    idade = str(menos['IDADE_DATA_ELEICAO'].iloc[0]) + " anos"
    natural = "Natural de " + menos['NOME_MUNICIPIO_NASCIMENTO'] + " (" + menos['SIGLA_UF_NASCIMENTO'] + ")"
    profissao = menos['DESCRICAO_OCUPACAO']
    eleito = menos['DESC_SIT_TOT_TURNO']
    return html.Div([html.H2(perfil + ' Menos Votado'),
                     html.H3(nome + " (" + partido + ")"),
                    #  html.H4(coligacao),
                     html.P(idade),
                     html.P(natural),
                    #  html.P(profissao),
                     html.P(eleito + ' (' + votos + ' votos)')], style={'background-color' : '#d0342e',
                                             'color' : 'white',
                                             'display': 'flex',
                                             'flex-direction': 'column',
                                             'flex-wrap' : 'wrap',
                                             'justify-content': 'center',
                                             'align-items': 'center',
                                             'height' : '350px',
                                             'padding': '5px'})


def card_mais_votado_perfil(candidato):
    uf = candidato['SIGLA_UE'].iloc[0]
    perfil = candidato['PERFIL'].iloc[0]

    # selecionar eleitos do estado
    eleitos = centis[(centis['SIGLA_UE'] == uf) & ((centis['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') |
                    (centis['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')) ]

    # ordenar eleitos do mesmo perfil
    eleitos_perfil = eleitos[eleitos['PERFIL'] == perfil]
    eleitos_perfil = eleitos_perfil.sort_values(by='QTDE_VOTOS').reset_index(drop=True)

    # identificar deputado federal mais votado
    mais = eleitos_perfil.tail(1)
    nome = mais['NOME_URNA_CANDIDATO']
    partido = mais['SIGLA_PARTIDO']
    coligacao = mais['NOME_COLIGACAO']
    votos = str(int(mais['QTDE_VOTOS']))
    idade = str(mais['IDADE_DATA_ELEICAO'].iloc[0]) + " anos"
    natural = "Natural de " + mais['NOME_MUNICIPIO_NASCIMENTO'] + " (" + mais['SIGLA_UF_NASCIMENTO'] + ")"
    profissao = mais['DESCRICAO_OCUPACAO']
    eleito = mais['DESC_SIT_TOT_TURNO']
    return html.Div([html.H2(perfil + ' Mais Votado'),
                     html.H3(nome + " (" + partido + ")"),
                    #  html.H4(coligacao),
                     html.P(idade),
                     html.P(natural),
                    #  html.P(profissao),
                     html.P(eleito + ' (' + votos + ' votos)')], style={'background-color' : '#2fa12e',
                                             'color' : 'white',
                                             'display': 'flex',
                                             'flex-direction': 'column',
                                             'flex-wrap' : 'wrap',
                                             'justify-content': 'center',
                                             'align-items': 'center',
                                             'height' : '350px',
                                             'padding': '5px'})



def card_resumo_perfil(candidato):
    if candidato['PERFIL'].iloc[0] == 'Bandeira':
        resumo = PERFIL_BANDEIRA
    else:
        resumo = PERFIL_REGIONAL

    return html.Div([html.H2('Perfil do Candidato: ' + candidato['PERFIL'].iloc[0]),
                     html.H4(resumo)])


def pizza_perfil(candidato):
    uf = candidato['SIGLA_UE'].iloc[0]
    perfil = candidato['PERFIL'].iloc[0]

    # selecionar eleitos do estado
    eleitos = centis[(centis['SIGLA_UE'] == uf) & ((centis['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') |
                    (centis['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')) ]

    # pizza eleitos por perfil
    grupo = eleitos.groupby('PERFIL').size().reset_index(name='QUANTIDADE')
    pizza = dcc.Graph(figure={
                              'data': [go.Pie(labels=grupo['PERFIL'].values.tolist(),
                                              values=grupo['QUANTIDADE'].values.tolist(),
                                              hole=0.5)],
                              'layout': go.Layout(
                                                  {'annotations': [{'font': {'size': 20},
                                                                    'showarrow': False,
                                                                    'text': 'Eleitos',
                                                                    'x': 0.50,
                                                                    'y': 0.5}],
                                                   'title' : 'Perfil dos Eleitos'}
                                                 )},
                      id='pizza-eleitos-perfil')

    return html.Div(pizza)


def barra_resultado_perfil(candidato):
    uf = candidato['SIGLA_UE'].iloc[0]

    cands_uf = centis[centis['SIGLA_UE'] == uf]

    prf = pd.merge(pd.DataFrame({'DESC_SIT_TOT_TURNO' : ['ELEITO POR QP', 'ELEITO POR MÉDIA', 'SUPLENTE', 'NÃO ELEITO'], 'CHAVE': [1, 1, 1, 1]}),
                   pd.DataFrame({'PERFIL' : ['Bandeira', 'Regional'], 'CHAVE': [1, 1]}))

    qt_perfil = cands_uf.groupby(['PERFIL', 'DESC_SIT_TOT_TURNO']).size().reset_index(name='QUANTIDADE')
    qt_perfil = pd.merge(prf, qt_perfil, how='left').fillna(0).reset_index(drop=True)

    trace1 = go.Bar(x=qt_perfil['DESC_SIT_TOT_TURNO'][qt_perfil['PERFIL'] == 'Bandeira'],
                    y=qt_perfil['QUANTIDADE'][qt_perfil['PERFIL'] == 'Bandeira'],
                    name='Bandeira'
                   )

    trace2 = go.Bar(x=qt_perfil['DESC_SIT_TOT_TURNO'][qt_perfil['PERFIL'] == 'Regional'],
                    y=qt_perfil['QUANTIDADE'][qt_perfil['PERFIL'] == 'Regional'],
                    name='Regional'
                   )
    data = [trace1, trace2]
    layout = go.Layout( barmode='group', title='Resultado da Eleição baseada no Perfil' )

    return dcc.Graph(figure={'data': data, 'layout': layout}, id='barra-resultado-perfil')


def tabela_similares_perfil(candidato):
#   identificar candidatos com votacao expressiva que sao similares ao candidato selecionado
    centil = candidato['CENTIL'].iloc[0]
    similares = expressivos[expressivos['CPF_CANDIDATO'] != candidato['CPF_CANDIDATO'].iloc[0]]
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

    return html.Div([html.P('Candidatos semelhantes', style=css.div_centralizada),
                     html.Div(html.Table(dados_similares, style=css.tabela['table']), style=css.div_centralizada)])
