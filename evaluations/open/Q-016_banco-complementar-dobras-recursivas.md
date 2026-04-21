---
id: Q-016
titulo: Banco complementar com dobras recursivas e matching aproximado
categoria: novidade
prioridade: critica
criado: 2026-04-04
relacionado: [Q-010, Q-011, Q-008, Q-015]
---

## Pergunta

Um codec baseado em: (1) dobra matematica do feature space para clustering
de segmentos similares-mas-nao-identicos, (2) criacao de representantes
canonicos por cluster, (3) residuais esparsos complementares, e (4) dobras
recursivas dos residuais — constitui uma abordagem nova e viavel?

---

## Descricao da Ideia (Intuicao do Autor)

### Operacao Central

Dados brutos sao "dobrados" num espaco matematico onde segmentos similares
se alinham, mesmo com deslocamentos e pequenas variacoes:

```
011011111101 ->
[011011,
 x111101] ->
[representante: 11111]
[membro 1: tem um zero no inicio]
[membro 2: deslocado 1, ultimo 1 vira 01]
```

### Tres Operacoes Fundamentais

1. **Dobra do espaco:** Transformar os dados de forma que itens similares
   (nao necessariamente identicos nem de mesmo tamanho) fiquem proximos.
   A dobra e binaria/recursiva — dobrar ao meio, comparar metades.

2. **Banco complementar:** Para cada cluster de segmentos similares, criar
   um REPRESENTANTE canonico (identico artificial) e armazenar:
   - O representante (uma vez)
   - Ponteiros dos membros para o representante
   - Residuais esparsos de cada membro (diferencas vs representante)

3. **Dobras recursivas dos residuais:** Os residuais tem estrutura propria
   (sao eles mesmos compressiveis). Aplicar o mesmo processo recursivamente:
   residual -> dobra -> representante -> sub-residual -> ...
   Ate chegar a residuais incompressiveis (ruido puro).

### Dimensoes de Similaridade

- XOR (bits diferentes)
- Deslocamento (shift por d posicoes)
- Complemento (NOT — bits invertidos)
- Escala (blocos de tamanhos diferentes normalizados)

---

## Analise da Literatura: O Que Ja Existe

### Tecnicas Mais Proximas

| Tecnica | Matching aprox? | Representante+Residual? | Recursivo? | Limitacao vs proposta |
|---------|----------------|------------------------|-----------|----------------------|
| **RVQ (Residual Vector Quantization)** | Sim (nearest codebook) | Sim (codebook + residual cascateado) | **Sim** | Vetores fixos, sem dobra binaria, sem complemento |
| **Locally Consistent Parsing** | Sim (cores canonicos) | Parcial (cores sao representantes) | **Sim** (iterativo) | Ferramenta de comparacao, nao codec |
| **LZ_XOR (Geldreich, 2022)** | Sim (XOR parcial) | Parcial (referencia + correcoes) | Nao | Greedy sliding window, sem clustering |
| **Fractal/PIFS (Jacquin, 1992)** | Sim (transformacoes afins) | Sim (domain block + afim) | Nao | So 2D, encoding lento, lossy |
| **H.264/HEVC residual coding** | Sim (motion compensation) | Sim (predicao + residual DCT) | Nao | Grid fixo, so video temporal |
| **Git pack delta** | Fraco (heuristica nome/tamanho) | Sim (base + delta) | Nao | Pairwise, nao clustered |
| **Bit-Swap (Kingma, 2019)** | Diferenciacao, nao matching | Sim (hierarquia latente) | **Sim** | Neural, nao pratico para codec geral |
| **Grammar (Re-Pair, Sequitur)** | **Nao** (so exato) | Parcial (nonterminals) | Nao | Nao tolera variacoes |
| **K-means centroid** | Sim (nearest centroid) | Sim mas lossy (descarta residual) | Nao | Lossy, sem residual preservation |
| **Approximate LZ (Steinberg, 1993)** | Sim (Hamming dist k) | Parcial (ref + patches literais) | Nao | Patches nao sao estruturados |

### Conclusao da Pesquisa

**Nenhuma tecnica existente combina os 4 elementos da proposta:**

1. Dobra binaria recursiva do espaco (nao apenas sliding window)
2. Clustering com representantes canonicos (nao apenas matches pairwise)
3. Residuais esparsos explicitamente codificados (nao descartados como lossy)
4. Recursao sobre residuais (comprimir os residuais com o mesmo metodo)

O mais proximo e **RVQ** (cascata de codebooks sobre residuais) — mas RVQ
opera em vetores de tamanho fixo, usa distancia euclidiana, e nao faz
dobra binaria nem explora complemento/deslocamento.

---

## Formalizacao Proposta

### Definicoes

