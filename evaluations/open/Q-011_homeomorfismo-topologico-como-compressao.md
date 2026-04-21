---
id: Q-011
titulo: Compressão como homeomorfismo topológico — o arquivo é a função φ, não os dados
categoria: novidade
prioridade: critica
criado: 2026-04-03
relacionado: [Q-001, Q-008, Q-010]
---

## Pergunta

É possível reformular compressão como o problema de encontrar um homeomorfismo
φ: C → D (de espaço compacto C para o espaço original dos dados D), de forma que
o arquivo comprimido seja a descrição de φ (e de C), tornando a compressão
independente do dado armazenado — apenas da estrutura do espaço?

---

## A Ideia Central

Compressão clássica:
```
arquivo = versão menor de D
decoder reconstrói D a partir do arquivo
```

Compressão funcional:
```
arquivo = descrição de φ: C → D
decoder avalia φ(c) para qualquer c ∈ C → reconstrói D
```

A diferença: no modelo funcional, **nunca armazenamos D** — armazenamos a função
que gera D. Decompressão é computação, não cópia.

---

## Hipótese Matemática

**H1:** Para qualquer dado D que satisfaz a hipótese do manifold (D vive em manifold
M ⊂ ℝⁿ com dim(M) = d << n), existe homeomorfismo φ: C → M onde C é espaço compacto
de dimensão d, e descrição de φ requer O(d · polylog(n)) bits — menor que D.

**H2:** A busca de φ ótimo é equivalente a minimizar:
```
|descrição(C)| + |descrição(φ)| + |residual(φ(C), D)|
```
que é o princípio MDL aplicado a homeomorfismos.

**H3:** Hilbert curves, SIREN, IFS e gramáticas são classes específicas de φ
parametrizadas por seus argumentos. O HSC atual busca φ na classe de curvas
de preenchimento de espaço — uma família restrita mas bem definida.

---

## Instâncias Conhecidas de Compressão Funcional

| Técnica | O que é φ | O que é C |
|---------|-----------|-----------|
| IFS (compressão fractal) | Conjunto de contrações afins | Atrator (fractal) |
| SIREN/INR | Rede neural com pesos θ | Grade de coordenadas |
| BWT + MTF | Permutação lexicográfica | Espaço de rotações |
| Gramática (Sequitur) | CFG com regras | Linguagem da gramática |
| **Hilbert (HSC)** | Curva de preenchimento + modelo Markov | Grade 2D |

**O HSC é uma instância de compressão funcional** com φ restrito à família
de curvas de Hilbert em grades 2D. A generalização proposta: buscar φ em
famílias mais ricas.

---

## Condição de Compressão

φ comprime D se e somente se:
```
|φ| + |C| + |residual| < |D|
```

Onde `|residual|` = custo de descrever o que φ(C) não capturou exatamente.

Para compressão lossless: residual = 0 (φ é exato).
Para compressão lossy: residual = tolerância ε (φ é ε-aproximação).

O parâmetro ε é o knob de lossy/lossless — exatamente o "controle de tolerância
ao erro" que o HSC já propõe como feature.

---

## Questões de Investigação

### Q11.1 — Qual família de φ é ótima por tipo de dado?

| Tipo de dado | Família φ recomendada | Justificativa |
|---|---|---|
| Imagem 2D natural | Curvas de Hilbert + SIREN | Correlação local + estrutura contínua |
| Texto | BWT + gramática | Correlação lexicográfica |
| DNA | Curvas + gramática | Periodicidade + repetições |
| Dados científicos (float) | F-transform + INR | Origem contínua, compressível lossy |
| Executável | Filtro ISA + gramática | Vocabulário de instruções |

### Q11.2 — A homologia persistente de D pode guiar a escolha de φ?

Se o diagrama de persistência de D mostra:
- Muitos H₀ componentes → dado tem clusters → φ baseado em agrupamento
- H₁ loops → dado tem periodicidade → φ baseado em wavelets/Fourier
- Topologia flat → dado é suave → φ baseado em SIREN/polynomiais

Isso tornaria a seleção de φ automática a partir da topologia dos dados.

### Q11.3 — Qual é a complexidade computacional de buscar φ ótimo?

- Classe IFS: NP-hard no caso geral (busca de contrações)
- Classe Hilbert: O(log N) candidatos, tratável
- Classe SIREN: gradiente descendente (approximação, não ótimo)
- Classe gramática: O(N²) para Re-Pair (aproximação do ótimo)

---

## Conexão com Q-001 (Novidade)

**A reformulação HSC em termos de homeomorfismo topológico é nova?**

Instâncias separadas existem (IFS desde 1985, SIREN desde 2020). O que não
existe como framework unificado:
1. A unificação de todas as técnicas sob o mesmo princípio φ: C → D
2. A busca adaptativa sobre classes de φ baseada em topologia dos dados
3. A combinação com álgebra fuzzy para residuais de dados de origem contínua
4. O formato auto-descritivo que carrega φ + descrição de C juntos

Isso expande e reformula a contribuição de Q-001.

---

## Plano de Investigação

### Fase teórica (sem implementação)
- [ ] Formalizar a definição de "arquivo como homeomorfismo" com notação matemática precisa
- [ ] Provar que IFS, SIREN, BWT são casos especiais do framework
- [ ] Derivar condição necessária e suficiente de compressão em termos de dim(M)
- [ ] Verificar na literatura: existe formulação equivalente?

### Fase experimental (dependente de Q-003)
- [ ] Comparar |φ_Hilbert| + |resíduo| vs. |dados| para datasets canônicos
- [ ] Medir dim intrínseca dos datasets (PCA, UMAP) como proxy para dim(M)
- [ ] Verificar se datasets com menor dim intrínseca comprimem mais com Hilbert

---

## Critério de Conclusão

- **Confirmado:** Framework formalizado, instâncias verificadas, e literatura não
  apresenta formulação equivalente → contribuição teórica clara para Q-001.
- **Parcialmente confirmado:** Formulação existe, mas a busca adaptativa e a
  combinação com fuzzy são novas → contribuição incremental mas sólida.
- **Refutado:** Formulação idêntica encontrada na literatura → reformular
  contribuição como aplicação específica do framework existente.
