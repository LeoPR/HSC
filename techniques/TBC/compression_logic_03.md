vamos supor que vamos comprimir os seguintes dados binários:

raw_data 1001100110010101010101010111
raw_data 10 01 10 01 10 01 01 01 01 01 01 01 01 11

pegamos uma recorrencia de 2 bits
total - 26 bits
00 - 0 vezes
01 - 10 vezes
10 - 3 vezes
11 - 1 vezes

começamos

comp_data lv 1 

01 - 0 1 0 1 0 1 1 1 1 1 1 0
10 - 1 1 1 0
11 - 1
00 -

aqui o 01 preenche onde 01 existe com 1, o 0 é incognita (pode ser 10 11 ou 00)
10 preenche na sequencia que o 01 com 1 só nos espaços que o 01 deixou com zero, e onde o 10 deixar zero, pode ser 11 ou 00
11 preenche as lacunas de 0 que o 10 deixou, no caso como só tinha 1 encerrou
00 é o resídu, se os 3 anteriores como o 01,10 e 11 preencheram tudo, não preciso colocar nada, pois o que sobrar só pode ser 00

repito o processo até não comprimir nada mais

