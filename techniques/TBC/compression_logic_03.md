# TuringBitCompression — Lógica de Construção (v0.3)

> **Nota de leitura.** Este documento descreve o **processo mental** que origina o TBC, não a implementação ótima nem a análise de ganho. Qualidade de compressão é preocupação futura. Aqui o objetivo é fixar o vocabulário e a mecânica para que o protótipo tenha sobre o que iterar.

---

## 1. Por que este método existe

A compressão tradicional percorre os dados como uma fila de símbolos e tenta produzir, para cada posição da fila, uma codificação mais curta que a original. Huffman atribui códigos curtos aos símbolos frequentes. LZ detecta repetições adjacentes e as substitui por referências. Em todos os casos, a unidade de raciocínio é o símbolo no seu lugar.

O TBC parte de um giro conceitual diferente:

> **Em vez de perguntar "qual símbolo está nesta posição?", pergunto "quais posições este símbolo ocupa?".**

Isso muda o objeto da codificação. Deixamos de codificar uma sequência `S[0], S[1], …, S[N−1]` de símbolos. Passamos a codificar, para cada símbolo possível do alfabeto, a **máscara de ocupação** desse símbolo no fluxo.

Quando a distribuição é muito desigual — um símbolo domina e os outros são raros — a máscara do símbolo dominante é quase toda `1`, e as máscaras dos raros são quase toda `0`. Máscaras quase constantes são previsíveis, e o que é previsível colapsa sob qualquer codificador entrópico.

Até aqui, o método é apenas uma variante de **bitplane coding**. A novidade do TBC vem quando olhamos para o símbolo **menos** frequente.

---

## 2. Dados de partida

Trabalharemos com o mesmo exemplo canônico ao longo de todo o documento.

```
raw_data = 1001100110010101010101010111        (28 bits)
         = 10 01 10 01 10 01 01 01 01 01 01 01 01 11        (14 símbolos de 2 bits)
```

Agrupamos de dois em dois. A escolha de `k = 2` é convencional; qualquer outro `k` serviria. Com `k = 2` o alfabeto tem `2² = 4` símbolos: `00`, `01`, `10`, `11`.

Contamos as ocorrências:

| Símbolo | Contagem |
|---------|----------|
| `01`    | 10       |
| `10`    | 3        |
| `11`    | 1        |
| `00`    | 0        |

A distribuição é desbalanceada: `01` sozinho carrega 71% do fluxo. Essa assimetria é o combustível do método. Se a distribuição fosse uniforme (cada símbolo com 25%), o TBC não teria nada a explorar.

Ordenamos por frequência descendente, desempatando por ordem lexicográfica para que a ordenação seja determinística:

```
σ₁ = 01   (rank 1, o mais comum)
σ₂ = 10   (rank 2)
σ₃ = 11   (rank 3)
σ₄ = 00   (rank 4, o mais raro — zero ocorrências neste exemplo)
```

O ranking vai no cabeçalho do arquivo comprimido. É uma permutação dos `2^k` símbolos possíveis — para `k = 2`, no máximo `log₂(4!) ≈ 5` bits para descrever, ou, pior caso explícito, `4 × 2 = 8` bits.

---

## 3. Primeira construção: o plano como máscara de ocupação

Vamos construir, para cada símbolo exceto o último do ranking, uma **máscara** que marca `1` onde o símbolo ocorre e `0` onde não ocorre. Chamamos essa máscara de **plano de indicadores** ou simplesmente **plano**.

Usamos uma regra importante de economia: **o plano P_i só percorre as posições ainda não explicadas pelos planos anteriores**. Toda posição marcada com `1` num plano anterior é "resolvida" — não preciso mais perguntar sobre ela.

### Plano P₁ — onde está `01`?

`01` é σ₁, o mais comum. Ainda não temos nenhum plano anterior, então P₁ cobre as 14 posições originais.

```
pos:    0  1  2  3  4  5  6  7  8  9 10 11 12 13
sym:   10 01 10 01 10 01 01 01 01 01 01 01 01 11
P₁:     0  1  0  1  0  1  1  1  1  1  1  1  1  0     (14 bits)
```

Leitura: `1` significa "aqui é `01`"; `0` significa "aqui é algo diferente de `01`, ainda não sei o quê".

### Plano P₂ — onde está `10`, nas posições que P₁ deixou incertas?

P₁ deixou 4 posições com `0`: 0, 2, 4, 13. É só sobre elas que P₂ opinará.

