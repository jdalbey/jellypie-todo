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
from . import window
from .helper import (
    gtk, gio, glib, gdk, gtksource, get_icon_dir, basedir
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

        # Configure search paths for development
        # Problem: GtkSourceView checks if directory exists, not if specific files exist
        # So if user dir exists (even empty), it won't check repo dir
        # Solution: Only include user dir in search path if user actually has the files
        repo_style_dir = os.path.join(basedir(), "style")
        if os.path.exists(repo_style_dir):
            scheme_manager = gtksource.StyleSchemeManager.get_default()
            lang_manager = gtksource.LanguageManager.get_default()

            # Get default search paths
            current_scheme_paths = scheme_manager.get_search_path()
            current_lang_paths = lang_manager.get_search_path()

            # Check if user has customized the jellypie style file
            user_style_dir = os.path.expanduser("~/.local/share/gtksourceview-5/styles")
            user_has_style = os.path.exists(os.path.join(user_style_dir, "jellypie.xml"))

            # Check if user has customized the language file
            user_lang_dir = os.path.expanduser("~/.local/share/gtksourceview-5/language-specs")
            user_has_lang = os.path.exists(os.path.join(user_lang_dir, "jellypie-formatted.lang"))

            # Build style scheme search path
            new_scheme_paths = []
            if user_has_style:
                # User has customization, respect it
                new_scheme_paths.append(user_style_dir)
            # Add repo directory for development
            new_scheme_paths.append(repo_style_dir)
            # Add system directories
            for path in current_scheme_paths:
                if path not in new_scheme_paths:
                    new_scheme_paths.append(path)
            scheme_manager.set_search_path(new_scheme_paths)

            # Build language specs search path
            new_lang_paths = []
            if user_has_lang:
                # User has customization, respect it
                new_lang_paths.append(user_lang_dir)
            # Add repo directory for development
            new_lang_paths.append(repo_style_dir)
            # Add system directories
            for path in current_lang_paths:
                if path not in new_lang_paths:
                    new_lang_paths.append(path)
            lang_manager.set_search_path(new_lang_paths)

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
