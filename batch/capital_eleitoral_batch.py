# This Python file uses the following encoding: utf-8
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession

sc = SparkContext('local','example')
spark = SparkSession(sc)

# pasta onde se encontram arquivos csv de entrada
mypath = '/media/mourao/BACKUP/eleicoes/'

# ler multiplos arquivos de candidatos extraidos do site
# http://www.tse.jus.br/hotSites/pesquisas-eleitorais/resultados.html
# recupera arquivo com candidatos de 2010
cand10 = spark.read.format('csv') \
    .option('charset', 'iso-8859-1') \
    .option('sep', ';') \
    .option('header', 'False') \
    .load(mypath + 'consulta_cand_2010_*.txt')
cand10.createOrReplaceTempView("T_CAND10")

# seleciona candidatos a deputado estadual e distrital
# seleciona variaveis
de10 = spark.sql("""
    SELECT _c5  AS SIGLA_UF
         , _c8  AS CODIGO_CARGO
         , _c12 AS NUMERO_CANDIDATO
         , _c13 AS CPF_CANDIDATO
         , _c14 AS NOME_URNA_CANDIDATO
         , _c20 AS CODIGO_LEGENDA
         , _c25 AS DESCRICAO_OCUPACAO
         , _c28 AS IDADE_DATA_ELEICAO
         , _c30 AS DESCRICAO_SEXO
         , _c32 AS DESCRICAO_GRAU_INSTRUCAO
         , _c34 AS DESCRICAO_ESTADO_CIVIL
         , _c37 AS SIGLA_UF_NASCIMENTO
         , _c39 AS NOME_MUNICIPIO_NASCIMENTO
         , _c40 AS DESPESA_MAX_CAMPANHA
         , _c42 AS DESC_SIT_TOT_TURNO
    FROM T_CAND10
    WHERE _c9 = 'DEPUTADO ESTADUAL'
       OR _c9 = 'DEPUTADO DISTRITAL'
""")
de10.createOrReplaceTempView("T_DE10")

# ler multiplos arquivos de votacao por secao extraidos do site
# http://www.tse.jus.br/hotSites/pesquisas-eleitorais/resultados.html
vot10 = spark.read.format('csv') \
    .option('charset', 'iso-8859-1') \
    .option('sep', ';') \
    .option('header', 'False') \
    .load(mypath + 'votacao_secao_2010_*.txt')
vot10.createOrReplaceTempView("T_VOT10")

# soma votos por candidato e seleciona variaveis
vot10 = spark.sql("""
    SELECT _c5 AS SIGLA_UF
         , _c11 AS CODIGO_CARGO
         , _c12 AS DESCRICAO_CARGO
         , _c13 AS NUMERO_CANDIDATO
         , SUM(_c14) AS QTDE_VOTOS
    FROM T_VOT10
    GROUP BY _c5
           , _c11
           , _c12
           , _c13
""")
vot10.createOrReplaceTempView("T_VOT10")

# efetua merge de votacoes e candidatos de 2010
de10 = spark.sql("""
    SELECT A.SIGLA_UF
         , A.CPF_CANDIDATO
         , A.NOME_URNA_CANDIDATO
         , A.CODIGO_LEGENDA
         , A.IDADE_DATA_ELEICAO
         , A.DESCRICAO_OCUPACAO
         , A.DESCRICAO_SEXO
         , A.DESCRICAO_GRAU_INSTRUCAO
         , A.DESCRICAO_ESTADO_CIVIL
         , A.SIGLA_UF_NASCIMENTO
         , A.NOME_MUNICIPIO_NASCIMENTO
         , A.DESPESA_MAX_CAMPANHA
         , A.DESC_SIT_TOT_TURNO
         , B.QTDE_VOTOS
    FROM T_DE10   A
       , T_VOT10  B
    WHERE A.SIGLA_UF         = B.SIGLA_UF
      AND A.CODIGO_CARGO     = B.CODIGO_CARGO
      AND A.NUMERO_CANDIDATO = B.NUMERO_CANDIDATO
""")
de10.createOrReplaceTempView("T_DE10")

