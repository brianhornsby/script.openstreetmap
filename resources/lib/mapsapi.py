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
import urllib
import urllib2


class request():

    def __init__(self,  apiurl=None, endpoint=None, method='get'):
        self.endpoint = endpoint
        self.method = method
        self.apiurl = apiurl

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            params = func(*args, **kwargs) or {}
            url = self.endpoint if self.endpoint else params.pop('url')
            params = urllib.urlencode(params)
            url = "%s%s?%s" % (self.apiurl, url, params)
            headers = {'User-Agent': 'OpenStreetMap for Kodi'}
            req = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(url).read()
            return simplejson.loads(response)
        return wrapped


class OpenStreetMapApi:

    @request('http://nominatim.openstreetmap.org/', 'search')
    def search(self, query):
        return {
            'q': query,
            'format': 'json'
        }


class MapQuestOpenApi:

    @request('http://open.mapquestapi.com/nominatim/v1/', 'search.php')
    def search(self, query):
        return {
            'q': query,
            'format': 'json'
        }
