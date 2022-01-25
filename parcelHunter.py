import os

from funkcje.dzialkiFunkcje import odd_indices, getAltitude, fileWrite

from konfig.dzialkiKonfig import (
    update, updateAlt, getKoord, getKmlData, getCentroidAlt, 
    plt_start, plt_body, wpt_start, wpt_body, 
    kml_start, kml_end, kml_body, kmlCoordTemplate, 
    Poland2000_header, Poland2000CoordTemplate
    )

def oziGenerator(db, filename):
    numerDzialki = filename.replace('.txt', '')
    
    wgs84Tab = []
    Poland2000Tab = []
    
    # tablice Lon i Lat (WGS84)
    tab3 = []
    tab4 = []

    # tablice X i Y (Poland2000)
    tab7 = []
    tab8 = []

    # pobieranie geometrii w postaci WGS84 w formacie tekstowym dla zaktualizowanej dzialki 
    try: 
        c3 = db.cursor()
        koord84 = getKoord.format(numerDzialki)
        c3.execute(koord84)
    except Exception as e:
        bladl = 'Blad :%s %s' % (e, koord84)   
        print(bladl)
        pass
    else:
        rezult = c3.fetchone()
        wgs84String = rezult[0]
        Poland2000String = rezult[1]
        
        # wrzucanie koordynatow WGS84 do tablicy
        wgs84Tab = wgs84String.split('|')
        Poland2000Tab = Poland2000String.split('|')
        lPunktow =  int((len(wgs84Tab))/2)

        # wypelnianie tablic z elementami Lat i Lon 
        tab3 = odd_indices(wgs84Tab, 0)
        tab4 = odd_indices(wgs84Tab, 1)

        tab7 = odd_indices(Poland2000Tab, 0)
        tab8 = odd_indices(Poland2000Tab, 1)

        # generowanie naglowkow plikow OziExplorer
        pltFile =  str(numerDzialki).strip()+'.plt'
        wptFile = str(numerDzialki).strip()+'.wpt'
        geoMaxFile = str(numerDzialki).strip()+'.txt'

        pltFileFull = os.path.join('shape', 'wpt', pltFile)
        wptFileFull = os.path.join('shape', 'wpt', wptFile)
        geoMaxFileFull = os.path.join('txtGeoMaxInput', geoMaxFile)

        # plt 
        fileWrite(pltFileFull, 'w', plt_start.format(numerDzialki, lPunktow))
        # wpt
        fileWrite(wptFileFull, 'w', wpt_start)
        # geoMax
        fileWrite(geoMaxFileFull, 'w', Poland2000_header)

        # generowanie  geometrii plikow OziExplorer
        for j in range(0, lPunktow):
            heightValue = getAltitude(tab4[j], tab3[j])

            # plt
            fileWrite(pltFileFull, 'a', plt_body.format(tab4[j], tab3[j]))
            #wpt
            fileWrite(wptFileFull, 'a', wpt_body.format(j+1, tab4[j], tab3[j]))
            #geoMax
            fileWrite(geoMaxFileFull, 'a', Poland2000CoordTemplate.format(j+1, tab8[j], tab7[j], heightValue))

        print(pltFile)               
        print(wptFile)
        print(geoMaxFile)