# recupera arquivo com candidatos de 2014
cand14 = spark.read.format('csv') \
    .option('charset', 'iso-8859-1') \
    .option('sep', ';') \
    .option('header', 'False') \
    .load(mypath + 'consulta_cand_2014_*.txt')
cand14.createOrReplaceTempView("T_CAND14")

# seleciona candidatos a deputado federal
# seleciona variaveis
df14 = spark.sql("""
    SELECT _c5  AS SIGLA_UF
         , _c8  AS CODIGO_CARGO
         , _c12 AS NUMERO_CANDIDATO
         , _c13 AS CPF_CANDIDATO
         , _c14 AS NOME_URNA_CANDIDATO
         , _c20 AS CODIGO_LEGENDA
         , _c25 AS DESCRICAO_OCUPACAO
         , _c28 AS IDADE_DATA_ELEICAO
         , _c30 AS DESCRICAO_SEXO
         , _c32 AS DESCRICAO_GRAU_INSTRUCAO
         , _c34 AS DESCRICAO_ESTADO_CIVIL
         , _c39 AS SIGLA_UF_NASCIMENTO
         , _c41 AS NOME_MUNICIPIO_NASCIMENTO
         , _c42 AS DESPESA_MAX_CAMPANHA
         , _c44 AS DESC_SIT_TOT_TURNO
    FROM T_CAND14
    WHERE _c9 = 'DEPUTADO FEDERAL'
""")
df14.createOrReplaceTempView("T_DF14")

# recupera arquivo com votacoes de 2014
vot14 = spark.read.format('csv') \
    .option('charset', 'iso-8859-1') \
    .option('sep', ';') \
    .option('header', 'False') \
    .load(mypath + 'votacao_secao_2014_*.txt')
vot14.createOrReplaceTempView("T_VOT14")

# soma votos por candidato e seleciona variaveis
vot14 = spark.sql("""
    SELECT _c5 AS SIGLA_UF
         , _c11 AS CODIGO_CARGO
         , _c12 AS DESCRICAO_CARGO
         , _c13 AS NUMERO_CANDIDATO
         , SUM(_c14) AS QTDE_VOTOS
    FROM T_VOT14
    GROUP BY _c5
           , _c11
           , _c12
           , _c13
""")
vot14.createOrReplaceTempView("T_VOT14")

# efetua merge de votacoes e candidatos de 2014
df14 = spark.sql("""
    SELECT A.SIGLA_UF
         , A.CPF_CANDIDATO
         , A.NOME_URNA_CANDIDATO
         , A.CODIGO_LEGENDA
         , A.IDADE_DATA_ELEICAO
         , A.DESCRICAO_OCUPACAO
         , A.DESCRICAO_SEXO
         , A.DESCRICAO_GRAU_INSTRUCAO
         , A.DESCRICAO_ESTADO_CIVIL
         , A.SIGLA_UF_NASCIMENTO
         , A.NOME_MUNICIPIO_NASCIMENTO
         , A.DESPESA_MAX_CAMPANHA
         , A.DESC_SIT_TOT_TURNO
         , B.QTDE_VOTOS
    FROM T_DF14   A
       , T_VOT14  B
    WHERE A.SIGLA_UF         = B.SIGLA_UF
      AND A.CODIGO_CARGO     = B.CODIGO_CARGO
      AND A.NUMERO_CANDIDATO = B.NUMERO_CANDIDATO
""")
df14.createOrReplaceTempView("T_DF14")

