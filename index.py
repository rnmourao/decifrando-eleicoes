# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
from apps import bolhas, capital_eleitoral, perfil, cargo, calculadora
import css

server = app.server

app.layout = html.Div([
     dcc.Tabs(
        tabs=[
            {'label': 'Cargos', 'value': 'idx-cargo'},
            {'label': 'Calculadora de TV', 'value': 'idx-calc'},
            {'label': 'Eficiência dos Partidos', 'value': 'idx-bolhas'},
            {'label': 'Perfil do Candidato', 'value': 'idx-perfil'},
            {'label': 'Capital Eleitoral', 'value': 'idx-capital'}
        ],
        value='idx-cargo',
        vertical=True,
        id='tabs'
    ),
    # html.Div([
    # dcc.RadioItems(
    # options=[
    #     {'label': 'Cargos', 'value': 'idx-cargo'},
    #     {'label': 'Calculadora de TV', 'value': 'idx-calc'},
    #     {'label': 'Eficiência dos Partidos', 'value': 'idx-bolhas'},
    #     {'label': 'Perfil do Candidato', 'value': 'idx-perfil'},
    #     {'label': 'Capital Eleitoral', 'value': 'idx-capital'}
    # ],
    # value='idx-bolhas',
    # id='tabs')], style=css.index['div-esquerda']),
    html.Div(id='page-content', style=css.index['div-direita'])
], style=css.index['todo'])


@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def idx_cargo(tela):
    if tela == 'idx-cargo':
        return cargo.layout
    elif tela == 'idx-calc':
        return calculadora.layout
    elif tela == 'idx-bolhas':
        return bolhas.layout
    elif tela == 'idx-perfil':
        return perfil.layout
    else:
        return capital_eleitoral.layout


if __name__ == '__main__':
    app.run_server(debug=True)
