# 04. Reordenacao: BWT, MTF, RLE

## Ideia central

Essas tecnicas nao "comprimem sozinhas" no sentido final de bits. Elas reorganizam dados para que codificadores entrópicos trabalhem melhor.

## BWT (Burrows-Wheeler Transform)

- Reordena blocos de texto/dados para agrupar simbolos parecidos.
- Aumenta ocorrencia de runs, preparando para RLE/MTF/entropia.
- Reversivel (lossless).

## MTF (Move-to-Front)

- Converte simbolos recorrentes em numeros pequenos repetidos.
- Funciona muito bem depois de BWT.

## RLE

- Codifica sequencias repetidas como (valor, comprimento).
- Simples e eficaz quando ha runs longos.

## Conexao com Hilbert

Uma estrategia promissora para dados 2D/3D:

1. varredura por Hilbert,
2. opcionalmente bloco + BWT,
3. MTF/RLE,
4. codificacao entrópica.

Assim, Hilbert atua como reordenacao espacial; BWT/MTF/RLE atuam como reordenacao simbolica.