# identifica nos arquivos candidatos a estadual/distrital em 2010 que foram
# candidatos a deputado federal em 2014. Criar dataframe com esses candidatos.
up14 = spark.sql("""
    SELECT B.SIGLA_UF
         , B.NOME_URNA_CANDIDATO
         , B.CPF_CANDIDATO
         , B.SIGLA_UF_NASCIMENTO
         , B.NOME_MUNICIPIO_NASCIMENTO
         , A.CODIGO_LEGENDA            AS LEGENDA_ESTADUAL
         , B.CODIGO_LEGENDA            AS LEGENDA_FEDERAL
         , A.IDADE_DATA_ELEICAO        AS IDADE_ESTADUAL
         , A.DESCRICAO_OCUPACAO        AS OCUPACAO_ESTADUAL
         , B.DESCRICAO_OCUPACAO        AS OCUPACAO_FEDERAL
         , A.DESCRICAO_SEXO            AS SEXO_ESTADUAL
         , B.DESCRICAO_SEXO            AS SEXO_FEDERAL
         , A.DESCRICAO_GRAU_INSTRUCAO  AS INSTRUCAO_ESTADUAL
         , B.DESCRICAO_GRAU_INSTRUCAO  AS INSTRUCAO_FEDERAL
         , A.DESCRICAO_ESTADO_CIVIL    AS ESTADO_CIVIL_ESTADUAL
         , B.DESCRICAO_ESTADO_CIVIL    AS ESTADO_CIVIL_FEDERAL
         , A.DESPESA_MAX_CAMPANHA      AS DESPESA_ESTADUAL
         , B.DESPESA_MAX_CAMPANHA      AS DESPESA_FEDERAL
         , A.DESC_SIT_TOT_TURNO        AS RESULTADO_ESTADUAL
         , A.QTDE_VOTOS                AS VOTOS_ESTADUAL
         , B.QTDE_VOTOS                AS VOTOS_FEDERAL
    FROM T_DE10 A
       , T_DF14 B
    WHERE A.CPF_CANDIDATO       = B.CPF_CANDIDATO
      AND A.NOME_URNA_CANDIDATO = B.NOME_URNA_CANDIDATO
""")
up14.createOrReplaceTempView("T_UP")

# identificar se candidato foi eleito em 2010
up14 = spark.sql("""
    SELECT *
         , CASE WHEN RESULTADO_ESTADUAL = 'ELEITO'
                  OR RESULTADO_ESTADUAL = 'ELEITO POR QP'
                  OR RESULTADO_ESTADUAL = 'ELEITO POR MÉDIA'
                  OR RESULTADO_ESTADUAL = 'MÉDIA'
                  OR RESULTADO_ESTADUAL = 'QP'
                THEN 1
                ELSE 0
            END AS IN_ELEITO
    FROM T_UP
""")
up14.createOrReplaceTempView("T_UP")

## identificar ordem de classificacao do candidato em sua coligacao de 2010
ranking = spark.sql('''
    SELECT SIGLA_UF
         , CODIGO_LEGENDA
         , CPF_CANDIDATO
         , QTDE_VOTOS
         , COUNT(*) OVER (PARTITION BY SIGLA_UF
                                     , CODIGO_LEGENDA
                          ORDER BY QTDE_VOTOS DESC) AS RANKING_LEGENDA
    FROM T_DE10
''')
ranking.createOrReplaceTempView("T_RANK")

# ultima colocacao de cada legenda em cada estado
max_ranking = spark.sql('''
    SELECT SIGLA_UF
         , CODIGO_LEGENDA
         , MAX(RANKING_LEGENDA) AS MAX_RANKING_LEGENDA
    FROM T_RANK
    GROUP BY SIGLA_UF
           , CODIGO_LEGENDA
''')
max_ranking.createOrReplaceTempView("T_MAX_RANK")

# colocacao em percentual
ranking = spark.sql("""
    SELECT A.SIGLA_UF
         , A.CPF_CANDIDATO
         , A.RANKING_LEGENDA / FLOAT(B.MAX_RANKING_LEGENDA) AS RANKING_LEGENDA
    FROM T_RANK     A
       , T_MAX_RANK B
    WHERE A.SIGLA_UF       = B.SIGLA_UF
      AND A.CODIGO_LEGENDA = B.CODIGO_LEGENDA
""")
ranking.createOrReplaceTempView("T_RANK")

# join com a tabela up14
up14 = spark.sql("""
    SELECT A.*
         , B.RANKING_LEGENDA
    FROM T_UP      A
       , T_RANK    B
    WHERE A.SIGLA_UF      = B.SIGLA_UF
      AND A.CPF_CANDIDATO = B.CPF_CANDIDATO
""")
up14.createOrReplaceTempView("T_UP")

