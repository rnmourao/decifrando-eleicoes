# This Python file uses the following encoding: utf-8
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

import sys
sys.path.append('..')
from cepesp import *

sc = SparkContext('local','example')
spark = SparkSession(sc)

# pasta onde se encontram arquivos csv de entrada
mypath = '/media/mourao/BACKUP/eleicoes/'

# ler multiplos arquivos de votacao por secao extraidos do site
# http://www.tse.jus.br/hotSites/pesquisas-eleitorais/resultados.html
df = spark.read.format('csv') \
    .option('charset', 'iso-8859-1') \
    .option('sep', ';') \
    .option('header', 'False') \
    .load(mypath + 'votacao_secao_2014_*.txt')
df.createOrReplaceTempView("tab_df")

# renomear colunas, limitar pesquisa ao cargo de deputado federal e
# manter votos diretos aos candidatos.
df = spark.sql('''
                    SELECT _c6  AS uf
                         , _c9  AS zona
                         , _c10 AS secao
                         , _c13 AS candidato
                         , cast(_c14 AS INTEGER) AS votos
                    FROM tab_df
                    WHERE _c12 = "DEPUTADO FEDERAL"
                      AND CAST(_c13 AS INTEGER) > 100
''')
df.createOrReplaceTempView("tab_df")

# soma votos por zona
df_zona = spark.sql('''
                    SELECT uf
                         , candidato
                         , zona
                         , SUM(votos) AS votos
                    FROM tab_df
                    GROUP BY uf
                           , candidato
                           , zona
''')
df_zona.createOrReplaceTempView("tab_zona")

# cria o campo de soma acumulada de votos, zerando por uf e candidato e
# ordenado por votos, em ordem decrescente
df_zona = spark.sql('''
                    SELECT uf
                         , candidato
                         , votos
                         , SUM(votos) OVER (PARTITION BY uf
                                                       , candidato
                                            ORDER BY votos DESC) AS votos_acumulados
                         , COUNT(*)     OVER (PARTITION BY uf
                                                       , candidato
                                            ORDER BY votos DESC, zona) AS zonas_acumuladas
                    FROM tab_zona
''')
df_zona.createOrReplaceTempView("tab_zona")

# descobrir em quantas zonas cada candidato teve votos.
df_total_zonas = spark.sql('''
                    SELECT uf
                         , candidato
                         , COUNT(*) AS total_zonas
                    FROM tab_zona
                    GROUP BY uf
                           , candidato
''')
df_total_zonas.createOrReplaceTempView("tab_total_zonas")

# incluir total de zonas na tabela principal
df_zona = spark.sql('''
                    SELECT a.uf
                         , a.candidato
                         , a.votos
                         , a.votos_acumulados
                         , a.zonas_acumuladas
                         , b.total_zonas
                    FROM tab_zona        a
                       , tab_total_zonas b
                    WHERE a.candidato = b.candidato
                      AND a.uf = b.uf
 ''')
df_zona.createOrReplaceTempView("tab_zona")

# quantidadte total de votos por candidato. recupera maximo do cumsum.
df_total_votos = spark.sql('''
                    SELECT uf
                         , candidato
                         , MAX(votos_acumulados) AS total_votos
                    FROM tab_zona
                    GROUP BY uf
                           , candidato
''')
df_total_votos.createOrReplaceTempView("tab_total_votos")

# incluir total de votos do candidato na tabela principal
df_zona = spark.sql('''
                    SELECT a.uf
                         , a.candidato
                         , a.votos
                         , a.votos_acumulados
                         , b.total_votos
                         , a.zonas_acumuladas
                         , a.total_zonas
                    FROM tab_zona        a
                       , tab_total_votos b
                    WHERE a.candidato = b.candidato
                      AND a.uf = b.uf
 ''')
df_zona.createOrReplaceTempView("tab_zona")

# calcular centil
zonas_centil = spark.sql('''
                    SELECT uf
                        , candidato
                        , MIN(zonas_acumuladas) as zonas_centil
                    FROM tab_zona
                    WHERE zonas_acumuladas >=  (total_zonas / float(100))
                    GROUP BY uf
                          , candidato
 ''')
zonas_centil.createOrReplaceTempView("tab_zonas_centil")

df_centil = spark.sql('''
                    SELECT a.uf
                         , a.candidato
                         , (a.votos_acumulados / float(a.total_votos)) as CENTIL
                         , a.total_votos AS QTDE_VOTOS
                    FROM tab_zona a
                       , tab_zonas_centil b
                    where a.uf = b.uf
                      and a.candidato = b.candidato
                      and a.zonas_acumuladas = b.zonas_centil
''')
df_centil.createOrReplaceTempView("tab_centil")

centis = df_centil.toPandas()

# recuperar todos deputados federais de 2014
deputados = candidatos(cargo=CARGO.DEPUTADO_FEDERAL, ano=2014)
# deputados['NUMERO_CANDIDATO'] = pd.to_numeric(deputados['NUMERO_CANDIDATO'], errors='coerce')

# efetuar merge dos dois dataframes
deputados = pd.merge(deputados, centis, left_on=['SIGLA_UF', 'NUMERO_CANDIDATO'], right_on=['uf', 'candidato'], how='inner')

deputados = deputados[['ANO_ELEICAO',
                       'SIGLA_UE',
                       'DESCRICAO_UE',
                       'NUMERO_CANDIDATO',
                       'CPF_CANDIDATO',
                       'NOME_URNA_CANDIDATO',
                       'DESCRICAO_CARGO',
                       'SIGLA_PARTIDO',
                       'NOME_COLIGACAO',
                       'DESCRICAO_OCUPACAO',
                       'IDADE_DATA_ELEICAO',
                       'DESCRICAO_SEXO',
                       'DESCRICAO_GRAU_INSTRUCAO',
                       'DESCRICAO_ESTADO_CIVIL',
                       'DESCRICAO_COR_RACA',
                       'SIGLA_UF_NASCIMENTO',
                       'NOME_MUNICIPIO_NASCIMENTO',
                       'DESPESA_MAX_CAMPANHA',
                       'DESC_SIT_TOT_TURNO',
                       'CENTIL',
                       'QTDE_VOTOS']]

deputados.to_csv('../data/centis_deputados_federais_2014.csv', index=False)
