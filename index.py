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
            {'label': 'Tempo de Rádio e TV', 'value': 'idx-calc'},
            {'label': 'Eficiência dos Partidos', 'value': 'idx-bolhas'},
            {'label': 'Benchmark Eleitoral', 'value': 'idx-perfil'},
            {'label': 'Capital Eleitoral', 'value': 'idx-capital'},
            {'label': 'Cargos', 'value': 'idx-cargo'}
        ],
        value='idx-calc',
        vertical=True,
        id='tabs'
    ),
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
