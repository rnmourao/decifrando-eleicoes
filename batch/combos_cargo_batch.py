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

combos = pd.DataFrame()
for indice, linha in anos.iterrows():
    print(str(linha['cargo']) + "-" + str(linha['ano']) + ":")

    v = votos(cargo=linha['cargo'], ano=linha['ano'], agregacao_politica=AGR_POLITICA.PARTIDO, agregacao_regional=AGR_REGIONAL.MUNICIPIO)
    temp = v.groupby(['CODIGO_CARGO', 'ANO_ELEICAO', 'UF', 'NOME_MUNICIPIO'], as_index=False).size().reset_index(name='QT')
    combos = pd.concat([combos, temp]).reset_index(drop=True)

del combos['QT']

combos.to_csv('../data/combos_cargo.csv', index=False)
