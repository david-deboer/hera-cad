try:
    from mpl_toolkits.basemap import pyproj
    basemapImported = True
except ImportError:
    print 'basemap not found'
    basemapImported = False

##############KML##################
def kmlplcmk(name,x,y,units='utm',zone=34):
    if units=='utm':
        lon,lat = utm2ll(x,y,zone)
    else:
        lon,lat = x,y
    kml = '	<Placemark>\n'
#    kml+= '             <name>%s</name>\n' % (name)
    kml+= '		<styleUrl>#point</styleUrl>\n		<Point>\n'
    kml+= '			<coordinates>%lf,%lf</coordinates>\n' % (lon,lat)
    kml+= '		</Point>\n	</Placemark>\n'
    return kml

def kmlhdr(name='HERA',pscale=0.4):
    kml = """<?xml version="1.0" encoding="UTF-8"?>"""
    kml+= """<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">"""
    kml+= """<Document>"""
    kml+= """    <Style id="point">"""
    kml+= """      <IconStyle>"""
    kml+= """        <scale>%.1f</scale>""" % (pscale)
    kml+= """        <Icon>"""
    kml+= """          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>"""
    kml+= """        </Icon>
          </IconStyle>
        </Style>
        <name>"""

    kml+= '%s</name>' % (name)
    return kml

def kmltrlr():
    kml = '</Document>\n</kml>\n'
    return kml

################Garmin#################
def garwypt(name,x,y,units='utm',zone=34):
    if units=='utm':
        lon,lat = utm2ll(x,y,zone)
    else:
        lon,lat = x,y
    gar = '\t<wpt lat="%lf" lon="%lf">\n' % (lat,lon)
    gar+= '\t\t<name>%s</name>\n' % (name)
    gar+= '\t\t<sym>Waypoint</sym>\n'
    gar+= '\t\t<type>user</type>\n'
    gar+= '\t\t<extensions>\n'
    gar+= '\t\t\t<gpxx:WaypointExtension>\n'
    gar+= '\t\t\t\t<gpxx:DisplayMode>SymbolAndName</gpxx:DisplayMode>\n'
    gar+= '\t\t\t</gpxx:WaypointExtension>\n'
    gar+= '\t\t</extensions>\n'
    gar+= '\t</wpt>\n'
    return gar

def garhdr(name='HERA'):
    gar = '<?xml version="1.0"?>\n'
    gar+= """<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxtrx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:trp="http://www.garmin.com/xmlschemas/TripExtensions/v1" xmlns:adv="http://www.garmin.com/xmlschemas/AdventuresExtensions/v1" xmlns:prs="http://www.garmin.com/xmlschemas/PressureExtension/v1" creator="Garmin Desktop App" version="1.1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v1 http://www8.garmin.com/xmlschemas/ActivityExtensionv1.xsd http://www.garmin.com/xmlschemas/AdventuresExtensions/v1 http://www8.garmin.com/xmlschemas/AdventuresExtensionv1.xsd http://www.garmin.com/xmlschemas/PressureExtension/v1 http://www.garmin.com/xmlschemas/PressureExtensionv1.xsd http://www.garmin.com/xmlschemas/TripExtensions/v1 http://www.garmin.com/xmlschemas/TripExtensionsv1.xsd">\n"""
    return gar
def gartrlr():
    gar = "</gpx>"
    return gar
    
###########Conversions################
if basemapImported:
    def utm2ll(x,y,zone=34):
        p = pyproj.Proj(proj='utm',zone=zone,south=True,ellps='WGS84')
        return p(x,y,inverse=True)

    def ll2utm(lon,lat):
        #lon needs to be between +/-180
        zone = (int((180 + lon) / 6.0) + 1) % 60
        print "ZONE:  ",zone
        #zone needs to be between 1 and 60
        centralMeridian = zone * 6 - 180 - 3
        south = False
        if lat < 0.0:
            south = True

        p = pyproj.Proj(proj='utm',zone=zone,south=south,ellps='WGS84')
        return p(lon,lat)