## incluir percentual de votos que o candidato obteve em 2010 em comparação ao total de votos do estado
# VOTO BRANCO = 95; VOTO NULO = 96; VOTO ANULADO NA APURACAO = 97
votos_estado = spark.sql("""
    SELECT SIGLA_UF
         , SUM(QTDE_VOTOS) AS TOTAL_VOTOS_UF
    FROM T_VOT10
    WHERE (    NUMERO_CANDIDATO != 95
           AND NUMERO_CANDIDATO != 96
           AND NUMERO_CANDIDATO != 97)
      AND (   DESCRICAO_CARGO = 'DEPUTADO ESTADUAL'
           OR DESCRICAO_CARGO = 'DEPUTADO DISTRITAL')
    GROUP BY SIGLA_UF
""")
votos_estado.createOrReplaceTempView("T_VE")

# join com a tabela up14
up14 = spark.sql("""
    SELECT A.*
         , A.VOTOS_ESTADUAL / FLOAT(B.TOTAL_VOTOS_UF) AS PERC_VOTOS_UF
    FROM T_UP      A
       , T_VE      B
    WHERE A.SIGLA_UF      = B.SIGLA_UF
""")
up14.createOrReplaceTempView("T_UP")

## calcular percentual eleitos em 2010 frente aa quantidade de candidatos por estado

# eleitos
eleitos_estado = spark.sql("""
    SELECT SIGLA_UF
         , COUNT(*) AS QTDE_ELEITOS
    FROM T_DE10
    WHERE DESC_SIT_TOT_TURNO = 'ELEITO'
       OR DESC_SIT_TOT_TURNO = 'ELEITO POR QP'
       OR DESC_SIT_TOT_TURNO = 'ELEITO POR MÉDIA'
       OR DESC_SIT_TOT_TURNO = 'MÉDIA'
       OR DESC_SIT_TOT_TURNO = 'QP'
    GROUP BY SIGLA_UF
""")
eleitos_estado.createOrReplaceTempView("T_EE")

# candidatos
candidatos_estado = spark.sql("""
   SELECT SIGLA_UF
        , COUNT(*) AS QTDE_CANDIDATOS
   FROM T_DE10
   GROUP BY SIGLA_UF
""")
candidatos_estado.createOrReplaceTempView("T_CE")

# join com a tabela up14
up14 = spark.sql("""
    SELECT A.*
         , B.QTDE_ELEITOS / FLOAT(C.QTDE_CANDIDATOS) AS PERC_ELEITOS_UF
    FROM T_UP      A
       , T_EE      B
       , T_CE      C
    WHERE A.SIGLA_UF = B.SIGLA_UF
      AND B.SIGLA_UF = C.SIGLA_UF
""")
up14.createOrReplaceTempView("T_UP")

## calcular o quociente eleitoral em 2010 no estado

# quociente eleitoral 2010
quociente = spark.sql("""
    SELECT A.SIGLA_UF
         , CAST(A.TOTAL_VOTOS_UF / FLOAT(B.QTDE_ELEITOS) AS INTEGER) AS QUOCIENTE_ELEITORAL
    FROM T_VE A
       , T_EE B
    WHERE A.SIGLA_UF = B.SIGLA_UF
""")
quociente.createOrReplaceTempView("T_QE")

# calcular o percentual de votos do candidato frente o quociente eleitoral em 2010
up14 = spark.sql("""
    SELECT A.*
         , A.VOTOS_ESTADUAL / FLOAT(B.QUOCIENTE_ELEITORAL) AS PERC_QE
    FROM T_UP      A
       , T_QE      B
    WHERE A.SIGLA_UF = B.SIGLA_UF
""")
up14.createOrReplaceTempView("T_UP")

## calcular o quociente eleitoral em 2014 no estado

