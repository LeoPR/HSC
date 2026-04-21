# 07. Logicas Globais de Projeto

## 1) Redundancia estatistica

Explorar distribuicoes desbalanceadas de simbolos.

- Ferramentas: Huffman, aritmetica, ANS.

## 2) Redundancia estrutural/local

Explorar repeticoes locais no espaco/tempo.

- Ferramentas: Hilbert/Morton scan, delta, RLE, LZ.

## 3) Redundancia por transformacao

Levar informacao para dominio onde poucos coeficientes concentram energia.

- Ferramentas: DCT, DWT/wavelets, outras transformadas.

## 4) Predicao/modelagem

Modelar proximo simbolo a partir de contexto.

- Ferramentas: modelos de contexto, PPM-like, predicao linear, filtros adaptativos.

## 5) Taxa-distorcao (quando lossy)

Controlar compromisso entre tamanho e fidelidade.

- Ferramentas: quantizacao, alocacao de bits, metricas perceptuais.

## Regra de ouro

Compressores de alto desempenho sao quase sempre hibridos: combinam varias logicas em pipeline.
