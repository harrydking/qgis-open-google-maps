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

Core plugin code

###

"""

### Main Plugin Code

# Import Packages - QGIS
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform, Qgis

# Import Packages - General
import os
import webbrowser

class OpenInGoogleMapsPlugin:

    # Definie functions to initiate plugin, remove plugin

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []

    def initGui(self):
        # Create action for toolbar
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.action = QAction(QIcon(icon_path), 'Open in Google Maps', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        
        # Add toolbar icon
        self.iface.addToolBarIcon(self.action)
        self.actions.append(self.action)

    def unload(self):
        # Remove toolbar icon and action
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
            self.iface.mainWindow().removeAction(action)
        self.actions.clear()

    # Define plugin running functions

    def run(self):
        # Get current map canvas
        canvas = self.iface.mapCanvas()
        
        # Get current extent
        extent = canvas.extent()
        
        # Get current CRS
        current_crs = canvas.mapSettings().destinationCrs()
        
        # Transform to WGS84 if not already
        wgs84_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        transform = QgsCoordinateTransform(current_crs, wgs84_crs, QgsProject.instance())
        
        # Transform extent
        transformed_extent = transform.transformBoundingBox(extent)
        
        # Get centre coordinates
        center_lon = (transformed_extent.xMinimum() + transformed_extent.xMaximum()) / 2
        center_lat = (transformed_extent.yMinimum() + transformed_extent.yMaximum()) / 2
        
        # Construct URL with centre coordinates and zoom
        maps_url = f"https://www.google.com/maps/@{center_lat},{center_lon},{self._calculate_zoom_level()}z"
        
        # Open in default web browser
        webbrowser.open(maps_url)

    def _calculate_zoom_level(self):
        """
        Calculate Google Maps zoom level based on QGIS map scale.

        """
        canvas = self.iface.mapCanvas()
        scale = canvas.scale()
        
        if scale < 100:
            return 20 
        elif scale < 250:
            return 20
        elif scale < 500:
            return 19
        elif scale < 750:
            return 19
        elif scale < 1000:
            return 18
        elif scale < 1500:
            return 18
        elif scale < 2500:
            return 17
        elif scale < 3500:
            return 17
        elif scale < 5000:
            return 16
        elif scale < 7500:
            return 16
        elif scale < 10000:
            return 15
        elif scale < 15000:
            return 15
        elif scale < 25000:
            return 14
        elif scale < 35000:
            return 14
        elif scale < 50000:
            return 13
        elif scale < 75000:
            return 13
        elif scale < 100000:
            return 12
        elif scale < 150000:
            return 12
        elif scale < 250000:
            return 11
        elif scale < 350000:
            return 11
        elif scale < 500000:
            return 10
        elif scale < 750000:
            return 10
        elif scale < 1000000:
            return 9
        elif scale < 1500000:
            return 9
        elif scale < 2500000:
            return 8
        elif scale < 3500000:
            return 8
        elif scale < 5000000:
            return 7
        elif scale < 7500000:
            return 7
        elif scale < 10000000:
            return 6
        elif scale < 15000000:
            return 6
        elif scale < 25000000:
            return 5
        elif scale < 35000000:
            return 5
        elif scale < 50000000:
            return 4
        elif scale < 75000000:
            return 4
        elif scale < 100000000:
            return 3
        elif scale < 150000000:
            return 3
        else:
            return 2