# limpar variaveis
rm(list = ls())

# INFORMAR LOCAL DO ARQUIVO DO DATASET ORIGINAL DO TSE

uf <- read.csv("~/election_mining/data/votacao_candidato_munzona_2014_SP.txt", 
               header=FALSE, 
               sep=";",
               fileEncoding = "Latin1",
               stringsAsFactors = TRUE,
               colClasses = "character")

# INFORMAR QUAL O CARGO PESQUISADO. O objeto desta pesquisa ? o cargo de Deputado Federal

CARGO <- 'DEPUTADO FEDERAL'

# checar quantidades das variaveis
unique(uf$V1)
unique(uf$V2)
unique(uf$V3)
unique(uf$V4)
unique(uf$V5)
unique(uf$V6)
unique(uf$V7)

# eliminar variaveis desnecessarias para o estudo
uf_novo <- uf[,c(9, 10, 13, 15, 16, 22, 24, 27, 29)]

# dar nomes aas colunas
names(uf_novo) <- c('NOME_MUNICIPIO', 'NUMERO_ZONA', 'SQ_CANDIDATO', 
                    'NOME_URNA_CANDIDATO', 'DESCRICAO_CARGO', 'DESC_SIT_CAND_TOT',
                    'SIGLA_PARTIDO', 'NOME_COLIGACAO', 'TOTAL_VOTOS')

## criar arquivo para cluster

# campos iniciais
eleitos <- uf_novo[uf_novo$DESCRICAO_CARGO == CARGO & 
                      (uf_novo$DESC_SIT_CAND_TOT != 'NÃO ELEITO' & uf_novo$DESC_SIT_CAND_TOT != 'SUPLENTE'),]
                     # (uf_novo$DESC_SIT_CAND_TOT == 'NÃO ELEITO' | uf_novo$DESC_SIT_CAND_TOT == 'SUPLENTE'),]                     

# manter somente codigo do candidato, nome, e tipo situacao eleicao
eleitos <- eleitos[,c(3, 4, 6)]

# retirar campos repetidos
eleitos <- unique(eleitos)

# criar campo com votacao total
vt <- aggregate(x=as.numeric(uf_novo$TOTAL_VOTOS), by=list(SQ_CANDIDATO = uf_novo$SQ_CANDIDATO), FUN=sum)

# jogar total para eleitos
eleitos <- merge(eleitos, vt, all.x = TRUE)
names(eleitos)[4] <- 'TOTAL_VOTOS_SOMADOS'

# votacoes por municipio
vzona <- aggregate(x=as.numeric(uf_novo$TOTAL_VOTOS), 
                   by=list(NOME_MUNICIPIO = uf_novo$NOME_MUNICIPIO, 
                           NUMERO_ZONA = uf_novo$NUMERO_ZONA, 
                           SQ_CANDIDATO = uf_novo$SQ_CANDIDATO), 
                   FUN=sum)

# media, eliminando zonas com votacao zero.
vzona_n_zero <- vzona[vzona$x != 0,]
media_n_zero <- aggregate(x=vzona_n_zero$x, by=list(SQ_CANDIDATO = vzona_n_zero$SQ_CANDIDATO), FUN=mean)
eleitos <- merge(eleitos, media_n_zero, all.x = TRUE)
names(eleitos)[5] <- 'MEDIA_NAO_ZEROS'
eleitos$MEDIA_NAO_ZEROS <- trunc(eleitos$MEDIA_NAO_ZEROS)

# percentual municipios/zonas zerados por eleitor
qt_zona <- nrow(unique(vzona[,c(1, 2)]))

