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

import math
import random
import sys
import xbmcgui
import resources.lib.mapsapi as mapsapi
import resources.lib.kodisettings as settings
import resources.lib.kodiutils as utils

_addonid = 'script.openstreetmap'

_action_move_left = 1
_action_move_right = 2
_action_move_up = 3
_action_move_down = 4
_action_page_up = 5
_action_page_down = 6
_action_select_item = 7
_action_previous_menu = 10
_action_zoom_out = 30
_action_zoom_in = 31
_action_nav_back = 92
_action_context_menu = 117

_map_max_zoom = 18
_map_min_zoom = 0

_control_maptype_image = 6002
_control_maptype_label = 6003
_control_marker = 6500
_control_zoom = 7000

_layer_type_standard = 0
_layer_type_cycle = 1
_layer_type_transport = 2
_layer_type_mapquest = 3
_layer_type_satellite = 4
_layer_type_hybrid = 5


class Coordinate:

    def __init__(self, row, column, zoom):
        self.row = row
        self.column = column
        self.zoom = zoom

    def __repr__(self):
        return '%d %d %d' % (self.row, self.column, self.zoom)

    def get_tile_url(self, layertype):
        subdomains = ['a', 'b', 'c']
        if layertype == _layer_type_standard:
            return 'http://%s.tile.openstreetmap.org/%d/%d/%d.png' % (subdomains[random.randint(0, 2)], self.zoom, self.column, self.row)
        elif layertype == _layer_type_cycle:
            return 'http://%s.tile.opencyclemap.org/cycle/%d/%d/%d.png' % (subdomains[random.randint(0, 2)], self.zoom, self.column, self.row)
        elif layertype == _layer_type_transport:
            return 'http://%s.tile2.opencyclemap.org/transport/%d/%d/%d.png' % (subdomains[random.randint(0, 2)], self.zoom, self.column, self.row)
        elif layertype == _layer_type_mapquest:
            return 'http://otile%d.mqcdn.com/tiles/1.0.0/map/%d/%d/%d.png' % (random.randint(1, 4), self.zoom, self.column, self.row)
        elif layertype == _layer_type_satellite:
            return 'http://otile%d.mqcdn.com/tiles/1.0.0/sat/%d/%d/%d.png' % (random.randint(1, 4), self.zoom, self.column, self.row)
        elif layertype == _layer_type_hybrid:
            return 'http://otile%d.mqcdn.com/tiles/1.0.0/hyb/%d/%d/%d.png' % (random.randint(1, 4), self.zoom, self.column, self.row)


