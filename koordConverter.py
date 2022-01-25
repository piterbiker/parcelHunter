# python koordConverter.py "dzialka.txt"

import os
import sys

from konfig.dzialkiKonfig import (
    dns, schema, userpwd
    )
from funkcje.parcelHunter import main, oziGenerator, kmlGenerator
from funkcje.dzialkiFunkcje import (
    polaczenieOracleDns, show_dir
    )

# zrodlowy folder z plikami txt: pliki z koordynatami z geoportalu (SRID 2180)
folder = os.path.join(os.getcwd(), 'txt')
db = polaczenieOracleDns(dns.strip(), schema, userpwd)

if len(sys.argv) == 2:
    # jesli przy wywolaniu programu podany jest parametr w postaci nazwy pliku wejsciowego...
    inputFile =  sys.argv[1]
    main(db, inputFile)
else:   
    # wywolanie bez parametrow: wszystkie pliki txt w folderze [folder]
    plikod = show_dir(folder)

    for inputFile in plikod:
        if inputFile not in ('test.txt', 'kw.txt'):
            print()
            print(inputFile)
            # dla wejsciowych plikow txt:

            # dodaje rekordy do bazy
            main(db, inputFile)
   
            # jedynie generuje pliki OZI: dla istniejacych geometrri w bazie
            #oziGenerator(db, inputFile)

print( 'END parcel ' + 40*'-')

# generowanie zbiorczego pliku KML
kmlGenerator(db)
input ( 'END KML ' + 40*'-')

