maphearder
cabecalho no arquivo compression_logic_01.md


raw_data - 10011001100101010101010101
raw_data - 1001100110010 1010101010101
raw_data - 100110 0 110010 101010 1 010101
raw_data - 100 110 0 110 010 101 010 1 010 101
raw_data - 10 01 10 01 10 01 01 01 01 01 01 01 01
raw_data -    0     0     0  0  0  0  0  0  0  0 
raw_data - 1     1     1                         
raw_data -  0     0     0                        
raw_data -     1     1     1  1  1  1  1  1  1  1
group
00 - 0 vezes
01 - 10 vezes
10 - 3 vezes
11 - 0 vezes

0 = 01
1 - 10

comp_data lv 1 - 1 0 1 0 1 0 0 0 0 0 0 0 0
comp_data lv 1 - 10 10 10 00 00 00 0
group
10 - 3 vezes
00 - 3 vezes
resto 0
0 = 10
1 = 00

comp_data lv 2 - 0 0 0 1 1 1 0
comp_data lv 2 - 00 01 11 0
group
00 - 1 vezes
01 - 1 vez
11 - 1 vez
resto 0
0 = 00
10 = 01
11 - 11

comp_data lv 3 - 0 10 11 0
comp_data lv 3 - 01 01 10
group
01 - 2 vezes
10 - 1 vez

0 = 01
1 - 10

comp_data lv 3 - 0 1 1