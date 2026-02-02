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


from .helper import gtk, gtksource, config, gdk


class Editor(gtksource.View):
    PAIRS = {
        gdk.KEY_apostrophe: ("'", "'"),
        gdk.KEY_quotedbl: ('"', '"'),
        gdk.KEY_parenleft: ("(", ")"),
        gdk.KEY_bracketleft: ("[", "]"),
        gdk.KEY_grave: ("`", "`"),
        gdk.KEY_braceleft: ("{", "}"),
        gdk.KEY_less: ("<", ">"),
    }

    def __init__(self):
        super().__init__()
        self.buff = gtksource.Buffer()
        self.set_buffer(self.buff)

        scheme_manager = gtksource.StyleSchemeManager()
        style = scheme_manager.get_scheme(config.get_config("scheme"))
        if style:
            self.buff.set_style_scheme(style)

        # self.set_auto_indent(config.get_config("auto_indent"))
        self.set_auto_indent(False)
        self.set_insert_spaces_instead_of_tabs(True)
        self.set_tab_width(4)

        # self.set_wrap_mode(
        #     gtk.WrapMode.WORD_CHAR if config.get_config(
        #         "wrap_mode") else gtk.WrapMode.NONE)
        self.set_wrap_mode(gtk.WrapMode.WORD_CHAR)  # wrap_mode: True
        # self.set_show_line_numbers(config.get_config("line_number"))
        self.set_show_line_numbers(False)  # line_number: False
        # self.set_show_right_margin(config.get_config("right_margin"))
        self.set_show_right_margin(True)  # right_margin: True
        # self.set_show_line_marks(config.get_config("line_mark"))
        self.set_show_line_marks(True)  # line_mark: True
        self.set_highlight_current_line(True)
        self.set_smart_home_end(gtksource.SmartHomeEndType.BEFORE)
        self.set_focusable(True)
        self.set_can_focus(True)

        controller = gtk.EventControllerKey()
        controller.set_propagation_phase(gtk.PropagationPhase.CAPTURE)
        controller.connect("key-pressed", self.on_key_press_event)
        self.add_controller(controller)

        self.MARK_TYPE_1 = "one"
        self.mark_attrs = gtksource.MarkAttributes()
        self.mark_attrs.set_icon_name("media-playback-start")
        self.set_mark_attributes(self.MARK_TYPE_1, self.mark_attrs, 0)

        gutter = self.get_gutter(gtk.TextWindowType.LEFT)
        click = gtk.GestureClick()
        click.connect("pressed", self.on_gutter_click)
        gutter.add_controller(click)
        self.set_bottom_margin(200)

    def on_key_press_event(self, controller, keyval, keycode, state):
        if getattr(self.buff, "_is_loading", False):
            return True

        if keyval in self.PAIRS:
            left, right = self.PAIRS[keyval]
            self.insert_pair(left, right)
            return True

        return False

    def insert_pair(self, left, right):
        self.buff.insert_at_cursor(left + right)
        insert_mark = self.buff.get_insert()
        iter = self.buff.get_iter_at_mark(insert_mark)
        iter.backward_char()
        self.buff.place_cursor(iter)

    def on_gutter_click(self, gesture, n_press, x, y):
        x_buf, y_buf = self.window_to_buffer_coords(
            gtk.TextWindowType.LEFT, int(x), int(y))

        result = self.get_iter_at_position(0, y_buf)
        iter = result.iter
        line_num = iter.get_line()

        marks = self.buff.get_source_marks_at_line(
            line_num, self.MARK_TYPE_1)

        if marks:
            self.buff.delete_mark(marks[0])
        else:
            self.buff.create_source_mark(None, self.MARK_TYPE_1, iter)

    def get_text(self):
        start_iter = self.buff.get_start_iter()
        end_iter = self.buff.get_end_iter()
        return self.buff.get_text(start_iter, end_iter, True)
