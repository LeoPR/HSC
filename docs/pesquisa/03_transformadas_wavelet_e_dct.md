# 03. Transformadas: Wavelet e DCT

## Logica global

Transform coding separa o sinal em componentes para concentrar energia/informacao em poucos coeficientes relevantes. Depois aplica quantizacao (lossy) e codificacao entropica.

Pipeline tipico:

1. Transformada (DCT ou DWT/Wavelet)
2. Quantizacao (opcional em lossless, essencial em lossy)
3. Entropia (Huffman, aritmetica, ANS)

## Wavelet (DWT)

- Forte em multirresolucao e detalhes localizados.
- Base matematica em espacos de Hilbert (bases ortonormais em L2) para varias construcoes classicas.
- Muito usada em imagem (ex.: JPEG 2000).

## DCT

- Muito consolidada em imagem/video tradicional.
- Excelente custo-beneficio de implementacao, hardware e padroes.

## Relevancia para sua ideia

Se a motivacao for "espaco de Hilbert" no sentido funcional (L2/bases ortonormais), wavelets sao o caminho mais direto e teoricamente estabelecido para compressao.
