# Copyright (c) 2025 Zulfian <zulfian1732@gmail.com>

# This file is part of Jollpi.

# Jollpi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Jollpi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with Jollpi. if not, see <https://www.gnu.org/licenses/>.


import json
import os
import gi
import importlib.resources as res
# from .config import SWITCH_ITEMS, DEFAULT_CONFIG
from .config import DEFAULT_CONFIG
from importlib.metadata import version, PackageNotFoundError

for lib, ver in {
    "Gtk": "4.0",
    "Gio": "2.0",
    "Gdk": "4.0",
    "GLib": "2.0",
    "GtkSource": "5",
}.items():
    gi.require_version(lib, ver)

from gi.repository import (
    Gtk as gtk,
    Gio as gio,
    Gdk as gdk,
    GLib as glib,
    GtkSource as gtksource,
    GObject,
    Graphene,
)  # noqa: E402

__all__ = [
    "gtk", "gio", "gdk", "glib", "gtksource", "GObject", "Graphene"]


APP_NAME = "jellypie"
CUSTOM_CSS = "custom.css"


class StyleScheme:
    @staticmethod
    def get_style_scheme_dict():
        manager = gtksource.StyleSchemeManager.get_default()
        schemes = manager.get_scheme_ids()

        ordered = []
        if APP_NAME in schemes:
            ordered.append(APP_NAME)

        for s in schemes:
            if s != APP_NAME:
                ordered.append(s)

        result = {}

        for scheme_id in ordered:
            scheme = manager.get_scheme(scheme_id)
            label = scheme.get_name() if scheme else scheme_id.capitalize()
            result[label] = scheme_id

        return result


class SwitchMenu:
    @staticmethod
    def generate_switch_menu():
        # Switch items are now hardcoded, no menu items needed
        return ""

    @staticmethod
    def get_switch_item():
        # return SWITCH_ITEMS
        return []


def basedir():
    return os.path.dirname(__file__)


def get_icon_dir():
    dev_path = os.path.join(basedir(), "..", "..", "data", "icons")
    if os.path.exists(dev_path):
        return os.path.abspath(dev_path)

    sys_path = "/usr/share/icons"
    if os.path.exists(sys_path):
        return sys_path

    user_path = os.path.expanduser("~/.local/share/icons")
    os.makedirs(user_path, exist_ok=True)
    return user_path


def get_css_path():
    try:
        with res.path(APP_NAME, CUSTOM_CSS) as p:
            return str(p)
    except ModuleNotFoundError:
        return os.path.join(basedir(), CUSTOM_CSS)


def get_app_version():
    try:
        return version(APP_NAME)
    except PackageNotFoundError:
        return "dev"


CONFIG_PATH = os.path.join(
    os.path.expanduser(f"~/.local/share/{APP_NAME}/config.json")
)


class ConfigManager:
    def __init__(self):
        self.config = DEFAULT_CONFIG
        self.load_config()
        self.switch_widgets = {}
        self.radio_widgets = {}

    def register(self, widget, key, mode):
        if mode == "switch":
            self.switch_widgets.setdefault(key, []).append(widget)
        elif mode == "radio":
            self.radio_widgets.setdefault(key, []).append(widget)

    def unregister_widgets_by_window(self, window):
        def filter_out_switches(widget_list):
            return [w for w in widget_list if not w.is_ancestor(window)]

        def filter_out_radio_groups(group_list):
            return [
                group for group in group_list
                if not any(w.is_ancestor(window) for w in group)
            ]

        for key, widgets in list(self.switch_widgets.items()):
            new_list = filter_out_switches(widgets)
            if new_list:
                self.switch_widgets[key] = new_list
            else:
                del self.switch_widgets[key]

        for key, group_list in list(self.radio_widgets.items()):
            new_group_list = filter_out_radio_groups(group_list)
            if new_group_list:
                self.radio_widgets[key] = new_group_list
            else:
                del self.radio_widgets[key]

    def update_all_widget(self, key, value, mode):
        if mode == "switch":
            for widget in self.switch_widgets.get(key, []):
                widget.set_active(value)
        elif mode == "radio":
            for group in self.radio_widgets.get(key, []):
                for btn in group:
                    btn_scheme = btn.get_label().strip()
                    btn.set_active(btn_scheme == value)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                self.config.update(json.load(f))

    def get_config(self, key):
        return self.config.get(key)

    def set_config(self, key, value):
        self.config[key] = value
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)
            f.write('\n')  # Add trailing newline

    def get_filepath(self):
        """Get the configured filepath with tilde expansion."""
        from .config import DEFAULT_CONFIG
        filepath = self.config.get("filepath", DEFAULT_CONFIG["filepath"])
        return os.path.expanduser(filepath)


class TabRow(GObject.GObject):
    label = GObject.Property(type=str)
    checked = GObject.Property(type=bool, default=True)
    tabdata = GObject.Property(type=object)

    def __init__(self, label, tabdata):
        super().__init__()
        self.label = label
        self.tabdata = tabdata


switchmenu = SwitchMenu()
stylescheme = StyleScheme()
config = ConfigManager()