```
posições incertas após P₁:   0   2   4  13
sym nessas posições:        10  10  10  11
P₂:                          1   1   1   0            (4 bits)
```

### Plano P₃ — onde está `11`, nas posições que P₂ deixou incertas?

P₂ deixou 1 posição com `0`: a posição 13. P₃ opina sobre ela.

```
posição incerta após P₂:  13
sym:                      11
P₃:                        1                          (1 bit)
```

### Resíduo implícito — σ₄ (`00`)

P₃ resolveu tudo. Não sobrou nenhuma posição incerta. Mesmo que tivesse sobrado, não precisaríamos codificá-la: o decodificador sabe que o que sobrar do percurso de planos é o símbolo de rank mais alto (`00`, no nosso caso). Essa é a economia do "último símbolo é implícito".

### Total

Resumo da versão 1 (o método original do TBC, sem comando):

| Plano | Tamanho |
|-------|---------|
| P₁    | 14 bits |
| P₂    | 4 bits  |
| P₃    | 1 bit   |
| σ₄    | 0 bits  |
| **Total bruto (sem header, sem entropia)** | **19 bits** |

Para comparação, os dados originais ocupam `14 × 2 = 28` bits. Há ganho bruto de 9 bits antes de qualquer codificação adicional. Mas isso já era conhecido — é só um rearranjo clever dos mesmos dados.

A pergunta interessante chega agora.

---

## 4. A observação que abre a versão 2

Olhe para o cenário de um ponto de vista diferente. Suponha que o plano P₁ tivesse ficado assim, em vez do bitmap que montamos:

```
P₁ (hipotético):   0  1  0  1  0  0  0           (7 bits, não 14)
```

Curto. Só 7 bits em vez de 14. Mas a informação que ele carrega original — "onde `01` ocorre no fluxo de 14 posições" — tem 10 uns, e precisaria de no mínimo 10 `1`s numa máscara. Esses 7 bits não cobrem isso.

E se o plano **não for uma máscara**? E se ele for um **programa**?

Leia novamente os 7 bits:

```
0 1 0 1 0 0 0
```

Reinterprete-os assim: "os quatro primeiros bits são a máscara tradicional até a posição 4; a partir dali, `0 0 0` deixa de significar 'não é `01`' e passa a significar 'para as posições de 5 a 12, repita o padrão que vem do símbolo dominante`".

A frase anterior está vaga de propósito. Ela será precisa quando definirmos a **linguagem de comando**. Mas o que importa é o salto conceitual:

> **Os bits de um plano não precisam ser apenas máscaras. Podem ser instruções.**

E existe um lugar natural para instruções: o **símbolo residual**.

---

## 5. Por que o residual é o canal natural de comando

O símbolo residual tem três propriedades que o tornam um canal privilegiado:

**(a) Ele é raro.** Poucas ocorrências, ou nenhuma. Se o usássemos para dados, gastaríamos muito cabeçalho e ganharíamos pouco. Usá-lo para dados é ruim.

**(b) Ele é previsível.** O decodificador já sabe "o que sobrar é o residual". Isso significa que **o fato de uma posição ser residual já está decidido por omissão**. Um bit `0` no final do processo de planos **sempre** significa "residual aqui".

**(c) Ele é implícito.** Não há plano próprio para o residual na versão 1. A ausência de plano é um espaço semântico vazio — onde a gramática do formato não diz nada. Esse vazio pode ser preenchido com uma convenção extra sem romper nada do que já funciona.

A conclusão é que o símbolo residual pode deixar de ser "o que sobra" e passar a ser **o gatilho de um canal paralelo de instruções**.

---

## 6. O resíduo como comando — a mecânica

Eis a mudança de regime da versão 2:

> **Uma posição residual no fluxo não significa mais "aqui é σ_m". Significa "aqui o decodificador entra em modo comando e lê a próxima instrução do canal de programa".**

A partir dessa troca, temos dois fluxos no arquivo:

1. **Fluxo de planos** — os planos P₁, P₂, …, P_{m−1}, como antes. Cada posição `1` é resolvida imediatamente pelo símbolo do rank correspondente.
2. **Fluxo de programa** — uma sequência de instruções. Começa vazio. Sempre que o decodificador chega a uma posição sem plano a marcando, ele consome a próxima instrução do fluxo de programa.

O fluxo de programa é codificado no lugar que antes seria ocupado pelo símbolo residual. Na prática, isso significa que a gente pode (e às vezes deve) **emitir planos mais curtos do que o necessário para cobrir todas as posições**, porque posições não cobertas passam a ser consumidas pelo programa.

