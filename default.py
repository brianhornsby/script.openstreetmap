#/*
# *
# * OpenStreetMap for Kodi
# *
# * Copyright (C) 2015 Brian Hornsby
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */

import simplejson
import sys
import urllib2
import resources.lib.mapsapi as mapsapi
import resources.lib.xbmcsettings as settings
import resources.lib.openstreetmap as openstreetmap

# Set some global values.
_addonid = 'script.openstreetmap'

# Initialise settings.
_settings = settings.Settings(_addonid, sys.argv)

# Get addon information.
_path = _settings.get_path()

# Get addon settings values.
_home = _settings.get('home')
_api = _settings.get('api')
_zoom = int(_settings.get('zoom'))
_layertype = int(_settings.get('layertype'))


def log_debug(msg):
    if _settings.get('debug') == 0:
        print '%s: DEBUG: %s' % (_addonid, msg)


def get_geolocation():
    try:
        url = 'http://api.ipinfodb.com/v3/ip-city/?key=24e822dc48a930d92b04413d1d551ae86e09943a829f971c1c83b7727a16947f&format=json'
        req = urllib2.Request(url)
        f = urllib2.urlopen(url)
        response = f.read()
        f.close()
        return simplejson.loads(response)
    except:
        return None


if (__name__ == '__main__'):
    log_debug('Path: %s' % _path)
    log_debug('Home: %s' % _home)

    response = get_geolocation()
    city = response['cityName'] if response else ''
    region = response['regionName'] if response else ''
    country = response['countryName'] if response else ''

    if _home is None or len(_home) == 0:
        _home = None
        if len(city) > 0 and city != '-':
            _home = city
        if len(region) > 0 and region != '-':
            if _home is None:
                _home = region
            else:
                _home = '%s, %s' % (_home, region)
        if len(country) > 0 and country != '-':
            if _home is None:
                _home = country
            else:
                _home = '%s, %s' % (_home, country)

    if _home is None or len(_home) == 0:
        _home = 'Cadnam, Hampshire, UK'

    if _api == 0:
        osm = mapsapi.OpenStreetMapApi()
    else:
        osm = mapsapi.MapQuestOpenApi()
    response = osm.search(_home)
    if len(response) > 0:
        lat_deg = float(response[0]['lat'])
        lon_deg = float(response[0]['lon'])

    openstreetmap = openstreetmap.OpenStreetMap(
        'openstreetmap.xml', _path, lat_deg=lat_deg, lon_deg=lon_deg, zoom=_zoom, layertype=_layertype)
    openstreetmap.doModal()
    del openstreetmap
