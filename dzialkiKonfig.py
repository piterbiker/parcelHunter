import os

dns = '(DESCRIPTION =    (ADDRESS = (PROTOCOL = TCP)(HOST = user-Komputer)(PORT = 1521))    (CONNECT_DATA =      (SERVER = DEDICATED)      (SERVICE_NAME = XE)    )  )'
schema = 'PJARCZAK'
userpwd = ''

hgtFolder = os.path.join('D:\\', 'Dokumenty', 'mapy', 'elevation', 'hgt')
geoMaxSep = ';'

insert = '''INSERT INTO EGB_PJ_DZIALKI (NUMER, KW, TYP, ID_OGLOSZENIA) VALUES ('{}.{}', '{}', '{}', '{}');
'''

update = '''update EGB_PJ_DZIALKI
set shape = 
  SDO_GEOMETRY(
    2003,  
    2180,  
    NULL,
    SDO_ELEM_INFO_ARRAY(1,1003,1), 
    SDO_ORDINATE_ARRAY(
{}
)
  )
where numer = replace('{}', '^', '/')
and shape is null
;
'''

updateAlt = '''update EGB_PJ_DZIALKI
set centroid_alt = {}
where numer = replace('{}', '^', '/')
and nvl(centroid_alt, 0) = 0
'''

# -----------------------------------------------------------------------------------
# POBIERANIE GEOMETRII

# nieuzywane: nastepne zapytanie jest aktualne
getKoordOld = '''with dane as (SELECT
    SDO_CS.TRANSFORM(g.shape, 4236) as GEOM_WGS84
FROM
    egb_pj_dzialki g
    where g.numer = replace('{}', '^', '/')
)
    select d.GEOM_WGS84.sdo_ordinates from dane d
'''

# pobieranie geometrii dzialki na potrzeby importu do urzadzenia GPS
# dynamiczne pobieranie strefy dla ETRS89 / Poland CS2000

# select * from sdo_coord_ref_sys where upper(COORD_REF_SYS_NAME) like '%LONG%WGS 84%';
getKoord = '''
select 
    replace(GeomToString(SDO_CS.TRANSFORM(d.shape, 8307)), ',', '.') as wg, 
    replace(GeomToString(SDO_CS.TRANSFORM(d.shape, p.srid)), ',', '.') as pol, 
    substr(k.coord_ref_sys_name, -1) as zone
from EGB_PJ_DZIALKI d
left outer join egb_pj_licytacje l on d.id_licytacji = l.id
left outer join egb_pj_ogloszenia o on d.id_ogloszenia = o.id
join egb_pj_miejscowosci m on coalesce(l.id_miejscowosci, o.id_miejscowosci) = m.id    
join egb_pj_powiaty p on m.id_powiatu = p.id
join sdo_coord_ref_sys k on p.srid = k.srid
where d.numer = replace('{}', '^', '/')
'''

# pobieranie geometrii wszystkich działek w WGS84
getKmlData = '''
select 
    id, 
    numer, 
    kw, 
    replace(GeomToString(SDO_CS.TRANSFORM(shape, 8307)), ',', '.') as koord
from EGB_PJ_DZIALKI
where shape is not null
and typ <> 'droga'
order by numer
'''

# pobieranie wysokosci centroida
getCentroidAlt = '''
SELECT 
    replace(SDO_GEOM.SDO_CENTROID(SDO_CS.TRANSFORM(c.shape, 8307), m.diminfo).sdo_point.x, ',', '.') as X, 
    replace(SDO_GEOM.SDO_CENTROID(SDO_CS.TRANSFORM(c.shape, 8307), m.diminfo).sdo_point.y, ',', '.') as Y
FROM EGB_PJ_DZIALKI c, user_sdo_geom_metadata m 
WHERE m.table_name = 'EGB_PJ_DZIALKI' AND m.column_name = 'SHAPE'
and c.numer = replace('{}', '^', '/')
'''

# -----------------------------------------------------------------------------------
# OziExplorer & KML files

# https://www.oziexplorer4.com/eng/help/fileformats.html
plt_start = '''OziExplorer Track Point File Version 2.1
WGS 84
Altitude is in Feet
Reserved 3
0, 2, 65280, {}, 1, 0, 0, 65280
{}
'''
plt_body = '''{},{},0,-777,,,\n'''

wpt_start = '''OziExplorer Waypoint File Version 1.0
WGS 84
Reserved 2
Reserved 3
'''
wpt_body = '''{0}, WP{0} , +{1},  +{2},, 18, 1, 5, 0, 13158342, , 0, 1, 3, -777, 6, 0,18,0,10.0,2,,,,0\n'''

kml_start = '''<?xml version="1.0" encoding="utf-8" ?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document id="root_doc">
<Schema name="EGB_PJ_DZIALKI" id="EGB_PJ_DZIALKI">
	<SimpleField name="Name" type="string"></SimpleField>
	<SimpleField name="ID" type="float"></SimpleField>
	<SimpleField name="KW" type="string"></SimpleField>
</Schema>
<Folder>
<name>EGB_PJ_DZIALKI</name>
'''

kml_end = '''</Folder>
</Document>
</kml>
'''

kml_body = '''
  <Placemark>
	<name>{}</name>
	<Style><LineStyle><color>FF1c1ae3</color><width>3</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>
	<ExtendedData><SchemaData schemaUrl="#EGB_PJ_DZIALKI">
		<SimpleData name="ID">{}</SimpleData>
		<SimpleData name="KW">{}</SimpleData>
	</SchemaData></ExtendedData>
      <Polygon><altitudeMode>clampToGround</altitudeMode><outerBoundaryIs><LinearRing><altitudeMode>clampToGround</altitudeMode><coordinates>{}</coordinates></LinearRing></outerBoundaryIs></Polygon>
  </Placemark>
'''

# sekwencja dla pary wspolrzednych w pliku KML
kmlCoordTemplate = '{},{},0 '

#GeoMax eksport
Poland2000_header = 'PTID;NORTH;EAST;HEIGHT\n'
Poland2000CoordTemplate = 4*('{}'+geoMaxSep)+'\n'




