# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

import sys
sys.path.append('..')
from cepesp import *

cargos = [CARGO.PRESIDENTE,
          CARGO.GOVERNADOR,
          CARGO.SENADOR,
          CARGO.DEPUTADO_FEDERAL,
          CARGO.DEPUTADO_ESTADUAL,
          CARGO.DEPUTADO_DISTRITAL,
          CARGO.PREFEITO,
          CARGO.VEREADOR]

anos = pd.DataFrame()
for cargo in cargos:
    if cargo in [CARGO.PREFEITO, CARGO.VEREADOR]:
        anos_temp = pd.DataFrame({'cargo': cargo, 'ano': np.arange(2016, 1998, -4)})
    else:
        anos_temp = pd.DataFrame({'cargo': cargo, 'ano': np.arange(2014, 1996, -4)})
    anos = pd.concat([anos, anos_temp]).reset_index(drop=True)

candidatos = pd.DataFrame()
for indice, linha in anos.iterrows():
    print(str(linha['cargo']) + "-" + str(linha['ano']) + ":")

    vc = votos_x_candidatos(cargo=linha['cargo'],
                            ano=linha['ano'],
                            agregacao_politica=AGR_POLITICA.CANDIDATO,
                            agregacao_regional=AGR_REGIONAL.MUNICIPIO)
    vc = vc.where(pd.notnull(vc), None)
    vc[['CODIGO_CARGO_x','ANO_ELEICAO', 'NUMERO_CANDIDATO', 'IDADE_DATA_ELEICAO']] = vc[['CODIGO_CARGO_x','ANO_ELEICAO', 'NUMERO_CANDIDATO', 'IDADE_DATA_ELEICAO']].apply(pd.to_numeric)

    # dados basicos
    bas = vc.groupby(['CODIGO_CARGO_x',
                      'ANO_ELEICAO',
                      'UF',
                      'NOME_MUNICIPIO',
                      'NUMERO_CANDIDATO',
                      'NOME_URNA_CANDIDATO',
                      'SIGLA_PARTIDO',
                      'IDADE_DATA_ELEICAO',
                      'DESCRICAO_ESTADO_CIVIL',
                      'DESCRICAO_SEXO',
                      'DESCRICAO_GRAU_INSTRUCAO',
                      'DESCRICAO_OCUPACAO',
                      'SIGLA_UF_NASCIMENTO',
                      'NOME_MUNICIPIO_NASCIMENTO'
                     ], as_index=False).size().reset_index(name='QT')
    bas = bas.rename(columns={'CODIGO_CARGO_x': 'CODIGO_CARGO'})
    bas['NOME_URNA_CANDIDATO'][bas['NUMERO_CANDIDATO'] == 95] == 'BRANCOS'
    bas['NOME_URNA_CANDIDATO'][bas['NUMERO_CANDIDATO'] == 96] == 'NULOS'
    del bas['QT']

    # votos 1º turno
    vt1 = vc[['NUMERO_CANDIDATO', 'QTDE_VOTOS']][vc['NUM_TURNO'] == '1']
    bas = pd.merge(bas, vt1, on='NUMERO_CANDIDATO', how='left')

    # votos 2º turno
    vt2 = vc[['NUMERO_CANDIDATO', 'QTDE_VOTOS']][vc['NUM_TURNO'] == '2']
    bas = pd.merge(bas, vt2, on='NUMERO_CANDIDATO', how='left')

    # despesa campanha
    des = vc[['NUMERO_CANDIDATO', 'DESPESA_MAX_CAMPANHA']][vc['NUM_TURNO'] == '1']
    bas = pd.merge(bas, des, on='NUMERO_CANDIDATO', how='left')

    # eleito ou nao eleito
    e01 = vc[['NUMERO_CANDIDATO']][(vc['DESC_SIT_TOT_TURNO'] == 'ELEITO') | (vc['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') | (vc['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')].reset_index(drop=True)
    e01['ELEITO'] = 1
    bas = pd.merge(bas, e01, on='NUMERO_CANDIDATO', how='left')

    # acumular informacoes
    candidatos = pd.concat([candidatos, bas]).reset_index(drop=True)

candidatos.to_csv('../data/candidatos.csv', index=False)
