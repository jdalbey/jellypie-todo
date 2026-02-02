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


from .helper import gtk, glib


class StatusBar(gtk.Overlay):
    def __init__(self):
        super().__init__()
        self.info_label = gtk.Label()
        self.info_label.get_style_context().add_class("info-label")
        self.info_label.set_halign(gtk.Align.END)
        self.info_label.set_valign(gtk.Align.END)
        self.info_label.set_margin_end(130)
        self.info_label.set_visible(False)

        self.add_overlay(self.info_label)

        self.timeout_id = None

    def show_line_col(self, buff, filetype, mode=None):
        _iter = buff.get_iter_at_mark(buff.get_insert())
        row = _iter.get_line() + 1
        col = _iter.get_line_offset() + 1

        line_col = f"{row}:{col}     "
        _mode = mode if mode else ""
        _ftype = f"     {filetype}" if filetype else ""

        text = f"{line_col}{_mode}{_ftype}"

        def do_show():
            self.info_label.set_text(text)
            self.info_label.set_visible(True)

            if self.timeout_id:
                glib.source_remove(self.timeout_id)

            self.timeout_id = glib.timeout_add_seconds(2, self.hide_info_label)
            return False

        glib.idle_add(do_show, priority=glib.PRIORITY_HIGH_IDLE)

    def hide_info_label(self):
        self.info_label.set_visible(False)
        self.timeout_id = None
        return False
