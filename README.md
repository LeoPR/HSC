# HSC — Hilbert Space Compression

Projeto guarda-chuva de pesquisa em compressão de dados vista como problema de espaço
topológico: encontrar o espaço de representação onde os dados são simples, descrever
esse espaço e a função que o mapeia de volta ao original.

O projeto abriga literatura, infraestrutura de benchmark e múltiplas técnicas experimentais
independentes. Cada técnica evolui na sua própria subpasta em `techniques/` e pode,
a qualquer momento, tornar-se um projeto autônomo.

## Estrutura

```
HSC/
├── docs/pesquisa/      # notas e literatura de base do projeto
├── datasets/           # corpora canônicos compartilhados (Calgary, Canterbury, Silesia)
├── evaluations/        # sistema de Q&A científico — perguntas abertas e respondidas
├── prototype/          # infraestrutura de benchmark compartilhada
├── results/            # saídas de benchmarks
├── tools/              # utilitários (download de datasets, etc.)
└── techniques/         # técnicas experimentais — cada uma tem README e andamento próprios
```

## Técnicas

Cada subpasta em `techniques/` é autônoma. Consulte o `README.md` de cada uma.

## Documentação de base

`docs/pesquisa/` — cobre curvas de preenchimento de espaço, wavelets/DCT, BWT/MTF/RLE,
codificação entrópica, compressão fractal, transformações de espaço de features e
compressão funcional topológica.

`evaluations/` — histórico de decisões científicas no formato Q&A (perguntas abertas
e respondidas com evidências).
