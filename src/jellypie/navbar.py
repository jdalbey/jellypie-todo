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


from .helper import gtk


class NavBar():
    def __init__(self):
        overlay = gtk.Overlay()
        self.search_entry = gtk.SearchEntry()
        self.search_entry.get_style_context().add_class("search-entry")
        self.search_entry.set_placeholder_text("Search")
        self.search_entry.set_hexpand(True)
        overlay.set_child(self.search_entry)

        self.result_label = gtk.Label()
        self.result_label.set_halign(gtk.Align.END)
        self.result_label.set_valign(gtk.Align.CENTER)
        self.result_label.set_margin_end(27)
        self.result_label.get_style_context().add_class("result-label")
        overlay.add_overlay(self.result_label)

        def make_button(icon, tooltip, toggle=False, x=False):
            if toggle:
                btn = gtk.ToggleButton()
                if x:
                    image = gtk.Image.new_from_icon_name(icon)
                    image.set_pixel_size(16)
                    btn.set_child(image)
                else:
                    btn.set_label(icon)
            else:
                btn = gtk.Button.new_from_icon_name(icon)
            btn.set_tooltip_text(tooltip)
            btn.get_style_context().add_class("flat")
            btn.get_style_context().add_class("option-btn")
            return btn

        self.prev_btn = make_button("go-up-symbolic", "Previous Match")
        self.next_btn = make_button("go-down-symbolic", "Next Match")

        self.case_sens_btn = make_button("Aa", "Match Case Sensitive", True)
        self.whole_word_btn = make_button("Wo", "Match Whole Word Only", True)
        self.regex_btn = make_button("Re", "Regular Expression", True)
        self.close_btn = make_button("window-close-symbolic", "Close Search")

        find_hbox = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=6)
        find_hbox.set_halign(gtk.Align.CENTER)
        find_hbox.set_valign(gtk.Align.CENTER)
        find_hbox.set_hexpand(True)

        find_hbox.append(overlay)
        find_hbox.append(self.prev_btn)
        find_hbox.append(self.next_btn)
        find_hbox.append(self.case_sens_btn)
        find_hbox.append(self.whole_word_btn)
        find_hbox.append(self.regex_btn)
        find_hbox.append(self.close_btn)

        box = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=4)
        box.set_hexpand(True)
        box.set_halign(gtk.Align.FILL)
        box.get_style_context().add_class("find-bar-wrapper")
        box.append(find_hbox)

        self.find_revealer = gtk.Revealer()
        self.find_revealer.set_transition_type(
            gtk.RevealerTransitionType.SLIDE_DOWN)
        self.find_revealer.set_transition_duration(150)
        self.find_revealer.set_reveal_child(False)
        self.find_revealer.set_child(box)

        self.gtl_hbox = gtk.Box(
            orientation=gtk.Orientation.HORIZONTAL, spacing=6)
        self.gtl_hbox.set_halign(gtk.Align.CENTER)
        self.gtl_hbox.set_valign(gtk.Align.CENTER)
        self.gtl_hbox.set_hexpand(True)

        self.gtl_entry = gtk.Entry()
        self.gtl_entry.set_icon_from_icon_name(
            gtk.EntryIconPosition.PRIMARY, "go-jump-symbolic")
        self.gtl_entry.get_style_context().add_class("search")
        self.gtl_entry.connect("notify::text", self.on_input_text)

        self.gtl_btn = gtk.Button(label="Go to line")
        self.gtl_btn.get_style_context().add_class("suggested-action")
        self.gtl_btn.set_hexpand(True)

        self.gtl_hbox.append(self.gtl_entry)
        self.gtl_hbox.append(self.gtl_btn)

        box1 = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=4)
        box1.set_hexpand(True)
        box1.set_halign(gtk.Align.FILL)
        box1.get_style_context().add_class("find-bar-wrapper")
        box1.append(self.gtl_hbox)

        self.gtl_revealer = gtk.Revealer()
        self.gtl_revealer.set_transition_type(
            gtk.RevealerTransitionType.SLIDE_DOWN)
        self.gtl_revealer.set_transition_duration(150)
        self.gtl_revealer.set_reveal_child(False)
        self.gtl_revealer.set_child(box1)

    def get_find_revealer(self):
        return self.find_revealer

    def get_gtl_revealer(self):
        return self.gtl_revealer

    def on_input_text(self, entry, param):
        text = entry.get_text()
        if not text.isdigit():
            entry.set_text(''.join(filter(str.isdigit, text)))
            entry.set_position(-1)
