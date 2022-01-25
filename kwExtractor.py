# -*- coding: utf-8 -*-

import os
from dzialkiKonfig import insert

# dane wejsciowe
numerOgloszenia = input('Numer ogloszenia:\t')
numerObszaruEw = input('Numer obszaru EW:\t')
kW = input('KW:\t')

# tablica numerow dzialek
numeryTab = []
# tablica sposobu wykorzystanai dzialki
wykorzystanieTab = []

sqlFile = 'dzialkiInserty.sql'
textFile = 'dzialkiInserty.txt'

# yworzenie/kasowanie plikow
with open(os.path.join('sql', sqlFile), "w") as file:
    file.write('')
with open(os.path.join('sql', textFile), "w") as file:
    file.write('')

# ladowanie do pamieci zawartosci pliku z KW
with open(os.path.join('txt', 'kw.txt'), encoding="utf8") as f:
    content = f.readlines()

# szukanie w pliku KW linii (ze znakami PL):
#   Numer dzialki 
#   Sposob korzystania
for line in content:
    x = line.find('Numer')
    y = line.find('korzystania')

    # budowanie tablicy z numerami dzialek
    if x>-1:
        numeryTab.append(
            line[int(line.find('\t')):int(line.find('\t1'))].strip()
        )    

    # budowanie tablicy ze sposobem wykorzystania
    if y>-1:
        wykorzystanieTab.append(
            line[int(line.find('\t')):int(line.find('\n'))].strip()
        )    

lDzialek =  int(len(numeryTab))
lWykorzystania =  int(len(wykorzystanieTab))

# tworzenie pliku SQL z insertami dzialek
for j in range(0, lDzialek):
    numerDzialki = '{}.{}'.format(numerObszaruEw, numeryTab[j])
    if lDzialek == lWykorzystania:
        wykorzystanie = wykorzystanieTab[j].lower().capitalize()
    else:
        wykorzystanie = ''

    with open(os.path.join('sql', sqlFile), "a") as file:
        file.write(insert.format(numerObszaruEw, numeryTab[j], kW, wykorzystanie, numerOgloszenia))

    with open(os.path.join('sql', textFile), "a") as file:
        file.write(numerDzialki+'\n')

    with open(os.path.join('txt', numerDzialki.replace('/', '^')+'.txt'), "a") as file:
        file.write('')