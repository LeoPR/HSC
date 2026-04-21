# 01. Hilbert e Compressao

## Pergunta central

"Dá para fazer compressor usando espacos/curva de Hilbert?"

Resposta curta: sim, principalmente como estrategia de reordenacao de dados multidimensionais para aumentar localidade e redundancia local antes da compressao principal.

## O que a curva de Hilbert oferece

- Mapeia dados de 2D/3D/... para 1D preservando localidade melhor que varreduras ingênuas (ex.: linha a linha), em muitos cenarios.
- Pontos vizinhos no espaco tendem a ficar proximos na sequencia linear.
- Isso facilita tecnicas que dependem de repeticao local: delta coding, RLE, MTF, modelos de contexto, e codificacao entropica.

## Onde isso aparece na literatura/pratica

- Indexacao espacial e bancos multidimensionais (propriedade de localidade).
- Compressao/aceleracao de estruturas de indice (ex.: variantes tipo Hilbert R-tree).
- Trabalhos de "Hilbert Space Compression Architecture" para data warehouse (enfoque em reorganizacao para reduzir redundancia de armazenamento/indexacao).

## Limites importantes

- A curva de Hilbert nao gera compressao forte sozinha. Ela rearranja; quem efetivamente reduz bits e a etapa de codificacao posterior.
- Ganho depende muito do tipo de dado:
- imagens/texturas/grades espaciais costumam se beneficiar mais;
- dados ja aleatorios ou pouco correlacionados espacialmente ganham pouco.

## Heuristica de projeto

Use Hilbert como "front-end de linearizacao" em dados espaciais e combine com:

1. predicao/delta local,
2. transformacoes de agrupamento (opcional),
3. codificacao entropica (Huffman/aritmetica/ANS).
