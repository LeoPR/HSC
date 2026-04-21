# HSC — Hilbert Space Compression

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Projeto guarda-chuva de pesquisa em compressão de dados vista como problema de **espaço topológico**: encontrar o espaço de representação em que os dados são simples, descrever esse espaço e a função que o mapeia de volta ao original.

O nome "Hilbert Space" refere-se simultaneamente (a) às curvas de preenchimento de espaço (ponto de partida histórico) e (b) ao conceito matemático de espaço de Hilbert como espaço vetorial com produto interno — o enquadramento mais geral para o qual o projeto gravita.

## O que é e o que não é

- **É** um repositório de pesquisa: ideias teóricas, experimentos, avaliações formais.
- **É** uma coleção de técnicas experimentais independentes, cada uma com seu próprio ciclo de vida.
- **Não é** um compressor pronto para produção. Ainda.

Cada técnica em `techniques/` pode, a qualquer momento, tornar-se um projeto autônomo.

## Estrutura

```
HSC/
├── docs/                  documentação (literature, framework, methodology)
│   ├── literature/        base bibliográfica — estado da arte
│   ├── framework/         visão teórica do projeto
│   └── methodology/       processo de pesquisa (SIAC, roadmap)
├── evaluations/           sistema de Q&A científico (open/ e answered/)
├── datasets/              corpora canônicos (Calgary, Canterbury, Silesia)
├── prototype/             infraestrutura de benchmark compartilhada
├── tools/                 utilitários (download de datasets, etc.)
├── techniques/            técnicas experimentais autônomas
│   └── TBC/               TuringBitCompression
└── results/               saídas de benchmarks
```

## Começando

1. Leitura conceitual: [`docs/README.md`](docs/README.md) aponta os três eixos (literatura, framework, metodologia).
2. Plano de pesquisa: [`docs/methodology/roadmap.md`](docs/methodology/roadmap.md) traz sprints e critérios.
3. Perguntas abertas: [`evaluations/open/`](evaluations/open/).
4. Técnicas concretas: cada [`techniques/<nome>/README.md`](techniques/) tem seu próprio uso.

### Executar benchmarks existentes

```bash
python tools/download_datasets.py download   # baixar corpora canônicos
python prototype/run_benchmark.py --only-priority --csv results/benchmark.csv
```

Ver [`tools/download_datasets.py`](tools/download_datasets.py) e [`prototype/run_benchmark.py`](prototype/run_benchmark.py).

## Técnicas

| Técnica | Ideia | Estado |
|---------|-------|--------|
| [TBC](techniques/TBC/) | TuringBitCompression — codificação por planos indicadores ordenados por frequência | Protótipo Python com round-trip validado |

## Licença

[MIT](LICENSE).

## Autor

Leonardo Marques de Souza
