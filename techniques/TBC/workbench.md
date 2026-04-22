# TBC — Mesa de Trabalho (workbench)

Este documento traz **pequenos exemplos pensáveis a olho nu** para que a gente discuta antes de implementar. Todos usam `k=2` (dibits). Quatro símbolos possíveis: `00`, `01`, `10`, `11`.

Nomenclatura: usamos **dibit** (com `i`) seguindo a literatura de modulação digital (PSK/QAM). "Dubit" é a palavra que surgiu na conversa e permanece como sinônimo informal. "Crumb" é outra alternativa registrada.

---

## V1 — Dibits **muito desbalanceados** (um domina)

```
raw_data  01 01 01 01 01 01 01 01 01 01 01 01 10 01 11 00      (16 dibits = 32 bits)
```

Contagem:

| dibit | freq | %   |
|-------|------|-----|
| `01`  | 12   | 75% |
| `10`  | 1    | 6%  |
| `11`  | 1    | 6%  |
| `00`  | 1    | 6%  |

Ranking: `σ₁=01, σ₂=10, σ₃=11, σ₄=00` (ou `σ₂=00` dependendo do desempate — aqui uso lex ascendente, então `00 < 10 < 11`, mas todos têm freq=1; com lex `00` vem antes e seria σ₂. Vou usar `00 < 10 < 11`).

**Correção do ranking** (desempate lex ascendente):

| rank | dibit | freq |
|------|-------|------|
| σ₁   | `01`  | 12   |
| σ₂   | `00`  | 1    |
| σ₃   | `10`  | 1    |
| σ₄   | `11`  | 1    |

**Planos (M0 puro):**

```
pos:    0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
sym:   01 01 01 01 01 01 01 01 01 01 01 01 10 01 11 00

P₁ (onde σ₁=01):
        1  1  1  1  1  1  1  1  1  1  1  1  0  1  0  0    (16 bits)

posições remanescentes após P₁:  12, 14, 15  (três posições)
sym nelas:                       10, 11, 00

P₂ (onde σ₂=00, nas 3 restantes):
        0  0  1                                            (3 bits)
        (pos 12 é 10 → 0; pos 14 é 11 → 0; pos 15 é 00 → 1)

posições remanescentes após P₂:  12, 14

P₃ (onde σ₃=10, nas 2 restantes):
        1  0                                               (2 bits)

σ₄=11 é resíduo: pos 14 é σ₄, implícito.

TOTAL de planos: 16 + 3 + 2 = 21 bits
Original:        32 bits
Overhead de header: ranking (log₂(4!) ≈ 5 bits) + N (5 bits) = ~10 bits
Total aproximado: 31 bits. Empate com o original.
```

**Observação:** mesmo com 75% de dominância, M0 puro quase não ganha aqui porque o fluxo é curto. O header come o ganho. Escala ajuda.

---

## V2 — Dibits **homogêneos** (distribuição ~uniforme)

```
raw_data  00 01 10 11 01 10 11 00 10 11 00 01 11 00 01 10      (16 dibits = 32 bits)
```

Contagem:

| dibit | freq | %    |
|-------|------|------|
| `00`  | 4    | 25%  |
| `01`  | 4    | 25%  |
| `10`  | 4    | 25%  |
| `11`  | 4    | 25%  |

Ranking (desempate lex): `σ₁=00, σ₂=01, σ₃=10, σ₄=11`.

**Planos (M0 puro):**

```
P₁ (onde σ₁=00):
        1  0  0  0  0  0  0  1  0  0  1  0  0  1  0  0    (16 bits)
        (pos 0, 7, 10, 13 são 00)

restantes após P₁: 12 posições (1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 14, 15)

P₂ (onde σ₂=01, nas 12 restantes):
        1  0  0  1  0  0  0  0  1  0  0  0                (12 bits)
        (entre as 12, 01 ocupa 4 — posições 1, 4, 11, 14 no original)

restantes após P₂: 8 posições

P₃ (onde σ₃=10, nas 8 restantes):
        1  0  1  0  1  0  0  1                            (8 bits)
        (10 ocupa 4 das 8 restantes)

σ₄=11 implícito (sobram 4 posições com 11).

TOTAL: 16 + 12 + 8 = 36 bits
Original: 32 bits
Overhead de header: ~10 bits.
Total: ~46 bits. PIOR que o original em 14 bits.
```

