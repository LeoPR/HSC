# TBC v1 — Aplicação Recursiva (estudo do processo)

> **Premissa.** Header e metadados fingidos como grátis. Medimos apenas bits de plano. O foco é entender como o processo se comporta quando aplicado sobre si mesmo — não tirar conclusões de qualidade.

---

## Pergunta

Aplicar v1 sucessivamente aos próprios planos, até que o tamanho pare de diminuir. A cada passagem, a distribuição dos dibits nos planos **muda** em relação ao nível anterior — então o ranking pode mudar também. Queremos observar:

1. Quantos níveis reduzem o tamanho antes de estabilizar?
2. O ranking muda entre níveis? Em que momento ele vira um **ponto fixo**?
3. Em algum ponto o mesmo ranking passa a valer para várias passadas consecutivas? Quando?

---

## Plano experimental

### Operação por nível

```
entrada N₀ = bits originais
para cada nível L = 1, 2, 3, ...:
    dibits_L   = bits_to_dibits(entrada_L)
    ranking_L  = ranking_por_frequencia(dibits_L)     # recalcula a cada nível
    planes_L   = build_planes(dibits_L, ranking_L)
    saida_L    = concat(planes_L)                     # lista bits dos planos como nova sequência
    registra   (ranking_L, plane_sizes_L, total_bits_L)
    se total_bits_L >= len(entrada_L):
        para (estabilizou)
    senao:
        entrada_{L+1} = saida_L
```

### Concatenação dos planos

Escolha: **(a) concatenar todos os planos em ordem** (L₁ ∘ L₂ ∘ … ∘ L_{m−1}).

Outras escolhas possíveis (fora de escopo agora): (b) recursar só no plano mais longo; (c) recursar em cada plano como árvore.

A opção (a) é a mais simples e preserva a identidade "compressão é entrada". É a que vamos usar.

### Critério de parada

Para quando `total_plane_bits(nível L+1) >= total_bits_atual`. Significa que mais uma aplicação não reduz.

### Round-trip

A descompressão reverte nível por nível, em ordem inversa, usando `(ranking, plane_sizes)` de cada nível como metadado. Round-trip exato exigido em cada execução.

### O que medir por execução

| Variável | Significado |
|----------|-------------|
| `nivel` | 0 = input; 1..L = passadas do processo |
| `ranking` | permutação dos 4 dibits por frequência naquele nível |
| `plane_sizes` | lista dos tamanhos \|P_i\| |
| `total_plane_bits` | soma dos tamanhos dos planos |
| `delta` | `total_plane_bits(L)` − `len(entrada_L)` |
| `ratio_acumulado` | `total_plane_bits(L)` / `len(entrada_0)` |
| `ranking_estabilizou` | boolean: ranking(L) == ranking(L−1)? |

### Distribuições a testar

Reuso as mesmas 5 da v1_demo.py:

- desbalanceado 75-8-8-8
- homogêneo 25-25-25-25
- um ausente (00 = 0%)
- bimodal 40-40-10-10
- extremo (1 dominante 95%)

### Tamanhos a testar

`N_dibits ∈ {50, 500, 5000}`. Três ordens de magnitude.

### O que esperar

Sem prejulgar a qualidade, algumas hipóteses **puramente exploratórias**:

- **Homogêneo:** não deve reduzir em nível 1 (já vimos isso); portanto não recurso nenhuma vez.
- **Desbalanceado extremo:** nível 1 reduz muito; nível 2 pode ou não reduzir, dependendo de como o P₁ se distribui (P₁ tem muitos `1`s → próximo dibit é dominado por `11`).
- **Ranking estabilizar:** espero que após alguns níveis o ranking entre em ciclo curto ou ponto fixo, porque a natureza das sequências de plano tem distribuição restrita.

Estas são hipóteses de pesquisa — o experimento decide.

---

## Resultados

### Exemplo canônico (28 bits do logic_03)

```
lvl  in_bits       planos        total  delta  ranking
  1       28     [14, 4, 1]         19     -9  01>10>11>00
  2       19     [9, 5, 2]          16     -3  11>01>10>00
  3       16     [8, 5, 2]          15     -1  01>11>00>10
  4       15     [7, 4, 2]          13     -2  01>10>00>11
  5       13     [6, 3, 2]          11     -2  01>00>10>11
  6       11     [5, 3, 1]           9     -2  00>01>11>10

final: 28 → 9 bits (acumulado 0.32x), 6 níveis, round-trip OK
```

**Observação imediata:** nenhum nível repete o ranking do anterior. O ranking flutua a cada passagem.

### Scale test — 5 distribuições × 3 tamanhos