def main(db, filename):
    numerDzialki = filename.replace('.txt', '')

    # tablica wejsciowa: koordynaty zrodlowe z geoportalu, odwrocone
    sourceTab = []
    # tablica z odwroconymi w parach koordynatami (X z Y) 
    destTab = []
    # tablica z koordynatami po konwersji Oracle SDO_CS.TRANSFORM
    wgs84Tab = []
    
    # tablice X i Y
    tab1 = []
    tab2 = []
    
    # wejsciowy string do bazy: SDO_ORDINATES
    koords = ''

    with open(os.path.join('txt', filename)) as f:
        content = f.readlines()

    # do tabeli wejsciowej laduje tylko linie z koordynatami (puste i numeryczne Lp pomijam)
    for line in content:
        x = line.find(".")
        if x>1:
            sourceTab.append(line.strip())            

    # tworze tablice z elementami X i Y
    tab1 = odd_indices(sourceTab, 0)
    tab2 = odd_indices(sourceTab, 1)

    # odwracanie koordynatow
    for i in range(0, int(len(sourceTab)/2)):
        destTab.append( tab2[i])
        destTab.append( tab1[i])

    # skladanie koordynatow w ciag SDO_ORDINATES
    for koord in destTab:
        koords = koords+koord+',\n'

    # powielanie punktu poczatkowego na koniec (POLYGON)
    koords = koords + \
    destTab[0] + \
    ',\n' + destTab[1] 

    # zapisywanie pliku skryptu SQL
    savedStr = update.format(koords, numerDzialki)
    sqlFile = str(numerDzialki).strip()+'.sql'
    sqlFileFull = os.path.join('sql', 'generated', sqlFile)   
    
    fileWrite(sqlFileFull, 'w', savedStr)

    # aktualizacja geometrii dla dzialki
    try: 
        c2 = db.cursor()
        c2.execute(savedStr.replace(';', ''))
    except Exception as e2:
        updateErr = "Blad aktualizacji dzialki: {}: {}".format(numerDzialki, e2)
        print (updateErr)
    else:
        db.commit()
        print(numerDzialki)
    finally:
        # generuje pliki
        oziGenerator(db, filename)
        # aktualizuje wysokosc centroidu dzialki
        updateCentroidAlt(db, filename)       

        
def kmlGenerator(db):
    kmlFile = 'EGB_PJ_DZIALKI.kml'

    # tablice Lon i Lat (WGS84)
    tab5 = []
    tab6 = []

    try: 
        c5 = db.cursor()
        c5.execute(getKmlData)
    except Exception as e:
        bladl = 'Blad :%s %s' % (e, getKmlData)   
        print(bladl)
        pass
    else:
        # generowanie naglowkow pliku zbiorczego KML
        fileWrite(os.path.join('shape', kmlFile), 'w', kml_start)

        for row in c5:
            coordinatesString = ''

            # wrzucanie koordynatow WGS84 do tablicy
            wgs84Tab = row[3].split('|')
            lPunktow =  int((len(wgs84Tab))/2)

            # wypelnianie tablic z elementami Lat i Lon 
            tab5 = odd_indices(wgs84Tab, 0)
            tab6 = odd_indices(wgs84Tab, 1)

            # budowanie zawartosci <coordinates>
            for i in range(0, lPunktow):
                coordinatesString = coordinatesString + kmlCoordTemplate.format(tab5[i], tab6[i])

            # generowanie Placemarkow (Polygony) pliku zbiorczego KML
            fileWrite(os.path.join('shape', kmlFile), 'a', kml_body.format(row[1], row[0], row[2], coordinatesString))

            print(row[1])

        # generowanie EOF pliku zbiorczego KML
        fileWrite(os.path.join('shape', kmlFile), 'a', kml_end)

    finally:
        db.close()


def updateCentroidAlt(db, filename):
    numerDzialki = filename.replace('.txt', '')

    # pobieranie centroidu dzialki
    try: 
        c7 = db.cursor()
        centroidCoords = getCentroidAlt.format(numerDzialki)
        c7.execute(centroidCoords)
    except Exception as e:
        bladl = 'Blad :%s %s' % (e, centroidCoords)   
        print(bladl)
        pass
    else:
        coords = c7.fetchone()
        xCoord = coords[0]
        yCoord = coords[1]

        # pobieranie wysokosci centroidu
        heightCentroid = getAltitude(yCoord, xCoord)

        # aktualizacja wysokosci centroidu dzialki
        if int(heightCentroid) > 0:
            try: 
                c8 = db.cursor()
                c8.execute(updateAlt.format(int(heightCentroid), numerDzialki))
            except Exception as e8:
                updateErr = "Blad aktualizacji dzialki: {}: {}".format(numerDzialki, e8)
                print (updateErr)
            else:
                db.commit()
                print(heightCentroid)
     
