# 08. Ideias de Pipeline Hibrido

## Objetivo

Traduzir a ideia de "compressor com Hilbert" para experimentos concretos.

## Pipeline A (lossless simples)

1. Entrada 2D/3D em blocos
2. Linearizacao por Hilbert (ou Morton como baseline)
3. Delta entre amostras adjacentes na ordem da curva
4. RLE de zeros/repeticoes
5. Codificacao entrópica (Huffman ou aritmetica)

## Pipeline B (lossless com reordenacao de simbolos)

1. Bloco -> Hilbert scan
2. BWT por bloco
3. MTF
4. RLE
5. Entropia

## Pipeline C (lossy para imagem)

1. Blocos por Hilbert para melhorar cache/localidade
2. Transformada (DWT ou DCT)
3. Quantizacao controlada por taxa-distorcao
4. Entropia

## Protocolo de avaliacao recomendado

Comparar sempre contra baselines:

1. Varredura raster + mesmo backend
2. Morton + mesmo backend
3. Hilbert + backend

Metricas:

1. Taxa de compressao
2. Velocidade encode/decode
3. Uso de memoria
4. Em lossy: PSNR/SSIM ou metrica perceptual do dominio

## Hipotese tecnica

Se seus dados tiverem alta correlacao espacial local, Hilbert tende a reduzir entropia condicional local da sequencia linearizada e facilitar as etapas seguintes.
