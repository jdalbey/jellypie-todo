#!/usr/bin/env python3

# Copyright (c) 2026 John Dalbey

# This file is part of Jellypie.

# Jellypie is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Jellypie is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with Jellypie. if not, see <https://www.gnu.org/licenses/>.

# Jellypie is modifed from the original Jollpi which is Copyright (c) 2025 Zulfian <zulfian1732@gmail.com>

import os
import sys
import shutil
from . import window
from .helper import (
    gtk, gio, glib, gdk, get_style_source, get_icon_dir, basedir
)


class Application(gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id='com.github.jdalbey.jellypie',
            flags=gio.ApplicationFlags.HANDLES_OPEN,
            **kwargs
        )
        self.windows = []
        self.open_files = {}

        self.add_main_option(
            'test',
            ord('t'),
            glib.OptionFlags.NONE,
            glib.OptionArg.STRING,
            'Command line test',
            None,
        )

        self.initial_files = []

    def is_file_open(self, path):
        return path in self.open_files

    def register_file(self, path, window, key):
        self.open_files[path] = (window, key)

    def unregister_file(self, path):
        self.open_files.pop(path, None)

    def do_startup(self):
        gtk.Application.do_startup(self)

    def do_activate(self):
        settings = gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        dev_mode = os.path.exists(
            os.path.join(basedir(), "style", "jellypie.xml"))

        if dev_mode:
            try:
                user_style_dir = os.path.expanduser(
                    "~/.local/share/gtksourceview-5/styles")
                os.makedirs(user_style_dir, exist_ok=True)
                style_target = os.path.join(user_style_dir, "jellypie.xml")
                style_source = get_style_source()
                shutil.copy(style_source, style_target)
            except Exception:
                pass

        icon_source = get_icon_dir()
        icon_theme = gtk.IconTheme.get_for_display(gdk.Display.get_default())
        icon_theme.add_search_path(icon_source)
        gtk.Window.set_default_icon_name(self.get_application_id())

        if not self.windows:
            win = window.MainWindow(application=self, files=self.initial_files)
            self.windows.append(win)

        self.initial_files = []

        self.get_active_window().present()

    def do_open(self, files, n_files, hint):
        # Disabled: Single-file mode - ignore command-line/drag-drop files
        if not self.get_windows():
            self.activate()
        else:
            win = self.get_active_window() or self.get_windows()[0]
            win.present()


def main():
    try:
        app = Application()
        return app.run(sys.argv)
    except KeyboardInterrupt:
        print("Bye!!!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
