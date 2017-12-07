# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

import sys
sys.path.append('..')
from cepesp import *

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

todos.to_csv('../data/calculadora.csv', index=False)
