# 06. Compressao Fractal

## Logica

Modela auto-similaridade da imagem por sistemas iterados de funcoes (IFS/PIFS), armazenando transformacoes ao inves de pixels diretamente.

## Pontos fortes

- Pode ter boa qualidade em algumas classes de imagem em altas taxas de compressao.
- Decodificacao pode ser rapida em certos esquemas.
- Traz ideia de "codigo generativo" da imagem.

## Pontos fracos

- Codificacao historicamente cara (busca por blocos auto-semelhantes e otimização).
- Complexidade maior que pipelines classicos em muitos cenarios.
- Adoção industrial ampla limitada em comparacao com DCT/DWT + entropia.

## Relacao com Hilbert

Sao ideias diferentes, mas ambas exploram estrutura espacial. Uma combinacao possivel e usar ordenacao espacial (Hilbert/Morton) para acelerar buscas locais em variantes fractais ou para pre-clustering de blocos.
