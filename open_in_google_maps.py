# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OpenGoogleMaps
                                 A QGIS plugin
 Opens the current map extent in Google Maps
                              -------------------
        begin                : 2024-12-17
        author               : Harry King
        email                : nlu1vwm0@anonaddy.com
        git sha              : $Format:%H$
        updated              : 2026-02-02
 ***************************************************************************/

 
 /***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Import Packages - QGIS
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import (
    QAction, QDialog, QVBoxLayout, QCheckBox, 
    QDialogButtonBox, QLabel, QGridLayout
)
from qgis.core import (
    QgsProject, 
    QgsCoordinateReferenceSystem, 
    QgsCoordinateTransform, 
    Qgis,
    QgsSettings
)

# Import Packages - General
import os
import webbrowser
import math
from functools import partial

# ----------------------------------------------------------------------
# Configuration Dialog Class
# ----------------------------------------------------------------------
class MapConfigDialog(QDialog):
    """
    Simple dialog to enable/disable specific map providers.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open Google Maps, Google Earth + Other Web Maps")
        self.resize(350, 200)
        
        self.settings = QgsSettings()
        
        layout = QVBoxLayout()
        
        # Instructions
        layout.addWidget(QLabel("<b>Open Google Maps, Google Earth + Other Web Maps</b>"))
        layout.addWidget(QLabel("Please select which map buttons you want to use:"))
        
        # Grid layout for checkboxes
        grid = QGridLayout()
        
        # Checkboxes
        self.cb_google = QCheckBox("Google Maps")
        self.cb_earth = QCheckBox("Google Earth Web")
        self.cb_osm = QCheckBox("OpenStreetMap")
        self.cb_bing = QCheckBox("Bing Maps")
        self.cb_apple = QCheckBox("Apple Maps")
        self.cb_yandex = QCheckBox("Yandex Maps")
        
        # Load current settings
        self.cb_google.setChecked(self.settings.value("OpenMaps/enable_google", True, type=bool))
        self.cb_earth.setChecked(self.settings.value("OpenMaps/enable_earth", False, type=bool))
        self.cb_osm.setChecked(self.settings.value("OpenMaps/enable_osm", False, type=bool))
        self.cb_bing.setChecked(self.settings.value("OpenMaps/enable_bing", False, type=bool))
        self.cb_apple.setChecked(self.settings.value("OpenMaps/enable_apple", False, type=bool))
        self.cb_yandex.setChecked(self.settings.value("OpenMaps/enable_yandex", False, type=bool))
        
        # Add to grid (row, col)
        grid.addWidget(self.cb_google, 0, 0)
        grid.addWidget(self.cb_earth, 0, 1)
        grid.addWidget(self.cb_osm, 1, 0)
        grid.addWidget(self.cb_bing, 1, 1)
        grid.addWidget(self.cb_apple, 2, 0)
        grid.addWidget(self.cb_yandex, 2, 1)
        
        layout.addLayout(grid)
        
        # Save/Cancel Buttons
        buttons = QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)

    def save_settings(self):
        """Save checkbox states to QGIS settings"""
        self.settings.setValue("OpenMaps/enable_google", self.cb_google.isChecked())
        self.settings.setValue("OpenMaps/enable_earth", self.cb_earth.isChecked())
        self.settings.setValue("OpenMaps/enable_osm", self.cb_osm.isChecked())
        self.settings.setValue("OpenMaps/enable_bing", self.cb_bing.isChecked())
        self.settings.setValue("OpenMaps/enable_apple", self.cb_apple.isChecked())
        self.settings.setValue("OpenMaps/enable_yandex", self.cb_yandex.isChecked())
        self.accept()

# ----------------------------------------------------------------------
# Main Plugin Class
# ----------------------------------------------------------------------
class OpenInGoogleMapsPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu_name = '&Open Google Maps, Google Earth + Other Web Maps'
        self.settings = QgsSettings()

    def initGui(self):
        """Initialize the GUI - Toolbar and Menus"""
        # 1. Create the Config Menu Item
        self.config_action = QAction(
            QIcon(), 
            'Configure Maps...', 
            self.iface.mainWindow()
        )
        self.config_action.triggered.connect(self.open_config)
        self.iface.addPluginToWebMenu(self.menu_name, self.config_action)
        
        # 2. Setup the Map Actions (Buttons) based on settings
        self.setup_map_actions()
        
        # 3. Check for First Run
        if not self.settings.value("OpenMaps/first_run_seen", False, type=bool):
            QTimer.singleShot(1000, self.trigger_first_run)

    def trigger_first_run(self):
        """Show the dialog and mark first run as complete"""
        self.open_config()
        self.settings.setValue("OpenMaps/first_run_seen", True)

    def setup_map_actions(self):
        """Reads settings and adds the relevant buttons to toolbar/menu"""
        self.unload_map_actions()
        
        # Define available providers
        # (Name, SettingKey, RelativePath, ProviderKey)
        providers = [
            ("Google Maps",     "OpenMaps/enable_google", "icon.png",              "google"),
            ("Google Earth",    "OpenMaps/enable_earth",  "img/icon_earth.png",    "earth"),
            ("OpenStreetMap",   "OpenMaps/enable_osm",    "img/icon_osm.png",      "osm"),
            ("Bing Maps",       "OpenMaps/enable_bing",   "img/icon_bing.png",     "bing"),
            ("Apple Maps",      "OpenMaps/enable_apple",  "img/icon_apple.png",    "apple"),
            ("Yandex Maps",     "OpenMaps/enable_yandex", "img/icon_yandex.png",   "yandex"),
        ]

        for name, setting_key, rel_path, provider_key in providers:
            is_enabled = self.settings.value(setting_key, (provider_key == "google"), type=bool)
            
            if is_enabled:
                icon_path = os.path.join(self.plugin_dir, rel_path)
                
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
                else:
                    icon = QIcon() # Blank icon fallback
                
                action = QAction(icon, f"Open in {name}", self.iface.mainWindow())
                action.triggered.connect(partial(self.run, provider=provider_key))
                
                self.iface.addToolBarIcon(action)
                self.iface.addPluginToWebMenu(self.menu_name, action)
                self.actions.append(action)

    def unload_map_actions(self):
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
            self.iface.removePluginWebMenu(self.menu_name, action)
        self.actions.clear()

    def unload(self):
        self.unload_map_actions()
        self.iface.removePluginWebMenu(self.menu_name, self.config_action)
        self.actions.clear()

    def open_config(self):
        dlg = MapConfigDialog()
        if dlg.exec():
            self.setup_map_actions()

    def run(self, provider="google"):
        """Main logic to open map"""
        try:
            canvas = self.iface.mapCanvas()
            if not canvas.mapSettings().hasValidSettings():
                self._show_error("Map settings are invalid.")
                return

            source_crs = canvas.mapSettings().destinationCrs()
            wgs84_crs = QgsCoordinateReferenceSystem('EPSG:4326')
            transform = QgsCoordinateTransform(source_crs, wgs84_crs, QgsProject.instance())
            
            center_point = canvas.center()
            projected_center = transform.transform(center_point)
            
            lat = projected_center.y()
            lon = projected_center.x()
            
            # Standard Tile Zoom calculation
            zoom = self._calculate_zoom_level(canvas.scale())
            
            # Google Earth Specific Distance Calculation
            # Updated to scale/1.25. (1000 scale = 800m camera distance)
            # This zooms IN slightly compared to 1:1, but not as drastic as 1.5
            earth_dist = max(100, int(canvas.scale() / 1.25))

            url = ""
            if provider == "google":
                url = f"https://www.google.com/maps/@{lat},{lon},{zoom}z"
            elif provider == "earth":
                url = f"https://earth.google.com/web/@{lat},{lon},0a,{earth_dist}d,35y,0h,0t,0r"
            elif provider == "osm":
                url = f"https://www.openstreetmap.org/#map={zoom}/{lat}/{lon}"
            elif provider == "bing":
                url = f"https://www.bing.com/maps?cp={lat}~{lon}&lvl={zoom}"
            elif provider == "apple":
                url = f"http://maps.apple.com/?ll={lat},{lon}&z={zoom}"
            elif provider == "yandex":
                url = f"https://yandex.com/maps/?ll={lon},{lat}&z={zoom}"
            
            if url:
                webbrowser.open(url)

        except Exception as e:
            self._show_error(f"An error occurred: {str(e)}")

    def _calculate_zoom_level(self, scale):
        if scale <= 0: return 2
        try:
            zoom = math.log2(591657550.5 / scale)
            return int(max(0, min(21, zoom)))
        except ValueError:
            return 10 

    def _show_error(self, message):
        self.iface.messageBar().pushMessage(
            "Open Google Maps, Google Earth + Other Web Maps",
            message,
            Qgis.Warning,
            duration=3
        )