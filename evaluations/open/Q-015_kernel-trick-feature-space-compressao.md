---
id: Q-015
titulo: Kernel trick (SVM) como projecao de feature space para compressao
categoria: teoria
prioridade: media
criado: 2026-04-04
relacionado: [Q-008, Q-010, Q-011]
---

## Pergunta

Tecnicas de kernel (como usadas em SVM) podem ser aplicadas para projetar dados
em espacos de features de alta dimensao onde padroes de compressibilidade
emergem — especificamente, separando regioes de alta/baixa entropia que possam
ser codificadas de forma diferenciada?

---

## Contexto e Intuicao

O kernel trick do SVM resolve um problema analogo ao da compressao: dados que
nao sao linearmente separaveis no espaco original podem ser separados ao
projeta-los num espaco de dimensao superior via funcao kernel K(x, y) = <phi(x), phi(y)>.

**Analogia com compressao:**
- No SVM: dados inseparaveis em R^d → separaveis em R^D (D >> d)
- Na compressao: dados incompressiveis na ordem original → compressiveis num
  espaco transformado

A hipotese e que kernels poderiam classificar/agrupar regioes dos dados de
forma que:
1. Regioes similares (baixa entropia relativa) ficam proximas
2. Regioes dissimilares (fronteiras, ruido) ficam distantes
3. A ordenacao de traversal pelo espaco projetado produz uma sequencia
   mais compressivel que a original

---

## Tipos de Kernel Relevantes

| Kernel | Formula | Aplicacao potencial para compressao |
|--------|---------|-------------------------------------|
| RBF (Gaussiano) | K(x,y) = exp(-gamma * ||x-y||^2) | Agrupa bytes similares em vizinhancas suaves |
| Polinomial | K(x,y) = (x.y + c)^d | Captura interacoes de ordem d entre bytes |
| Spectral | K baseado em autovalores de Laplaciano | Agrupa por componentes espectrais |
| String kernel | K baseado em substrings comuns | Mede similaridade entre segmentos |
| Diffusion kernel | K baseado em caminhadas aleatorias em grafo | Conecta a topologia do dado |

---

## Conexoes com o Framework HSC

### Com Q-008 (Perspectivas de Feature Space)
- Kernel = instancia de **P1 (remapear para visualizar)** + **P5 (dobrar espaco)**
- O espaco projetado por phi(x) e um "Hilbert space" no sentido matematico
  (espaco de Hilbert = espaco vetorial com produto interno completo)
- Conexao direta: SFC no espaco original vs. SFC no espaco projetado

### Com Q-010 (Fold-XOR)
- Kernels poderiam definir a permutacao sigma* da dobragem:
  sigma_kernel(x) = ordenacao dos dados pela projecao em componentes do kernel
- Match aproximado no espaco do kernel: dois blocos sao "similares" se
  K(bloco_i, bloco_j) > threshold

### Com Q-011 (Homeomorfismo Topologico)
- A funcao phi do kernel e um homeomorfismo do espaco original para o espaco
  de features — exatamente a funcao phi: C -> D do framework topologico
- A diferenca: phi do kernel e implicita (kernel trick), enquanto phi do
  homeomorfismo precisa ser explicita para decodificacao

---

## Problemas e Limitacoes

1. **Decodificacao:** O kernel trick e implicito — nao computa phi(x) explicitamente,
   apenas K(x,y). Para compressao, precisamos da projecao explicita para reconstruir
   os dados. Isso limita a classes de kernels com phi computavel (ex: Nystrom
   approximation, Random Fourier Features).

2. **Custo computacional:** Kernel matrix NxN para N bytes e O(N^2) — proibitivo
   para datasets grandes. Aproximacoes necessarias.

3. **Overhead de descricao:** Armazenar os parametros do kernel + a projecao no
   arquivo comprimido adiciona overhead. MDL precisa ser favoravel.

4. **Nao esta claro que supere metodos simples:** Modelos de contexto adaptativos
   (PPM, context mixing) ja capturam dependencias complexas sem projecao explicita.
   O kernel precisaria oferecer algo que esses metodos nao oferecem.

---

## Hipoteses a Investigar

**H1 (classificacao de regioes):** Um classificador kernel aplicado a janelas
deslizantes dos dados pode segmentar o input em regioes de alta/baixa entropia,
permitindo codificacao diferenciada (similar a codificacao por contexto).

**H2 (ordenacao por kernel):** Reordenar os dados pela projecao no primeiro
componente principal do espaco do kernel (kernel PCA) produz uma sequencia
com menor entropia condicional que a ordem original.

**H3 (distancia kernel para matching):** Usar distancia no espaco do kernel
como criterio de matching aproximado (Q-010) melhora a qualidade das dobras
comparado com Hamming distance direta.

---

## Trabalhos Relacionados (a verificar)

- Random Fourier Features (Rahimi & Recht, 2007) — aproximacao explicita de kernels
- Kernel PCA para reducao de dimensionalidade (Scholkopf et al., 1998)
- String kernels para analise de sequencias (Lodhi et al., 2002)
- Compressed sensing via kernel methods
- Kernel methods for lossy compression (possivelmente em rate-distortion theory)

---

## Prioridade e Momento

**Agora:** Apenas registrar a hipotese. Nao implementar.

**Depois de Sprint 2 (Q-010 fold-XOR):** Se o framework de dobragem mostrar que
a escolha de sigma* importa significativamente, kernels sao uma forma principiada
de definir sigma* via projecao de feature space. Nesse caso, implementar H2 como
experimento.

**Para o paper:** Se Q-010 for a contribuicao central, kernel trick e um
"future work" natural e fortalece o posicionamento teorico.

---

## Criterio de Conclusao

- **Para fechar como investigada:** Revisar literatura de kernel methods aplicados
  a compressao. Se existir trabalho substancial, documentar e fechar como A-015
  com estado da arte mapeado.
- **Para promover a experimento:** Se a revisao mostrar lacuna (nenhum codec usa
  kernel trick), criar experimento minimo com kernel PCA + reordenacao.
