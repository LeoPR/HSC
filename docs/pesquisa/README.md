# Pesquisa: Compressao e Espacos/Curvas de Hilbert

Este diretorio consolida uma pesquisa tecnica para avaliar a ideia de um compressor inspirado em espacos/curvas de Hilbert e comparar com familias classicas de compressao.

## Resumo rapido

- Existe base tecnica para usar ordenacao por curva de Hilbert como etapa de preprocessamento/reordenacao para melhorar localidade espacial e criar sequencias 1D mais compressiveis.
- Em geral, a curva de Hilbert nao substitui, sozinha, o compressor final; ela tende a funcionar melhor em pipeline com transformacoes e codificacao entropica.
- Tecnicas de referencia para comparar: BWT+MTF+RLE+Huffman/aritmetica, DWT/DCT+quantizacao+entropia, LZ, codificacao entropica (Huffman/aritmetica/ANS), e metodos fractais.

## Arquivos

- 01_hilbert_e_compressao.md
- 02_curvas_preenchimento_de_espaco.md
- 03_transformadas_wavelet_e_dct.md
- 04_reordenacao_bwt_mtf_rle.md
- 05_codificacao_entropica.md
- 06_compressao_fractal.md
- 07_logicas_globais_de_projeto.md
- 08_ideias_de_pipeline_hibrido.md
- 09_siac-mapa-pesquisa.md
- **10_transformacoes_de_espaco_para_compressao.md** — Taxonomia completa: 6 perspectivas sobre transformação de feature space para compressão (SFC, mudança de base, adaptação iterativa, vocabulário, embedding nD, multi-perspectiva)
- **11_compressao_funcional_topologica.md** — Framework unificado: compressão como homeomorfismo φ: C → D; topologia persistente, álgebra fuzzy, INR/SIREN, autopoiese, independência de substrato (binário/analógico/quântico)
- **12_roadmap_experimentos.md** — Plano de execução: 4 sprints, critérios go/no-go, estrutura do paper, escopo controlado

## Referencias de partida (pesquisa)

- Hilbert curve: https://en.wikipedia.org/wiki/Hilbert_curve
- Z-order (Morton): https://en.wikipedia.org/wiki/Z-order_curve
- Wavelet transform/compression: https://en.wikipedia.org/wiki/Wavelet_transform
- Burrows-Wheeler transform: https://en.wikipedia.org/wiki/Burrows%E2%80%93Wheeler_transform
- Arithmetic coding: https://en.wikipedia.org/wiki/Arithmetic_coding
- Fractal compression: https://en.wikipedia.org/wiki/Fractal_compression

Observacao: algumas referencias acima sao paginas de visao geral. Para implementacao e avaliacao comparativa, convem complementar com artigos e benchmarks especificos do seu dominio de dados.
