# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
from apps import bolhas, capital_eleitoral, perfil, cargo, calculadora

server = app.server

app.layout = html.Div([
    #  dcc.Tabs(
    #     tabs=[
    #         {'label': 'Cargos', 'value': 'idx-cargo'},
    #         {'label': 'Calculadora de TV', 'value': 'idx-calc'},
    #         {'label': 'Eficiência dos Partidos', 'value': 'idx-bolhas'},
    #         {'label': 'Perfil do Candidato', 'value': 'idx-perfil'},
    #         {'label': 'Capital Eleitoral', 'value': 'idx-capital'}
    #     ],
    #     value='idx-cargo',
    #     id='tabs'
    # ),
    dcc.RadioItems(
    options=[
        {'label': 'Cargos', 'value': 'idx-cargo'},
        {'label': 'Calculadora de TV', 'value': 'idx-calc'},
        {'label': 'Eficiência dos Partidos', 'value': 'idx-bolhas'},
        {'label': 'Perfil do Candidato', 'value': 'idx-perfil'},
        {'label': 'Capital Eleitoral', 'value': 'idx-capital'}
    ],
    value='idx-bolhas',
    id='tabs', style={'background': '#aaaaaa'}),
    html.Div(id='page-content')
])


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
        return capital.layout


if __name__ == '__main__':
    app.run_server(debug=True)