| Distribuição            | N     | Níveis | In → Out       | Acum    | Ranking final          | Estab. | Round-trip |
|-------------------------|-------|-------:|----------------|---------|-------------------------|--------|------------|
| desbalanceado 75-8-8-8  | 50    | 3      | 100 → 46       | 0.460x  | `11>00>01>10`           | 1/3    | OK         |
| desbalanceado 75-8-8-8  | 500   | 2      | 1000 → 660     | 0.660x  | `11>01>10>00`           | 1/2    | OK         |
| desbalanceado 75-8-8-8  | 5000  | 2      | 10000 → 6586   | 0.659x  | `11>10>01>00`           | 1/2    | OK         |
| homogêneo 25-25-25-25   | 50    | 0      | 100 → 100      | 1.000x  | (não reduziu)           | —      | OK         |
| homogêneo 25-25-25-25   | 500   | 0      | 1000 → 1000    | 1.000x  | (não reduziu)           | —      | OK         |
| homogêneo 25-25-25-25   | 5000  | 0      | 10000 → 10000  | 1.000x  | (não reduziu)           | —      | OK         |
| um ausente (00=0%)      | 50    | 2      | 100 → 83       | 0.830x  | `11>00>01>10`           | 1/2    | OK         |
| um ausente (00=0%)      | 500   | 1      | 1000 → 859     | 0.859x  | `01>10>11>00`           | 1/1    | OK         |
| um ausente (00=0%)      | 5000  | 1      | 10000 → 8508   | 0.851x  | `01>10>11>00`           | 1/1    | OK         |
| bimodal 40-40-10-10     | 50    | 1      | 100 → 85       | 0.850x  | `01>10>00>11`           | 1/1    | OK         |
| bimodal 40-40-10-10     | 500   | 1      | 1000 → 908     | 0.908x  | `01>10>00>11`           | 1/1    | OK         |
| bimodal 40-40-10-10     | 5000  | 1      | 10000 → 8956   | 0.896x  | `10>01>00>11`           | 1/1    | OK         |
| extremo (1 dominante 95%) | 50  | 4      | 100 → 16       | 0.160x  | `11>01>00>10`           | 1/4    | OK         |
| extremo (1 dominante 95%) | 500 | 4      | 1000 → 250     | 0.250x  | `11>00>10>01`           | 1/4    | OK         |
| extremo (1 dominante 95%) | 5000 | 4     | 10000 → 2380   | 0.238x  | `11>00>10>01`           | 1/4    | OK         |

A coluna **Estab.** `K/N` indica: dos N níveis executados, os últimos K tiveram ranking idêntico (K=1 significa "apenas o último").

---

## Observações do experimento

### 1. Round-trip é estável em todas as escalas

Nenhum dos 15 casos falhou. Pequeno problema encontrado e corrigido: quando `input_bits` é ímpar, sobra um bit que não forma dibit. O encoder precisa registrar esse `tail_bit` e o decoder precisa reanexá-lo. Sem esse cuidado, perde-se 1 bit por nível ímpar.

### 2. O ranking nunca se torna ponto fixo

Em nenhuma execução dois níveis consecutivos produziram o **mesmo** ranking. A coluna `Estab.` é sempre `1/N` quando há redução.

Interpretação honesta: a distribuição dos dibits **muda a cada passada**. Os planos são pedaços binários com estrutura diferente da do input — agrupar esses bits de volta em dibits para o próximo nível produz um novo histograma, com nova ordem.

Isso implica que **o ranking precisa ser armazenado em cada nível** — não é possível "fixar um dicionário" e reutilizar. A metadata cresce linearmente com o número de níveis (4! = 24 permutações × número de níveis).

### 3. Homogêneo não recursa

Já no nível 1 o total de planos ≥ input, então para. Quatro dibits com 25% cada dão planos cheios ou muito próximos — nada a compactar.

### 4. Distribuição extrema recursa mais

"Extremo" (95% dominância) faz 4 níveis em todos os tamanhos. Cada nível corta aproximadamente metade do material. A razão acumulada chega a 0.16x em N=50, 0.24x em N=5000.

A diferença entre N=50 (0.16x) e N=5000 (0.24x) não é "pior em grande"; é efeito de amostra. Em N=50 a distribuição real pode ser mais extrema que os 95% nominais. Em N=5000 ela converge para os 95%.

### 5. N pequeno causa mais níveis em alguns casos

Nos casos "desbalanceado 75-8-8-8" e "um ausente", N=50 produz MAIS níveis que N=500 ou N=5000. Razão: flutuação estatística faz com que o segundo nível ainda encontre estrutura residual exploitável, enquanto em N grande a estrutura já foi totalmente drenada no primeiro nível.

Isso sugere que **mais recursão não é automaticamente melhor**. Depende da estrutura remanescente.

### 6. Estabilização estatística dos grandes

Em N=500 e N=5000, para cada distribuição, a razão acumulada é praticamente a mesma. Exemplos:

- desbalanceado 75-8-8-8: 0.660x vs 0.659x
- um ausente: 0.859x vs 0.851x
- bimodal: 0.908x vs 0.896x
- extremo: 0.250x vs 0.238x

A partir de N ≈ 500, o processo já tem comportamento assintoticamente estável. Experimentos em N maior provavelmente só refinam essa estatística.

---

## Implicações para o plano

1. **O ranking flutua a cada nível** — sem ponto fixo nos casos testados. Isso significa que v1 recursivo precisa registrar um ranking por nível, e não há atalho "mesmo dicionário para todos".

2. **A recursão tem ponto de parada natural** pelo critério `total ≥ input`. Nenhum caso explodiu para além de 4 níveis.

3. **A qualidade do processo depende fortemente da distribuição inicial.** O processo é honesto: faz o que pode, onde pode.

4. **Para v2, o canal de comando precisa justificar seu custo.** Em distribuições que v1 já comprime bem (extremo, desbalanceado), adicionar v2 pode não ajudar muito — o ganho já foi pego. Onde v1 falha (homogêneo, bimodal), v2 pode preencher a lacuna com estrutura macro que v1 não enxerga.

### Próximas perguntas abertas

- E se aplicarmos a recursão a **cada plano separadamente** em vez de concatenar? (Árvore de planos)
- E se o ranking do nível 0 for **mantido** para os níveis seguintes (mesmo que subótimo)? Qual a perda?
- E se, em vez de concatenar em ordem, concatenarmos **plano a plano recursivamente** (primeiro P1, depois aplicar no resto)?
- Há uma distribuição inicial para a qual o processo entra em ciclo (ranking oscilante)?

Essas são perguntas para explorar antes ou depois de v2 — à escolha.