class OpenStreetMap(xbmcgui.WindowXML):

    def __init__(self, xml, path, **kwargs):
        xbmcgui.WindowXML(xml, path)
        self._settings = settings.Settings(_addonid, sys.argv)
        self._initialised = False
        self._home_lat_deg = self._lat_deg = kwargs['lat_deg']
        self._home_lon_deg = self._lon_deg = kwargs['lon_deg']
        self._zoom = kwargs['zoom']
        self._layertype = kwargs['layertype']
        self._centre_tilex, self._centre_tiley, self._home_pixelx, self._home_pixely = self.deg2num(
            self._lat_deg, self._lon_deg, self._zoom)
        self._home_column = self._centre_tilex
        self._home_row = self._centre_tiley

    def onAction(self, action):
        actionid = action.getId()
        # if actionid != 107:
        #    print 'onAction: %s' % actionid

        if actionid == _action_previous_menu or actionid == _action_nav_back:
            self.close()

        elif actionid == _action_select_item:
            if self._layertype == _layer_type_hybrid:
                self._layertype = 0
            else:
                self._layertype += 1
            self.set_tiles()

        elif actionid == _action_move_left or actionid == _action_move_right or actionid == _action_move_up or actionid == _action_move_down:
            if actionid == _action_move_left:
                self._centre_tilex -= 1
            elif actionid == _action_move_right:
                self._centre_tilex += 1
            elif actionid == _action_move_up:
                self._centre_tiley -= 1
            elif actionid == _action_move_down:
                self._centre_tiley += 1
            self._lat_deg, self._lon_deg = self.num2deg(
                self._centre_tilex, self._centre_tiley, self._zoom)
            self.set_tiles()

        elif actionid == _action_page_up or actionid == _action_page_down:
            if actionid == _action_page_up:
                if self._zoom < _map_max_zoom:
                    self._zoom += 1
            elif actionid == _action_page_down:
                if self._zoom > _map_min_zoom:
                    self._zoom -= 1
            self._centre_tilex, self._centre_tiley, self._home_pixelx, self._home_pixely = self.deg2num(
                self._lat_deg, self._lon_deg, self._zoom)
            self._home_column, self._home_row, self._home_pixelx, self._home_pixely = self.deg2num(
                self._home_lat_deg, self._home_lon_deg, self._zoom)
            self.set_tiles()

        elif actionid == _action_context_menu:
            query = utils.keyboard('', heading=self._settings.get_string(3001))
            if query and len(query) > 0:
                if self._settings.get('api') == 0:
                    osm = mapsapi.OpenStreetMapApi()
                else:
                    osm = mapsapi.MapQuestOpenApi()
                response = osm.search(query)
                if len(response) > 0:
                    index = 0
                    if len(response) > 1:
                        displaynames = []
                        for result in response:
                            displaynames.append(result['display_name'])
                        index = utils.select(self._settings.get_string(3002), displaynames)
                    if index >= 0 and index < len(response):
                        self._home_lat_deg = self._lat_deg = float(
                            response[index]['lat'])
                        self._home_lon_deg = self._lon_deg = float(
                            response[index]['lon'])
                        self._centre_tilex, self._centre_tiley, self._home_pixelx, self._home_pixely = self.deg2num(
                            self._lat_deg, self._lon_deg, self._zoom)
                        self._home_column = self._centre_tilex
                        self._home_row = self._centre_tiley
                        self.set_tiles()
                else:
                    utils.ok(self._settings.get_string(3000), self._settings.get_string(3003) % query, self._settings.get_string(3004))

    def onFocus(self, controlId):
        # print 'onFocus: %d' % controlId
        pass

    def onInit(self):
        # print 'onInit'
        if not self._initialised:
            self.set_tiles()
            self._initialised = True

    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = (lon_deg + 180.0) / 360.0 * n
        ytile = (1.0 - math.log(math.tan(lat_rad) + (
            1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
        return (int(xtile), int(ytile), int(round((xtile - int(xtile)) * 256)), int(round((ytile - int(ytile)) * 256)))

    def num2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def set_tiles(self):
        if self._layertype == 0:
            self.getControl(_control_maptype_label).setLabel(
                self._settings.get_string(2011))
            self.getControl(_control_maptype_image).setImage('map.png')
        elif self._layertype == 1:
            self.getControl(_control_maptype_label).setLabel(
                self._settings.get_string(2012))
            self.getControl(_control_maptype_image).setImage('map.png')
        elif self._layertype == 2:
            self.getControl(_control_maptype_label).setLabel(
                self._settings.get_string(2013))
            self.getControl(_control_maptype_image).setImage('map.png')
        elif self._layertype == 3:
            self.getControl(_control_maptype_label).setLabel(
                self._settings.get_string(2003))
            self.getControl(_control_maptype_image).setImage('map.png')
        elif self._layertype == 4:
            self.getControl(_control_maptype_label).setLabel(
                self._settings.get_string(2004))
            self.getControl(_control_maptype_image).setImage('sat.png')
        else:
            self.getControl(_control_maptype_label).setLabel(
                self._settings.get_string(2010))
            self.getControl(_control_maptype_image).setImage('sat.png')

        markercolour = self._settings.get('markercolour')
        if markercolour == 1:
            markercolour = 'green'
        elif markercolour == 2:
            markercolour = 'red'
        elif markercolour == 3:
            markercolour = 'yellow'
        else:
            markercolour = 'blue'

        self.getControl(_control_zoom).setPosition(
            0, ((18 - self._zoom) * 10) + 22)

        tiles_columns = [1, 2, 3, 4, 5, 6, 7, 8]
        tiles_rows = [1, 2, 3, 4, 5]

        control = self.getControl(_control_marker)
        control.setImage('')
        for row in tiles_rows:
            for column in tiles_columns:
                coordinate = Coordinate(self._centre_tiley + (row - (len(
                    tiles_rows) / 2)), self._centre_tilex + (column - (len(tiles_columns) / 2)), self._zoom)

                self.getControl((row * 1000) + column).setImage(coordinate.get_tile_url(
                    self._layertype) if self._layertype != _layer_type_hybrid else coordinate.get_tile_url(_layer_type_satellite))
                self.getControl((row * 1000) + column + 500).setImage(coordinate.get_tile_url(
                    _layer_type_hybrid) if self._layertype == _layer_type_hybrid else '')

                if self._home_column == coordinate.column and self._home_row == coordinate.row:
                    control.setPosition(((column - 1) * 256) + self._home_pixelx - 12, (
                        (row - 1) * 256) + self._home_pixely - 41)
                    control.setImage('marker-%s.png' % markercolour)

    def close(self):
        super(OpenStreetMap, self).close()