# votos 2014
votos_estado = spark.sql("""
    SELECT SIGLA_UF
         , SUM(QTDE_VOTOS) AS TOTAL_VOTOS_UF
    FROM T_VOT14
    WHERE NUMERO_CANDIDATO != 95
      AND NUMERO_CANDIDATO != 96
      AND NUMERO_CANDIDATO != 97
      AND DESCRICAO_CARGO = 'DEPUTADO FEDERAL'
    GROUP BY SIGLA_UF
""")
votos_estado.createOrReplaceTempView("T_VE")

# eleitos 2014
eleitos_estado = spark.sql("""
    SELECT SIGLA_UF
         , COUNT(*) AS QTDE_ELEITOS
    FROM T_DF14
    WHERE DESC_SIT_TOT_TURNO = 'ELEITO'
       OR DESC_SIT_TOT_TURNO = 'ELEITO POR QP'
       OR DESC_SIT_TOT_TURNO = 'ELEITO POR MÉDIA'
       OR DESC_SIT_TOT_TURNO = 'QP'
       OR DESC_SIT_TOT_TURNO = 'MÉDIA'
    GROUP BY SIGLA_UF
""")
eleitos_estado.createOrReplaceTempView("T_EE")

# quociente eleitoral 2014
quociente = spark.sql("""
    SELECT A.SIGLA_UF
         , CAST(A.TOTAL_VOTOS_UF / FLOAT(B.QTDE_ELEITOS) AS INTEGER) AS QUOCIENTE_ELEITORAL
    FROM T_VE A
       , T_EE B
    WHERE A.SIGLA_UF = B.SIGLA_UF
""")
quociente.createOrReplaceTempView("T_QE")

# calcular o percentual de votos do candidato frente o quociente eleitoral em 2014
up14 = spark.sql("""
    SELECT A.*
         , A.VOTOS_FEDERAL / FLOAT(B.QUOCIENTE_ELEITORAL) AS TARGET
    FROM T_UP      A
       , T_QE      B
    WHERE A.SIGLA_UF = B.SIGLA_UF
""")
up14.createOrReplaceTempView("T_UP")

# salvar csv para criar regressao
df_up14 = up14.toPandas()
df_up14.to_csv('../data/capital_eleitoral_2014.csv', index=False, encoding='utf-8')

#### CRIAR MODELO DE REGRESSAO (gerado no Weka)

# 85% CORRELACAO
# TARGET = -0.0025 * IDADE_ESTADUAL + 0.9289 * PERC_QE + 0.116


#### PREPARAR UPGRADE DEPUTADO FEDERAL 2018

# recuperar candidatos a deputado estadual em 2014
de14 = spark.sql("""
    SELECT _c5  AS SIGLA_UF
         , _c8  AS CODIGO_CARGO
         , _c12 AS NUMERO_CANDIDATO
         , _c13 AS CPF_CANDIDATO
         , _c14 AS NOME_URNA_CANDIDATO
         , _c20 AS CODIGO_LEGENDA
         , _c25 AS DESCRICAO_OCUPACAO
         , _c28 AS IDADE_DATA_ELEICAO
         , _c30 AS DESCRICAO_SEXO
         , _c32 AS DESCRICAO_GRAU_INSTRUCAO
         , _c34 AS DESCRICAO_ESTADO_CIVIL
         , _c39 AS SIGLA_UF_NASCIMENTO
         , _c41 AS NOME_MUNICIPIO_NASCIMENTO
         , _c42 AS DESPESA_MAX_CAMPANHA
         , _c44 AS DESC_SIT_TOT_TURNO
    FROM T_CAND14
    WHERE _c9 = 'DEPUTADO ESTADUAL'
""")
de14.createOrReplaceTempView("T_DE14")

