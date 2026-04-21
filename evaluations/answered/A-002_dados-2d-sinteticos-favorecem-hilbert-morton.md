---
id: A-002
titulo: Dados 2D sintéticos com correlação local favorecem Hilbert/Morton sobre raster
categoria: empirico
prioridade: alta
criado: 2026-03-29
concluido: 2026-03-29
---

## Pergunta Original

Curvas de preenchimento de espaço (Hilbert, Morton) produzem menor entropia de modelo
de contexto do que raster em dados sintéticos com correlação espacial 2D local?

---

## Resposta

**Sim.** Em dados sintéticos construídos com correlação espacial 2D local (valores
próximos na grade tendem a ser similares), Morton e Hilbert superam raster em model_bps.
O pipeline E (busca exaustiva) seleciona Morton ou Hilbert como topologia ótima nesses casos.

---

## Evidências

### Experimento — Dataset sintético 2D com correlação local

Dados gerados com estrutura de blocos uniformes ou suavização espacial local (pixels
vizinhos com valores similares), formatados como grade 2D e serializados.

| Topologia | Resultado relativo |
|-----------|-------------------|
| A — Raster | model_bps mais alto |
| B — Morton | model_bps menor que raster |
| C — Hilbert | model_bps menor que raster |
| E — Melhor | seleciona Morton ou Hilbert |

*Margem observada:* Morton e Hilbert mostraram ganho positivo sobre raster (magnitude
não documentada precisamente — ver limitação abaixo).

### Mecanismo Explicativo

```
Dados 2D com correlação local:
  valor(x,y) ≈ valor(x±1, y) ≈ valor(x, y±1)

Raster serializa: (0,0),(1,0),(2,0),...,(0,1),(1,1),...
  → salto da linha: (n-1,0) → (0,1) são distantes na grade 2D
  → P(s_t | s_{t-1}) não captura correlação entre linhas adjacentes

Hilbert serializa preservando vizinhança 2D local:
  → s_{t-1} e s_t tendem a ser 2D-vizinhos
  → P(s_t | s_{t-1}) captura mais redundância
  → model_bps menor
```

---

## Conclusão Científica

Dados com estrutura de correlação espacial 2D local (onde a similaridade entre
posições é função da distância na grade, não da posição linear) são favorecidos por
curvas de preenchimento de espaço. O efeito é observável via modelo de contexto de
ordem 1 como redução de model_bps.

**Escopo de validade:** Este resultado foi demonstrado apenas com dados sintéticos
controlados. A generalização para dados reais (imagens, dados médicos) é a hipótese
central do projeto e ainda está em aberto — ver Q-003.

---

## Limitações do Experimento

1. **Dados sintéticos idealizados:** A correlação foi construída artificialmente com
   máxima uniformidade local. Dados reais têm bordas, texturas e ruído que podem
   atenuar o efeito.

2. **Magnitude não documentada com precisão:** Os resultados do sprint do protótipo
   não registraram os valores exatos de model_bps, apenas o ranking qualitativo.
   Para publicação, reproduzir com logging explícito de valores numéricos.

3. **Sem comparação de Morton vs. Hilbert:** Os dois superam raster, mas qual supera
   o outro varia. Morton é computacionalmente mais barato — se as margens são similares,
   Morton pode ser preferível para produção.

---

## Implicações para o Projeto

1. **Prova de princípio confirmada:** O mecanismo teórico funciona em condições
   controladas. Justifica prosseguir para Q-003 (dados reais).

2. **Morton é um baseline competitivo:** Não é apenas uma curva inferior ao Hilbert —
   em alguns casos sintéticos é equivalente ou melhor, com menor custo de índice.
   O paper deve incluir Morton como baseline forte, não apenas como comparação interna.

3. **O pipeline E funciona como esperado:** A busca adaptativa seleciona corretamente
   a topologia para o tipo de dado — validação do mecanismo de seleção.

---

## Referências

- Protótipo: `prototype/compare_orders.py` — pipelines A, B, C, E
- SIAC log: `docs/pesquisa/09_siac-mapa-pesquisa.md` (seção "Observações do protótipo")
- Teoria: `docs/pesquisa/02_curvas_preenchimento_de_espaco.md`
