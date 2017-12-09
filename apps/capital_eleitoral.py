# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import locale

from app import app

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

print('entrou capital eleitoral')

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
deputados = pd.read_csv('data/capital_eleitoral_2018.csv')

layout = html.Div([
               html.Div([
                         dcc.Dropdown(options=ufs, id='combo-ufs')
                       ], id='head'),
               html.Div(id='ce-body')
              ])

@app.callback(Output('ce-body', 'children'),
              [Input('combo-ufs', 'value')])
def preenche_capital_eleitoral(uf):
    if not uf:
        return []

    deputados_uf = deputados[deputados['SIGLA_UF'] == uf]
    deputados_uf = deputados_uf.sort_values(by='TARGET', ascending=False)
    deputados_uf = deputados_uf.reset_index(drop=True)
    print(deputados_uf.dtypes)

    dados_deputados_uf = html.Table(
        # Header
        [html.Tr([html.Td('Nome'), html.Td('Quociente Eleitoral Atingido 2014'), html.Td('Quociente Eleitoral Esperado 2018')])] +

        # Body
        [html.Tr([html.Td(s['NOME_URNA_CANDIDATO']), html.Td('{:.2f}'.format(100 * s['PERC_QE'])), html.Td('{:.2f}'.format(100 * s['TARGET']))]) for i, s in deputados_uf.iterrows()]
    )

    return html.Div(dados_deputados_uf)
