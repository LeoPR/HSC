# 05. Codificacao Entropica

## Papel no compressor

E a etapa que realmente converte simbolos em bits de forma proxima ao limite teorico de entropia de Shannon.

## Principais familias

### Huffman

- Simples, muito difundido.
- Excelente baseline.
- Menos eficiente quando probabilidades nao sao proximas de potencias de 2.

### Aritmetica/Range Coding

- Geralmente mais proxima da entropia para modelos probabilisticos ricos.
- Muito boa para integrar com modelos adaptativos/contextuais.

### ANS (Asymmetric Numeral Systems)

- Compete em eficiencia com aritmetica e pode ter desempenho muito alto.
- Bastante usado em codificadores modernos.

## Principio global

Sem modelagem estatistica boa, ate o melhor codificador entrópico perde desempenho. Modelagem + codificacao caminham juntas.
