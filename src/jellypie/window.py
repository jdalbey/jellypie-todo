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


import os
from . import menu
from . import notebook
from . import statusbar
from . import navbar
from .helper import gtk, config


class MainWindow(gtk.ApplicationWindow):
    def __init__(self, files=None, **kargs):
        super().__init__(**kargs)

        self.set_resizable(True)

        # Restore window size from config
        window_width = config.get_config("window_width")
        window_height = config.get_config("window_height")

        if window_width and window_height and window_width > 0 and window_height > 0:
            self.set_default_size(window_width, window_height)
        else:
            # Default to maximized
            self.set_default_size(800, 600)
            self.maximize()

        stbar = statusbar.StatusBar()
        nav_bar = navbar.NavBar()
        find_revealer = nav_bar.get_find_revealer()
        gtl_revealer = nav_bar.get_gtl_revealer()

        self.menu = menu.Menu(self, nav_bar, find_revealer, gtl_revealer)
        header_obj = self.menu.header
        self.set_titlebar(header_obj)

        label = gtk.Label()
        header_obj.set_title_widget(label)

        self.nb = notebook.Notebook(
            label, stbar, nav_bar, find_revealer,
            gtl_revealer, self.get_application(), self)

        stbar.set_child(self.nb)

        vbox = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        vbox.append(stbar)
        vbox.append(find_revealer)
        vbox.append(gtl_revealer)

        self.set_child(vbox)

        # Single-file mode: load file from config
        filepath = config.get_filepath()

        # Create file if it doesn't exist
        if not os.path.exists(filepath):
            try:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write("")  # Create empty file
            except Exception as e:
                print(f"Warning: Could not create file {filepath}: {e}")

        # Load the file
        if os.path.exists(filepath):
            self.menu.open_file([filepath])
        else:
            # Fallback if file creation failed
            self.nb.new_tab("Untitled", tooltip="Untitled")

    def do_close_request(self):
        # Save window size (GTK4 doesn't support window position)
        width = self.get_width()
        height = self.get_height()

        config.set_config("window_width", width)
        config.set_config("window_height", height)

        self.nb.on_close_window(self)
        return True