**Observação crítica:** distribuição uniforme é o pior caso para M0. Cada plano tem entropia máxima e M0 paga opcode-zero em cada um deles. Este é o caso onde **o método TBC v1 explicitamente perde**. Qualquer melhoria (comandos, entropia) teria que vir por outro caminho — porque não há padrão simples a explorar.

Esta é também uma boa âncora experimental: **se M2 não vencer aqui, é por falta de estrutura macro, não por falha do método.**

---

## V3 — Dibits com **um ausente**

```
raw_data  01 01 01 10 10 01 10 11 01 01 10 11 01 10 11 01      (16 dibits)
```

Contagem:

| dibit | freq | %      |
|-------|------|--------|
| `01`  | 7    | 43.75% |
| `10`  | 5    | 31.25% |
| `11`  | 3    | 18.75% |
| `00`  | 0    | 0%     |

Ranking: `σ₁=01, σ₂=10, σ₃=11, σ₄=00` (com freq 0).

**Planos (M0 puro):**

```
P₁ (onde σ₁=01):
        1  1  1  0  0  1  0  0  1  1  0  0  1  0  0  1    (16 bits)
        (01 em pos 0,1,2,5,8,9,12,15 — mas isso é 8, não 7. Recontando…)

Recontando o dado: 01 01 01 10 10 01 10 11 01 01 10 11 01 10 11 01
pos:               0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15

pos 0=01, pos 1=01, pos 2=01, pos 5=01, pos 8=01, pos 9=01, pos 12=01, pos 15=01 → 8 ocorrências de 01.

Corrigindo a contagem:
```

| dibit | freq | %   |
|-------|------|-----|
| `01`  | 8    | 50% |
| `10`  | 5    | 31% |
| `11`  | 3    | 19% |
| `00`  | 0    | 0%  |

```
P₁ (onde σ₁=01):
        1  1  1  0  0  1  0  0  1  1  0  0  1  0  0  1    (16 bits)

restantes: pos 3, 4, 6, 7, 10, 11, 13, 14 (8 posições)
sym:       10, 10, 10, 11, 10, 11, 10, 11

P₂ (onde σ₂=10):
        1  1  1  0  1  0  1  0                            (8 bits)

restantes: pos 7, 11, 14 (3 posições, todos 11)

σ₃=11: normalmente emitiríamos P₃. Mas note que só restam 3 posições e todas são σ₃.
Se fosse estritamente M0, emitiríamos P₃ = 1 1 1 (3 bits). Mas nessa configuração
σ₄=00 tem freq zero — σ₃ acaba sendo o "último real". **Podemos omitir P₃?**

Resposta: sim, se o header informar explicitamente que σ₃ é o último símbolo com
freq > 0. Isso é uma otimização: sempre que σ_{m'} com m' < m tem freq(σ_{m'+1}) = 0,
σ_{m'} pode ser tratado como residual implícito.

Economia aqui: 3 bits (o P₃).

TOTAL otimizado: 16 + 8 = 24 bits + header
Original: 32 bits
Ganho real quando σ₄ não aparece: ganho bruto ~25% antes de header.
```

**Observação:** dibits ausentes permitem "encurtar o ranking". Isso é uma inferência barata e deve estar explícita no header (bit para cada símbolo do alfabeto: apareceu ou não).

---

## V4 — Dibits **bimodais** (dois dominam, dois raros)

```
raw_data  01 10 01 10 01 10 01 10 01 10 01 10 00 11 01 10      (16 dibits)
```

Contagem:

| dibit | freq | %      |
|-------|------|--------|
| `01`  | 7    | 43.75% |
| `10`  | 7    | 43.75% |
| `00`  | 1    | 6.25%  |
| `11`  | 1    | 6.25%  |

Padrão visível: `01 10 01 10 01 10 01 10 01 10 01 10` + `00 11` + `01 10`. Doze posições são o par alternante `01 10`. Isso é **estrutura macro** que M0 não enxerga mas M2 enxergaria trivialmente.

```
P₁ (onde σ₁=01):
        1  0  1  0  1  0  1  0  1  0  1  0  0  0  1  0    (16 bits)

P₂ (onde σ₂=10):
        1  1  1  1  1  1  0  0  1                         (9 bits — restantes são 7)
        Espera, o σ₂ entra nas posições não marcadas em P₁: pos 1,3,5,7,9,11,12,13,15.
        Dessas, 10 ocupa pos 1,3,5,7,9,11,15 (7). Então P₂ = 1 1 1 1 1 1 0 0 1 (9 bits).

P₃ (onde σ₃=00, nas 2 restantes):
        1  0                                              (2 bits)

σ₄=11 implícito na posição 13.

TOTAL: 16 + 9 + 2 = 27 bits + header
```

