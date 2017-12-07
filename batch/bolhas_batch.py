# -*- coding: utf-8 -*-
from cepesp import *
import pandas as pd
import numpy as np

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
    anos = anos.append(anos_temp)

anos = anos.reset_index(drop=True)

candidatos_partidos = pd.DataFrame()
votos_partidos = pd.DataFrame()
eleitos_partidos = pd.DataFrame()
for indice, linha in anos.iterrows():
    print(str(linha['cargo']) + "-" + str(linha['ano']) + ":")

    # recuperar quantidade de votos por partido, cargo e ano
    vc = votos_x_candidatos(cargo=linha['cargo'], ano=linha['ano'], agregacao_politica=AGR_POLITICA.CANDIDATO, agregacao_regional=AGR_REGIONAL.UF)
    vc['CODIGO_CARGO'] = vc['CODIGO_CARGO_x']
    vc['QTDE_VOTOS'] = pd.to_numeric(vc['QTDE_VOTOS'], errors='coerce')

    # recuperar quantidade de candidatos
    temp = vc[vc['NUM_TURNO'] == '1'][['SIGLA_PARTIDO', 'ANO_ELEICAO', 'UF', 'CODIGO_CARGO']].reset_index(drop=True)
    temp = temp.groupby(['SIGLA_PARTIDO', 'ANO_ELEICAO', 'UF', 'CODIGO_CARGO'], as_index=False).size().reset_index(name='QTDE_CANDIDATOS')
    temp = temp.fillna(0)
    candidatos_partidos = pd.concat([candidatos_partidos,temp]).reset_index(drop=True)

    temp = vc[vc['NUM_TURNO'] == '1'][['SIGLA_PARTIDO', 'ANO_ELEICAO', 'UF', 'CODIGO_CARGO', 'QTDE_VOTOS']].reset_index(drop=True)
    temp = temp.groupby(['SIGLA_PARTIDO', 'ANO_ELEICAO', 'UF', 'CODIGO_CARGO'], as_index=False)['QTDE_VOTOS'].agg({'QTDE_VOTOS': np.sum})
    temp = temp.fillna(0)
    votos_partidos = pd.concat([votos_partidos,temp]).reset_index(drop=True)

    # recuperar quantidade de eleitos por partido, cargo e ano
    temp = vc[(vc['DESC_SIT_TOT_TURNO'] == 'ELEITO') | (vc['DESC_SIT_TOT_TURNO'] == 'ELEITO POR QP') | (vc['DESC_SIT_TOT_TURNO'] == 'ELEITO POR MÉDIA')][['SIGLA_PARTIDO', 'ANO_ELEICAO', 'UF', 'CODIGO_CARGO', 'DESC_SIT_TOT_TURNO']].reset_index(drop=True)
    temp = temp.groupby(['SIGLA_PARTIDO', 'ANO_ELEICAO', 'UF', 'CODIGO_CARGO'], as_index=False).size().reset_index(name='QTDE_ELEITOS')
    temp = temp.fillna(0)
    eleitos_partidos = pd.concat([eleitos_partidos, temp]).reset_index(drop=True)

bolhas_votos = pd.merge(candidatos_partidos, votos_partidos, on=['SIGLA_PARTIDO', 'ANO_ELEICAO', 'UF', 'CODIGO_CARGO'])
bolhas_votos = pd.merge(bolhas_votos, eleitos_partidos, on=['SIGLA_PARTIDO', 'ANO_ELEICAO', 'UF', 'CODIGO_CARGO'], how='left')
bolhas_votos.to_csv('../data/bolhas.csv', index=False)
