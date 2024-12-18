# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OpenGoogleMaps
                                 A QGIS plugin
 Opens the current map extent in Google Maps
                              -------------------
        begin                : 2024-12-17
        copyright            : (C) 2024 Harry King
        email                : nlu1vwm0@anonaddy.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

###

Initialises the plugin

###

"""

# Import plugin
def classFactory(iface):
    from .open_in_google_maps import OpenInGoogleMapsPlugin
    return OpenInGoogleMapsPlugin(iface)


###