**Com M2 (LZ):**

O encoder vê a repetição de `01 10` cedo e emite:
- `LIT 01` — emite 01
- `LIT 10` — emite 10
- `REF offset=2 len=10` — copia o que já foi emitido 5 vezes
- `LIT 00` — emite 00
- `LIT 11` — emite 11
- `REF offset=14 len=2` — copia `01 10` de novo (ou LITs)

Custo aproximado M2:
- 2 LIT iniciais: 2×(3+2) = 10 bits
- REF(2, 10): 3 + γ(2) + γ(10) = 3 + 3 + 7 = 13 bits
- 2 LITs para 00,11: 10 bits
- REF(14, 2): 3 + γ(14) + γ(2) = 3 + 7 + 3 = 13 bits
- END: 3 bits
- Header: ~10 bits
- **Total M2 ≈ 59 bits**

Neste exemplo muito pequeno, **M0 vence M2**. M2 só ganha em fluxos maiores onde a repetição amortiza o opcode.

---

## Síntese das quatro variações

| Caso | Distribuição | M0 ganha? | M2 ganha? | Observação |
|------|--------------|-----------|-----------|------------|
| V1 desbalanceado | 1 domina 75% | sim (limitado) | marginal | Header come ganho em escala pequena |
| V2 homogêneo    | 25% cada  | **não** (perde 14b) | **não** | Incomprimível por estrutura local |
| V3 ausente      | 1 domina + 1 ausente | sim (otimiza skip do último plano) | sim se for grande | Inferência do "ranking curto" |
| V4 bimodal      | par alternante | sim (moderado) | só em escala | Estrutura macro que LZ pega |

Conclusão desta análise:

> **O TBC v1 (M0) depende de desbalanceamento local. Se não houver, não há ganho algum. Isso é honesto e esperado — M0 é o piso do método.**

> **Qualquer ganho maior precisa vir de: (a) entropia dentro dos planos; (b) comandos no canal residual (v2 conceitual); (c) referência retroativa (M2). Cada um ataca uma classe diferente de estrutura.**

---

## O paradoxo do resíduo-como-comando

Você levantou este ponto literalmente:

> *"depois de eu fazer os estágios de passar pelos 3 dubits, o quarto dubit residual conseguir se identificar nas 3 sequencias para descomprimir, me parece um paradoxo."*

Vou expor o que é o paradoxo e como destravar.

### Enunciando o paradoxo

Em M0 puro: o decoder percorre os planos P₁, P₂, P₃. Toda posição não marcada por nenhum deles é σ₄ (o residual implícito).

Na versão comando: queremos que o residual seja um **canal de programa**. Isso significa que as posições residuais não guardam mais dados do tipo σ₄ — guardam **instruções**.

O paradoxo aparece porque:

1. Se o resíduo é sempre comando, não há como representar `σ₄` como dado.
2. Se o resíduo às vezes é comando e às vezes é dado, o decoder não sabe distinguir sem informação adicional — **que custa bits**.
3. A informação adicional roubaria parte do ganho que o comando deveria trazer.

É realmente um paradoxo estrutural, não só uma ambiguidade de implementação.

### Três soluções conhecidas

**Solução A — σ₄ deixa de existir como dado.**
Se eu declarar que toda posição residual é instrução, o símbolo σ₄ desaparece como dado. Se ele aparecer no input real, o compilador emite `LIT(σ₄)` no programa para recriar. Custo: cada ocorrência real de σ₄ vira uma instrução explícita.

Quando funciona bem: quando σ₄ é genuinamente raro. Como o resíduo por definição é o símbolo **menos frequente**, f(σ₄) é pequeno. LIT é caro mas são poucas chamadas.

Quando funciona mal: quando há muitos σ₄ **e** não há padrão macro para comandos explorarem. Aí pagamos LIT sem retorno.

**Solução B — dois planos-resíduo.**
Um plano extra P_R marca, dentro das posições residuais, quais são dados (σ₄) e quais são comando. O custo é |P_R| = f(σ₄) + n_commands bits.

Se o número de comandos for pequeno, P_R é curto. Mas ele ainda paga um bit por resíduo.

**Solução C — ordem separada.**
O arquivo tem uma seção explícita de programa (fora dos planos). O programa é executado antes dos planos e marca posições "ocupadas pelo programa". Planos só preenchem o que restar. Aí não há ambiguidade: a separação é estrutural.