vzona_zero <- vzona[vzona$x == 0,]
conta_zero <- aggregate(x=vzona_zero$x, by=list(SQ_CANDIDATO = vzona_zero$SQ_CANDIDATO), FUN=length)
conta_zero$percentual <- conta_zero$x / qt_zona  
conta_zero$x <- NULL
eleitos <- merge(eleitos, conta_zero, all.x = TRUE)
names(eleitos)[6] <- 'PERCENTUAL_ZONAS_ZERADAS'
eleitos$PERCENTUAL_ZONAS_ZERADAS[is.na(eleitos$PERCENTUAL_ZONAS_ZERADAS)] <- 0

# colocacao media
vzona_n_zero <- vzona_n_zero[order(vzona_n_zero$NOME_MUNICIPIO, vzona_n_zero$NUMERO_ZONA, vzona_n_zero$x, decreasing = TRUE),]
vzona_n_zero$colocacao <- 0

c = 0
gda_x = 0
gda_zona = vzona_n_zero$NUMERO_ZONA[1]
gda_municipio = vzona_n_zero$NOME_MUNICIPIO[1]
for (i in 1:nrow(vzona_n_zero)) {
  if (gda_zona != vzona_n_zero$NUMERO_ZONA[i] | gda_municipio != vzona_n_zero$NOME_MUNICIPIO[i]) {
    c = 1
    gda_x = 0
    gda_zona = vzona_n_zero$NUMERO_ZONA[i]
    gda_municipio = vzona_n_zero$NOME_MUNICIPIO[i]
  } else {
    if (gda_x != vzona_n_zero$x[i]) {
      c = c + 1
      gda_x = vzona_n_zero$x[i]
    }
  }
  vzona_n_zero$colocacao[i] <- c

#  cat("\014")
#  print(100 * i/nrow(vzona_n_zero))
}

media_colocacao <- aggregate(x=vzona_n_zero$colocacao, 
                             by=list(SQ_CANDIDATO = vzona_n_zero$SQ_CANDIDATO), FUN=mean)

eleitos <- merge(eleitos, media_colocacao, all.x = TRUE)
names(eleitos)[7] <- 'MEDIA_COLOCACAO'
eleitos$MEDIA_COLOCACAO <- trunc(eleitos$MEDIA_COLOCACAO)

# desvio-padrao COLOCACAO
temp <- aggregate(x = vzona_n_zero$colocacao, 
                  by = list(SQ_CANDIDATO = vzona_n_zero$SQ_CANDIDATO), 
                  FUN=sd)
names(temp)[2] <- 'DESVIO_PADRAO_COLOCACAO'
temp$DESVIO_PADRAO_COLOCACAO <- trunc(temp$DESVIO_PADRAO_COLOCACAO)
eleitos <- merge(eleitos, temp, all.x = TRUE)

# coeficiente de variacao da coloca??o
eleitos$COEFICIENTE_VARIACAO_COLOCACAO <- eleitos$DESVIO_PADRAO_COLOCACAO / eleitos$MEDIA_COLOCACAO

# centil
vzona_eleitos <- vzona[vzona$SQ_CANDIDATO %in% eleitos$SQ_CANDIDATO,]
vzona_eleitos <- vzona_eleitos[order(vzona_eleitos$SQ_CANDIDATO, vzona_eleitos$x, decreasing = TRUE),]

# o quanto um municipio corresponde a quantidade total de zonas eleitorais
cte_mun_zona <- 100 / nrow(unique(vzona[,c(1,2)])) 

# criar coluna acumulada
vzona_eleitos$acm_voto <- 0
vzona_eleitos$acm_zona <- 0
gda_candidato = vzona_eleitos$SQ_CANDIDATO[1]
acm_voto = 0
acm_zona = 0
for (i in 1:nrow(vzona_eleitos)) {
  if  (gda_candidato == vzona_eleitos$SQ_CANDIDATO[i]) {
    acm_voto <- acm_voto + vzona_eleitos$x[i] 
    acm_zona <- acm_zona + cte_mun_zona
  } else {
    acm_voto <- vzona_eleitos$x[i]
    acm_zona <- cte_mun_zona
    gda_candidato <- vzona_eleitos$SQ_CANDIDATO[i]
  }
  vzona_eleitos$acm_zona[i] <- acm_zona 
  vzona_eleitos$acm_voto[i] <- acm_voto
}