# efetua merge de votacoes e candidatos de 2014
de14 = spark.sql("""
    SELECT A.SIGLA_UF
         , A.CPF_CANDIDATO
         , A.NOME_URNA_CANDIDATO
         , A.CODIGO_LEGENDA
         , A.IDADE_DATA_ELEICAO
         , A.DESCRICAO_OCUPACAO
         , A.DESCRICAO_SEXO
         , A.DESCRICAO_GRAU_INSTRUCAO
         , A.DESCRICAO_ESTADO_CIVIL
         , A.SIGLA_UF_NASCIMENTO
         , A.NOME_MUNICIPIO_NASCIMENTO
         , A.DESPESA_MAX_CAMPANHA
         , A.DESC_SIT_TOT_TURNO
         , B.QTDE_VOTOS
    FROM T_DE14   A
       , T_VOT14  B
    WHERE A.SIGLA_UF         = B.SIGLA_UF
      AND A.CODIGO_CARGO     = B.CODIGO_CARGO
      AND A.NUMERO_CANDIDATO = B.NUMERO_CANDIDATO
""")
de14.createOrReplaceTempView("T_DE14")

# criar tabela up18

# identifica nos arquivos candidatos a estadual/distrital em 2010 que foram
# candidatos a deputado federal em 2014. Criar dataframe com esses candidatos.
up18 = spark.sql("""
    SELECT SIGLA_UF
         , NOME_URNA_CANDIDATO
         , IDADE_DATA_ELEICAO        AS IDADE_ESTADUAL
         , QTDE_VOTOS                AS VOTOS_ESTADUAL
    FROM T_DE14
""")
up18.createOrReplaceTempView("T_UP")

## incluir percentual de votos que o candidato obteve em 2010 em comparação ao total de votos do estado
votos_estado = spark.sql("""
    SELECT SIGLA_UF
         , SUM(QTDE_VOTOS) AS TOTAL_VOTOS_UF
    FROM T_VOT14
    WHERE (    NUMERO_CANDIDATO != 95
           AND NUMERO_CANDIDATO != 96
           AND NUMERO_CANDIDATO != 97)
      AND (   DESCRICAO_CARGO = 'DEPUTADO ESTADUAL'
           OR DESCRICAO_CARGO = 'DEPUTADO DISTRITAL')
    GROUP BY SIGLA_UF
""")
votos_estado.createOrReplaceTempView("T_VE")

# eleitos
eleitos_estado = spark.sql("""
    SELECT SIGLA_UF
         , COUNT(*) AS QTDE_ELEITOS
    FROM T_DE14
    WHERE DESC_SIT_TOT_TURNO = 'ELEITO'
       OR DESC_SIT_TOT_TURNO = 'ELEITO POR QP'
       OR DESC_SIT_TOT_TURNO = 'ELEITO POR MÉDIA'
    GROUP BY SIGLA_UF
""")
eleitos_estado.createOrReplaceTempView("T_EE")

# quociente eleitoral 2014
quociente = spark.sql("""
    SELECT A.SIGLA_UF
         , CAST(A.TOTAL_VOTOS_UF / FLOAT(B.QTDE_ELEITOS) AS INTEGER) AS QUOCIENTE_ELEITORAL
    FROM T_VE A
       , T_EE B
    WHERE A.SIGLA_UF = B.SIGLA_UF
""")
quociente.createOrReplaceTempView("T_QE")

# calcular o percentual de votos do candidato frente o quociente eleitoral em 2014
up18 = spark.sql("""
    SELECT A.*
         , A.VOTOS_ESTADUAL / FLOAT(B.QUOCIENTE_ELEITORAL) AS PERC_QE
    FROM T_UP      A
       , T_QE      B
    WHERE A.SIGLA_UF = B.SIGLA_UF
""")
up18.createOrReplaceTempView("T_UP")

# montar saida
up18 = spark.sql("""
    SELECT SIGLA_UF
         , NOME_URNA_CANDIDATO
         , (-0.0025 * IDADE_ESTADUAL + 0.9289 * PERC_QE + 0.116 ) AS TARGET
    FROM T_UP
""")
up18.createOrReplaceTempView("T_UP")

# retirar negativos
up18 = spark.sql("""
    SELECT SIGLA_UF
         , NOME_URNA_CANDIDATO
         , CASE WHEN TARGET < 0
               THEN 0
               ELSE TARGET
           END AS TARGET
    FROM T_UP
""")
up18.createOrReplaceTempView("T_UP")

# salvar csv para usar na pagina.
up18.toPandas().to_csv('../data/capital_eleitoral_2018.csv', index=False, encoding='utf-8')