Esta é a solução mais simples e é a que os codecs reais usam (header-then-body). É também a mais próxima do que M2 já faz hoje (o programa é literalmente a sequência de instruções; não há planos).

### Recomendação para o protótipo

**Ir pela Solução C.** Pelas seguintes razões:

1. **Ela unifica M0, M1, M2.** M0 ≡ "programa que é só SKIPs + planos". M1 ≡ "só programa, sem planos". M2 ≡ "programa com REF, sem planos". Hipotético M1.5 ≡ "programa com SKIPs + planos nas regiões SKIPpadas".
2. **Resolve o paradoxo por decreto.** Não há ambiguidade: se está no programa, é comando; se está num plano, é dado.
3. **É incremental.** Podemos implementar M1.5 adicionando um opcode `SKIP(n)` ao M1 e declarando que após a execução do programa, posições não tocadas são preenchidas por planos M0.

A solução A é elegante mas paga LIT por cada σ₄ real. A solução B tem custo fixo por resíduo. A solução C tem custo zero para posições que não disparam comando — elas simplesmente não aparecem no programa.

### O que isso muda na teoria

A "residual-como-comando" original (v0.3 do compression_logic_03.md) descreve a mesma ideia da Solução A mas via "gatilho implícito". Funciona, mas é frágil. A Solução C descreve a mesma família de máquinas sem paradoxo: o programa sempre está em lugar próprio, declarado, sem gatilho implícito.

**Podemos manter a ideia v0.3 como instância particular da Solução C:** um programa cujo "arquivo físico" ocupa o mesmo espaço que as posições residuais ocupariam em M0. Isso é uma **decisão de formato**, não de semântica. Semanticamente, há planos e há programa. Fisicamente, eles podem compartilhar o mesmo espaço de bits se a gente quiser economizar.

---

## Opcodes: o que é inferível e o que não é

Algumas perguntas que você levantou sobre a ISA:

**Q: LITERAL pode ser inferido? "o compressor sempre começa em modo literal"**

Sim, parcialmente. Podemos definir:
- O programa começa em **modo emit literal**.
- Enquanto em modo literal, bits são interpretados como símbolos (`k` bits cada).
- Uma instrução `MODE` muda o modo para REP, REF, etc.

Problema: como marcar o fim do modo literal? Duas opções:
- **(i) Comprimento fixo.** Header diz "os próximos N_lit símbolos são literais". Bom se o compressor decide blocos grandes antecipadamente.
- **(ii) Escape por símbolo.** Um símbolo especial sinaliza saída do modo literal. Requer reservar um valor do alfabeto, reduzindo alfabeto efetivo.

Em alfabetos pequenos (k=2), escape é caro porque um dos 4 dibits teria que virar "escape". Nunca compensa.

**Q: Loop x vezes volta ao literal automaticamente?**

Sim, naturalmente. `LOOP(count, body_len)` executa as próximas body_len instruções count vezes. Quando termina, o ponteiro de instrução passa para a instrução após o corpo. Estado seguinte = estado anterior ao LOOP.

Esse é o caminho padrão para adicionar loop sem END explícito no corpo.

**Q: Precisa de marcador de fim de operação?**

Depende de como codificamos os operandos. Se todo operando tem comprimento calculável a partir do opcode + parâmetros fixos + Elias-gamma (auto-delimitante), o decoder sabe sempre quando cada instrução terminou. Não precisa de END por instrução. Só precisa de END global para o programa.

Nossa ISA já é assim. Opcode + operandos de comprimento autocontido → sem END interno.

---

## Plano revisado após esta análise

1. **Manter M2 como está** (LZ simples). É nossa linha de base para texto.
2. **Formalizar a Solução C** num documento: unificação M0/M1/M2 como configurações do mesmo paradigma programa+planos.
3. **Implementar M1.5 (opcional):** programa M1 + opcode SKIP(n) + planos M0 nas regiões SKIP. Testar em V1/V3/V4 onde a intuição prevê ganho.
4. **M3 (depois):** adicionar DEF/CALL/LOOP, cobrir grammar-based.
5. **Entropia final:** aplicar Huffman/ANS aos opcodes e literais em qualquer Mn. Fecha gap com zlib.

Ordem prática sugerida: **fixar formato binário com header explícito (solução C), depois M3, depois entropia final.** Essa ordem deixa cada etapa com ganho mensurável isolado.