# recuperando votos totais
vzona_eleitos <- merge(vzona_eleitos, eleitos[,c(1,4)], all.x = TRUE)

# calcular percentuais
vzona_eleitos$PERCENTUAL <- vzona_eleitos$acm_voto / vzona_eleitos$TOTAL_VOTOS_SOMADOS

# criar centil
temp <- vzona_eleitos[vzona_eleitos$acm_zona >= 1,]
centil <- aggregate(x = temp$PERCENTUAL, by = list(SQ_CANDIDATO = temp$SQ_CANDIDATO), FUN=min)
names(centil)[2] <- 'centil'
eleitos <- merge(eleitos, centil, all.x = TRUE)

# criar vintil
temp <- vzona_eleitos[vzona_eleitos$acm_zona >= 5,]
vintil <- aggregate(x = temp$PERCENTUAL, by = list(SQ_CANDIDATO = temp$SQ_CANDIDATO), FUN=min)
names(vintil)[2] <- 'vintil'
eleitos <- merge(eleitos, vintil, all.x = TRUE)

# criar decil
temp <- vzona_eleitos[vzona_eleitos$acm_zona >= 10,]
decil <- aggregate(x = temp$PERCENTUAL, by = list(SQ_CANDIDATO = temp$SQ_CANDIDATO), FUN=min)
names(decil)[2] <- 'decil'
eleitos <- merge(eleitos, decil, all.x = TRUE)

# criar quintil
temp <- vzona_eleitos[vzona_eleitos$acm_zona >= 20,]
quintil <- aggregate(x = temp$PERCENTUAL, by = list(SQ_CANDIDATO = temp$SQ_CANDIDATO), FUN=min)
names(quintil)[2] <- 'quintil'
eleitos <- merge(eleitos, quintil, all.x = TRUE)

# media entre zonas eleitorais
temp <- aggregate(x = vzona_eleitos$x, 
                  by = list(SQ_CANDIDATO = vzona_eleitos$SQ_CANDIDATO), 
                  FUN=mean)
names(temp)[2] <- 'MEDIA_VOTOS_ZONA'
temp$MEDIA_VOTOS_ZONA <- trunc(temp$MEDIA_VOTOS_ZONA)
eleitos <- merge(eleitos, temp, all.x = TRUE)

# desvio-padrao entre zonas eleitorais
temp <- aggregate(x = vzona_eleitos$x, 
                by = list(SQ_CANDIDATO = vzona_eleitos$SQ_CANDIDATO), 
                FUN=sd)
names(temp)[2] <- 'DESVIO_PADRAO_ZONA'
temp$DESVIO_PADRAO_ZONA <- trunc(temp$DESVIO_PADRAO_ZONA)
eleitos <- merge(eleitos, temp, all.x = TRUE)

# coeficiente de variacao
eleitos$COEFICIENTE_VARIACAO <- eleitos$DESVIO_PADRAO_ZONA / eleitos$MEDIA_VOTOS_ZONA
eleitos$COEFICIENTE_VARIACAO[is.infinite(eleitos$COEFICIENTE_VARIACAO)] <- 0

## selecionar atributos
par(xpd=FALSE) # this is usually the default
plot(eleitos$centil, xlab = "Eleitos", ylab = "Percentis",type = "l", col = "black", main = "Comparação entre Percentis", bty="L")
lines(eleitos$decil, col= "red")
lines(eleitos$vintil, col= "blue")
lines(eleitos$quintil, col= "green")
par(xpd=TRUE)
legend(-15, 0, legend=c("centil", "decil", "vintil", "quintil"), 
                    fill=c("black", "red", "blue", "green"), bty="n")

