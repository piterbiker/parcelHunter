import os
import srtm
import cx_Oracle

from konfig.dzialkiKonfig import hgtFolder

def polaczenieOracleDns(dns, schema, userpwd):
    try:
        db = cx_Oracle.connect(schema, userpwd, dns, encoding='UTF-8')
    except Exception as e:
        bladl = 'Blad polaczenia %s:\n%s' % (conn_str, e.message)   
        input(bladl)
        db = None
    else:       
        print (db.version)
    finally:
        return db


def odd_indices(lst, pier):
    # funkcja zwracajaca z listy [lst] tylko parzyste lub nieparzyste elementy
    # w zaleznosci od parametru [pier] (wartosci 0 lub 1) 
    odd_indice = []
    for index in range(pier, len(lst), 2):
        odd_indice.append(lst[index])
    return odd_indice


def show_dir(path):
    # funkcja wrzucajaca do tablicy elementy folderu
    # z podanym w funkcji rozszerzeniem
    nodes = []
    for file in os.listdir(path):
        if file.endswith(".txt"):
            nodes.append(file)

    return nodes


def getAltitude(long, lat):
    elevation_data = srtm.get_data(local_cache_dir=hgtFolder)
    heightValue = elevation_data.get_elevation(long, lat)

    return heightValue


def fileWrite(fname, openType, saveStr):
    with open(fname, openType) as file:
        file.write(saveStr)