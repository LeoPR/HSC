# 02. Curvas de Preenchimento de Espaco

## Visao geral

Curvas de preenchimento (Hilbert, Z-order/Morton, Peano etc.) convertem coordenadas multidimensionais em uma ordem linear, tentando manter proximidade espacial.

## Hilbert vs Z-order (Morton)

### Hilbert

- Melhor preservacao de localidade em geral.
- Custo de calculo de indice costuma ser maior.
- Boa opcao quando qualidade de agrupamento local e mais importante que simplicidade.

### Z-order (Morton)

- Muito simples e rapido (intercalacao de bits).
- Excelente para implementacoes de alto desempenho e indexacao.
- Em alguns cenarios perde para Hilbert em localidade fina, mas pode ganhar em custo computacional total.

## Uso em compressao

- Reordenar pixels/voxels/tiles por curva espacial pode aumentar sequencias repetidas.
- Frequentemente combinado com RLE, delta, BWT-like block transforms, ou codificacao de entropia.

## Regra pratica

1. Prototipe com Z-order primeiro (mais simples).
2. Compare com Hilbert em taxa e tempo.
3. Se ganho de taxa com Hilbert compensar custo, migre.