## NORMALIZA A PLANILHA ELEITOS

eleitos_normalizado <- eleitos
eleitos_normalizado[is.na(eleitos_normalizado)] <- 0

z <- max(eleitos_normalizado$TOTAL_VOTOS_SOMADOS)
if (z > 0) {
  eleitos_normalizado$TOTAL_VOTOS_SOMADOS <- eleitos_normalizado$TOTAL_VOTOS_SOMADOS/z}

z <- max(eleitos_normalizado$MEDIA_NAO_ZEROS)
if (z > 0) {
  eleitos_normalizado$MEDIA_NAO_ZEROS <- eleitos_normalizado$MEDIA_NAO_ZEROS/z}

z <- max(eleitos_normalizado$PERCENTUAL_ZONAS_ZERADAS)
if (z > 0) {
  eleitos_normalizado$PERCENTUAL_ZONAS_ZERADAS <- eleitos_normalizado$PERCENTUAL_ZONAS_ZERADAS/z}

z <- max(eleitos_normalizado$MEDIA_COLOCACAO)
if (z > 0) {
    eleitos_normalizado$MEDIA_COLOCACAO <- eleitos_normalizado$MEDIA_COLOCACAO/z}
  
z <- max(eleitos_normalizado$DESVIO_PADRAO_COLOCACAO)
if (z > 0) {
  eleitos_normalizado$DESVIO_PADRAO_COLOCACAO <- eleitos_normalizado$DESVIO_PADRAO_COLOCACAO/z}

z <- max(eleitos_normalizado$COEFICIENTE_VARIACAO_COLOCACAO)
if (z > 0) {
  eleitos_normalizado$COEFICIENTE_VARIACAO_COLOCACAO <- eleitos_normalizado$COEFICIENTE_VARIACAO_COLOCACAO/z}

z <- max(eleitos_normalizado$MEDIA_VOTOS_ZONA)
if (z > 0) {
  eleitos_normalizado$MEDIA_VOTOS_ZONA <- eleitos_normalizado$MEDIA_VOTOS_ZONA/z}

z <- max(eleitos_normalizado$DESVIO_PADRAO_ZONA)
if (z > 0) {
  eleitos_normalizado$DESVIO_PADRAO_ZONA <- eleitos_normalizado$DESVIO_PADRAO_ZONA/z}

z <- max(eleitos_normalizado$COEFICIENTE_VARIACAO)
if (z > 0) {
  eleitos_normalizado$COEFICIENTE_VARIACAO <- eleitos_normalizado$COEFICIENTE_VARIACAO/z}

## RODAR HCLUSTER

tb = eleitos_normalizado
d = dist(tb[4:16])

hc = hclust (d)
plot(hc, labels=as.character(eleitos$NOME_URNA_CANDIDATO), cex=0.7)
rec <- rect.hclust(hc, 3, border = 2:2)

grupo <- cutree(hc, k=3)

classificacao <- cbind(tb, grupo)
aggregate(x = classificacao$CENTIL, by=list(classificacao$grupo), FUN=max)
#   Group.1         x
# 1       1 0.6677949
# 2       2 0.3092579
# 3       3 0.9635287

write.table(cbind(tb, grupo) , file='~/election_mining/data/h_cluster.csv', sep=',', row.names=F)

## RODAR K-MEANS
mydata <- tb[4:16]
wss <- (nrow(mydata)-1)*sum(apply(mydata,2,var))
for (i in 2:15) wss[i] <- sum(kmeans(mydata, centers=i)$withinss)
plot(1:15, wss, type="b", xlab="Number of Clusters",
     ylab="Within groups sum of squares")

km <- kmeans(x=tb[4:15], centers=3, iter.max=10, nstart=10, algorithm="Hartigan-Wong", trace=TRUE)

write.table(cbind(tb, km$cluster), file='~/election_mining/data/clusterizado.csv', sep=',', row.names=F)