Isso é o que os 7 bits de P₁ hipotéticos da Seção 4 significam: P₁ cobre explicitamente as 4 primeiras posições, e as 3 últimas são gatilhos para instruções.

---

## 7. Uma linguagem mínima de comandos

A linguagem não precisa ser rica nesta primeira formulação. Quatro operações já dão conta de cobrir repetição, referência e cópia:

| Opcode | Nome         | Operandos                          | Semântica |
|--------|--------------|------------------------------------|-----------|
| `R`    | **REPEAT**   | símbolo `s`, contagem `n`          | Escreve `s` nas próximas `n` posições do fluxo de saída |
| `J`    | **JUMP**     | offset `d`, comprimento `l`        | Copia `l` posições a partir da posição atual menos `d` (análogo a LZ77) |
| `L`    | **LITERAL**  | bits `b₁ b₂ … b_j`                 | Escreve os bits literais na saída, sem interpretação |
| `E`    | **END**      | —                                  | Marca o fim do programa |

Quatro opcodes cabem em 2 bits. Os operandos herdam o formato comum: contagens e offsets em Elias-gamma ou código de Golomb, comprimento em binário simples, literais em bruto.

Essa linguagem é voluntariamente pobre. Ela é o **esqueleto**. Mais tarde podemos adicionar:

- `CALL` — executar um subprograma armazenado no cabeçalho (gramática).
- `SHIFT` — aplicar uma transformação ao resultado de outro comando.
- `PLANE` — instruir o decodificador a abrir um sub-plano recursivo.

Mas essas são extensões. Por enquanto, quatro opcodes.

---

## 8. Exemplo trabalhado — versão 2

Voltemos aos dados originais. Lembre-se do ranking:

```
σ₁ = 01    σ₂ = 10    σ₃ = 11    σ₄ = 00 (residual = canal de comando)
```

E da estrutura original:

```
pos:    0  1  2  3  4  5  6  7  8  9 10 11 12 13
sym:   10 01 10 01 10 01 01 01 01 01 01 01 01 11
```

### Estratégia 1 — planos curtos, comando suplementar

Olhe para o trecho `01 01 01 01 01 01 01 01` nas posições 5 a 12. É monótono: oito `01`s em sequência. Em vez de emitir oito `1`s no plano P₁, emitimos a máscara só até a posição 4 e usamos um comando `REPEAT(01, 8)` para cobrir o trecho monótono:

```
P₁ (curto):    0 1 0 1 0                             (5 bits — cobre posições 0..4)

               posição 5 não tem marcação → vira gatilho de programa
               comando lido: REPEAT(σ₁=01, n=8) → preenche 5..12

P₂:            1 1 1 0                               (4 bits — cobre posições restantes 0, 2, 4, 13)
P₃:            0 0 0 1                               (4 bits — só a posição 13 é 11)
σ₄:            nenhuma posição residual neste exemplo
```

Fluxo de programa: `REPEAT(01, 8) | END`.

Em bits simbólicos: 5 (P₁) + 4 (P₂) + 4 (P₃) + programa. O programa gasta, digamos, 2 bits de opcode + 2 bits de símbolo + Elias-gamma(8) ≈ 7 bits ≈ 11 bits de programa + END.

Total aproximado: 5 + 4 + 4 + 11 ≈ 24 bits. Pior que a versão 1 neste caso microscópico, porque o custo do comando excede a economia dos planos. Mas esse é um efeito esperado em exemplos muito pequenos: o overhead do programa domina. A ideia se paga em fluxos longos, onde um único comando cobre grandes trechos.

### Estratégia 2 — comando para padrões distantes

Imagine que o fluxo, mais adiante, tivesse o trecho `10 01 10 01 10` repetido. Os planos capturariam isso como máscaras alternadas, caras. Um comando `JUMP(offset=18, length=10)` carregaria o mesmo trecho por referência, ao custo fixo de um offset e um comprimento. A economia cresce com o comprimento do match.

### Estratégia 3 — residual como marcador

Aqui entra a leitura original do documento: se o residual (`00`) aparecer apenas como marcador, sem dados semânticos próprios, podemos reservar seu lugar para orquestrar outros planos. O plano P_4 (que na versão 1 não existia) passa a ser uma lista de instruções, e cada ocorrência residual é uma chamada para a próxima instrução.

