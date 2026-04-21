# Space-Filling Curves e Compressão

## Contexto

Curvas de preenchimento de espaço (Hilbert, Z-order/Morton, Peano, Gosper, Moore, Sierpinski etc.) convertem coordenadas multidimensionais em uma ordem linear preservando, em diferentes graus, a proximidade espacial. Em compressão são aplicáveis como etapa de reordenação antes de codificadores entrópicos.

## Hilbert

- Mapeia dados 2D/3D/nD para 1D preservando localidade com qualidade empiricamente superior a varreduras raster em muitos cenários.
- Pontos vizinhos no espaço tendem a ficar próximos na sequência linear.
- Facilita técnicas que dependem de repetição local: delta coding, RLE, MTF, modelos de contexto e codificação entrópica.
- Custo de cálculo de índice é O(log² N) — maior que Morton.
- Indicado quando a qualidade de agrupamento local compensa o custo computacional.

## Z-order / Morton

- Índice obtido por intercalação de bits das coordenadas.
- O(1) por índice — ordens de magnitude mais rápido que Hilbert.
- Excelente para indexação espacial e implementações de alto desempenho.
- Perde para Hilbert em localidade fina em alguns cenários, mas pode compensar pelo custo total.

## Onde aparece na literatura e prática

- Indexação espacial e bancos multidimensionais (explorando localidade).
- Compressão e aceleração de estruturas de índice (ex. variantes Hilbert R-tree).
- "Hilbert Space Compression Architecture" em data warehouses (reorganização para reduzir redundância de armazenamento e indexação).
- Tiling de imagens e texturas em GPUs e formatos gráficos.

## Limites

- Curvas espaciais não geram compressão forte sozinhas — apenas rearranjam. A redução efetiva de bits vem da codificação posterior.
- O ganho depende do tipo de dado:
  - imagens, texturas, grades espaciais e volumes beneficiam-se mais;
  - dados já aleatórios ou pouco correlacionados espacialmente ganham pouco;
  - texto sequencial tende a ser prejudicado (a ordem natural já maximiza contexto local).

## Heurística de uso

1. Se os dados têm correlação espacial 2D/3D, prototipar com Z-order primeiro (implementação simples).
2. Comparar com Hilbert em taxa e tempo.
3. Se Hilbert compensar o custo, migrar.
4. Combinar com: predição delta local, transformação de agrupamento (opcional), codificação entrópica (Huffman/aritmética/ANS).

## Referências iniciais

- Hilbert curve — https://en.wikipedia.org/wiki/Hilbert_curve
- Z-order / Morton — https://en.wikipedia.org/wiki/Z-order_curve
- Sagan, H. (1994). *Space-Filling Curves*. Springer.
- Bader, M. (2013). *Space-Filling Curves: An Introduction with Applications in Scientific Computing*. Springer.
- Mokbel et al. (2003). Analysis of multi-dimensional space-filling curves. *GeoInformatica* 7(3).