```
Dado: S = sequencia de N bytes

FoldCluster(S, params):
  1. Particionar S em blocos B_1, ..., B_k (tamanho variavel)
  2. Para cada par (B_i, B_j):
     sim(B_i, B_j) = 1 - hamming(align(B_i, B_j)) / max(|B_i|, |B_j|)
     onde align() testa: identidade, shift(d), complemento, shift+complemento
  3. Clustering: agrupar blocos com sim > threshold
  4. Para cada cluster C_m:
     representante R_m = medoid ou consenso do cluster
     Para cada B_i in C_m:
       residual_i = encode_diff(B_i, R_m)  # XOR esparso + shift + flags
  5. Retornar {(R_m, [(ptr_i, residual_i) for B_i in C_m]) for each C_m}

Recursao:
  residuais_todos = concat(todos os residuais)
  se entropy(residuais_todos) > threshold:
     FoldCluster(residuais_todos, params_refinados)
  senao:
     codificar_entropicamente(residuais_todos)
```

### Custo MDL de um No

```
custo(no) = custo(representante) +
            sum(custo(ponteiro_i) + custo(residual_i)) +
            custo(parametros_cluster)

Condicao de ganho:
  custo(no) < sum(custo(B_i))  para todos B_i do cluster
```

### Dimensoes de Alinhamento (align())

```
align(A, B):
  candidatos = []
  para d in [-max_shift, ..., +max_shift]:
    para complement in [False, True]:
      B' = shift(B, d)
      se complement: B' = NOT(B')
      score = popcount(A XOR B') / max(|A|, |B|)
      candidatos.append((d, complement, score))
  retornar min(candidatos, key=score)
```

---

## Conexoes com Framework HSC

### Com Q-010 (Fold-XOR)
Q-016 GENERALIZA Q-010:
- Q-010: dobra fixa (metade), matching exato+XOR, sem clustering
- Q-016: dobra adaptativa, matching aproximado, clustering com representantes

Q-010 e um caso especial de Q-016 onde:
- Numero de clusters = 2 (metades)
- Representante = uma das metades
- Residual = XOR da outra metade
- Sem shift nem complemento

### Com Q-011 (Homeomorfismo)
O "banco complementar" e uma implementacao concreta do homeomorfismo phi:
- phi^-1 (compressao) = encontrar representantes + residuais
- phi (descompressao) = aplicar residuais aos representantes
- C (espaco compacto) = conjunto de representantes
- Residuais = descricao de phi

### Com Q-015 (Kernel)
Kernels poderiam definir a metrica de similaridade sim(B_i, B_j):
- Kernel RBF: similaridade baseada em distancia euclidiana
- String kernel: similaridade baseada em substrings comuns
- Custom kernel: incorpora shift + complemento como dimensoes

### Com Q-008 (Perspectivas)
- P1: a dobra do espaco e um remapeamento
- P3: representantes sao adaptativos (dependem dos dados)
- P4: representantes sao um "vocabulario" comprimido
- P5: o espaco dobrado permite busca multidirecional
- P6: residuais recursivos compoem multiplas camadas

---

## Hipoteses a Testar

**H1 (viabilidade):** Para dados com auto-similaridade local (imagens, texto,
executaveis), o metodo produz representantes que cobrem >= 60% dos blocos
com residuais <= 10% do tamanho do bloco.

**H2 (recursao util):** Pelo menos 2 niveis de recursao sobre residuais
produzem ganho mensuravel (>= 5% reducao adicional).

**H3 (complemento util):** A dimensao de complemento (NOT) captura matches
que XOR puro nao captura, em pelo menos 1 tipo de dado.

**H4 (novidade):** A combinacao (dobra binaria + clustering + representantes +
residuais recursivos + complemento) nao existe como codec na literatura.

---

## Prioridade e Sequenciamento

1. **Agora:** Registrar a ideia (este ticket).
2. **Sprint 2 (pos Q-003):** Implementar versao minima — fold fixo (Q-010)
   + medir XOR sparsity para validar H1 de forma barata.
3. **Sprint 3:** Se H1 confirmada, implementar clustering + representantes.
4. **Sprint 4:** Recursao sobre residuais.
5. **Paper:** Se H4 confirmada, esta e potencialmente a contribuicao central.

---

## Referencias

- Steinberg & Gutman (1993). A lossy compression based on approximate string matching. IEEE TIT.
- Sahinalp & Vishkin (1996). Locally Consistent Parsing. SODA.
- Geldreich (2022). LZ_XOR — XOR-based partial matching. Blog post.
- Gray (1984). Vector Quantization. IEEE ASSP Magazine.
- Zeghidour et al. (2022). SoundStream: End-to-end neural audio codec. IEEE TASLP.
- Jacquin (1992). Image coding based on fractal theory of IFS. IEEE TIP.
- Kingma et al. (2019). Bit-Swap: Recursive Bits-Back Coding. ICML.
- Larsson & Moffat (1999). Re-Pair: Off-line dictionary-based compression. IEEE DCC.