Todas as três estratégias compartilham o mesmo princípio: **posições ausentes dos planos disparam leitura de comando**.

---

## 9. Por que "Turing"

Na versão 1, o decodificador é puramente reativo. Ele lê bits e preenche posições numa tabela. É equivalente a uma máquina de estados finitos.

Na versão 2, o decodificador executa um programa. O programa tem loops (REPEAT), saltos (JUMP), literais (LITERAL), terminação (END). Um decodificador desses pode, em princípio, simular qualquer computação computável com memória suficiente.

O nome **TuringBitCompression** registra essa mudança de estatuto: o arquivo comprimido não é mais uma codificação passiva, é um programa que, quando executado, reconstrói os dados. Essa é a mesma intuição por trás da compressão fractal (IFS como programa que converge para a imagem), da complexidade de Kolmogorov (comprimento do menor programa que gera os dados) e, do lado prático, do MDL (Minimum Description Length).

A diferença é que o TBC chega lá por um caminho concreto: o residual do ranking de frequência é o lugar natural de injetar instruções sem quebrar a economia da codificação por planos.

---

## 10. Recursão

Cada plano é em si um fluxo de bits. Nada impede que o TBC seja aplicado recursivamente a cada plano:

```
S → TBC → (ranking, P₁, P₂, …, P_{m−1}, programa)
P₁ → TBC → (ranking_P1, P₁.₁, P₁.₂, …, programa_P1)
P₂ → TBC → …
```

Na prática, a recursão só vale a pena se o plano tiver entropia menor que o overhead adicional (ranking + programa interno). Como os planos de símbolos frequentes são muito desbalanceados (quase toda `1` para σ₁, quase toda `0` para símbolos raros), há motivo para acreditar que a recursão paga seu custo.

A regra prática para o protótipo é: recurse se `tamanho(TBC(P)) < tamanho(P)`; pare quando essa condição falhar.

---

## 11. O que interessa testar antes de falar de qualidade

O documento não se compromete com ganho de compressão. O protótipo atual ([`tbc.py`](tbc.py), [`test_tbc.py`](test_tbc.py)) já verifica a versão 1: round-trip lossless em dados aleatórios e controlados.

A versão 2 precisa, antes de comparar com compressores existentes, de três verificações de **processo**:

1. **Formalizar a linguagem.** Escrever a gramática dos comandos como BNF ou estrutura de dados Python. Saber exatamente o que o programa pode e não pode dizer.
2. **Round-trip com comandos.** Codificador que emite REPEAT/JUMP/LITERAL, decodificador que os executa, teste de igualdade com o original. Sem isso, nada do que se discute aqui é verificável.
3. **Política de escolha.** Regra explícita sobre quando emitir um comando em vez de um bit de plano. Pode começar com uma política míope (emite REPEAT sempre que o próximo símbolo se repete ≥ N vezes), e evoluir.

Quando esses três itens estiverem no lugar, a conversa sobre taxa, entropia e comparação com baselines faz sentido. Antes disso, não.

---

## 12. Glossário rápido

| Termo | Significado |
|-------|-------------|
| k     | bits por símbolo (alfabeto `2^k`) |
| σ_i   | símbolo de rank `i` (frequência descendente) |
| P_i   | plano de indicadores do símbolo σ_i |
| residual | o símbolo menos frequente; na v2, gatilho para o canal de comando |
| programa | fluxo de comandos codificado no espaço do residual |
| REPEAT / JUMP / LITERAL / END | opcodes mínimos da v0.3 |
| recursão | aplicar o TBC aos próprios planos |

---

## 13. Limites e problemas em aberto

- **Ambiguidade de gatilho.** Na v2, uma posição sem marcação pode vir de "o programa cobrirá" ou de "planos posteriores cobrirão". Falta regra clara para o decodificador distinguir. Possível solução: exigir que o residual seja emitido **antes** de qualquer outro plano, ou dedicar um único plano-marcador.
- **Custo do header.** A descrição dos comandos precisa caber num espaço pequeno para que a ideia tenha sentido em fluxos curtos. Em fluxos longos o custo amortiza.
- **Interação com recursão.** Se o plano recursivo também tiver comandos, o arquivo passa a ser uma árvore de programas. Gerenciável, mas precisa de metadados explícitos.
- **Decidibilidade de ganho.** Escolher emitir um comando em vez de bits de plano é um problema de busca. Uma política gulosa é trivial; uma política ótima é combinatorial.

Esses são os pontos a visitar depois que a v2 tiver um round-trip funcional.
