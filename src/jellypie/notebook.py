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
import re
import time
import gc
from . import editor
from . import minimap
from .helper import (
    gtk, gdk, gio, glib, gtksource, config, get_css_path, TabRow)

EDIT_ICON = "document-edit-symbolic"
SAVE_ICON = "document-save-symbolic"

PLAIN_WHITELIST = [
    "text/csv",
    "text/tab-separated-values",
    "text/x-log",
    "text/x-gettext-translation",
    "application/x-hex-dump",
    "application/octet-stream",
]


class Notebook(gtk.Notebook):
    def __init__(self, label, statusbar, nav, find_rev, gtl_rev, app, window):
        super().__init__()
        self.app = app
        self.window = window

        esc_act = gio.SimpleAction.new("esc", None)
        esc_act.connect("activate", self.on_esc_key_press)
        self.window.add_action(esc_act)
        self.app.set_accels_for_action("win.esc", ["Escape"])

        self.statusbar = statusbar
        self.navbar = nav
        self.find_revealer = find_rev
        self.gtl_revealer = gtl_rev

        self.navbar.search_entry.connect(
            "changed", self.on_search_entry_changed)

        controller = gtk.EventControllerKey()
        controller.set_propagation_phase(gtk.PropagationPhase.CAPTURE)
        controller.connect("key-pressed", self.on_search_entry_key_press)
        self.navbar.search_entry.add_controller(controller)

        self.navbar.next_btn.connect("clicked", self.on_next_clicked)
        self.navbar.prev_btn.connect("clicked", self.on_prev_clicked)

        self.navbar.case_sens_btn.connect(
            "toggled", self.on_case_sensitive_toggled)
        self.navbar.whole_word_btn.connect(
            "toggled", self.on_whole_word_toggled)
        self.navbar.regex_btn.connect("toggled", self.on_regex_toggled)

        self.navbar.close_btn.connect("clicked", self.close_findbar)

        self.navbar.gtl_entry.connect(
            "activate", lambda entry: self.go_to_line())
        self.navbar.gtl_btn.connect("clicked", lambda entry: self.go_to_line())

        css_path = get_css_path()
        self.apply_global_css(
            css_path,
            family=config.get_config("font_family"),
            size=config.get_config("font_size"),
            weight=config.get_config("font_weight"))

        self.set_tab_pos(gtk.PositionType.TOP)
        self.set_scrollable(True)
        self.set_show_tabs(False)

        self.admin_files = set()
        self.editor_instance = {}
        self.files = {}
        self.unsave = {}
        self.key = None
        self.value = None
        self.search_cancellable = None
        self.loader_cancellable = {}

        self.findbar_visible = {}
        self.search_text = {}
        self.result_label = {}

        self.case_sensitive = {}
        self.whole_word = {}
        self.use_regex = {}

        self.search_context = {}
        self.search_error = {}

        self.gtlbar_visible = {}
        self.gtl_text = {}

        self.monitors = {}
        self.pending_reload = {}
        self.recently_saved = {}
        self.file_event_timer = {}
        self.is_saving = {}

        self.mark_set_timeout = {}

        self.title_label = label
        self.title_label.get_style_context().add_class("title")

        self.switch_id = self.connect("switch_page", self.on_switch_page)

    def get_language_for_buffer(self, lang, mime_type):
        """
        Determine which language to use for syntax highlighting.
        Returns jellypie-formatted language if enabled in config, otherwise the guessed language.
        """
        from .helper import config

        # Check if jellypie formatting is enabled
        allow_formatting = config.get_config("allow_jellypie_formatting")
        if allow_formatting is None:
            allow_formatting = True  # Default to True

        if allow_formatting:
            # Use jellypie-formatted language for syntax highlighting
            lang_man = gtksource.LanguageManager.get_default()
            jellypie_lang = lang_man.get_language("jellypie-formatted")
            if jellypie_lang:
                return jellypie_lang

        # Fall back to original language detection
        return None if mime_type in PLAIN_WHITELIST else lang

    def on_search_entry_key_press(self, controller, keyval, keycode, state):
        if keyval == gdk.KEY_Up:
            self.on_prev_clicked(None)
            return True
        elif keyval == gdk.KEY_Down:
            self.on_next_clicked(None)
            return True
        return False

    def on_close_tab_accel(self, action, param):
        page_num = self.get_current_page()
        if page_num != -1:
            hbox = self.get_nth_page(page_num)
            self.close_tab(None, hbox)

    def update_result_label(self, index, total):
        if total <= 0:
            label_text = ""
        elif index < 0:
            label_text = f"0 of {total}"
        else:
            label_text = f"{index} of {total}"

        if self.result_label.get(self.key) == label_text:
            return

        self.navbar.result_label.set_text(label_text)
        self.result_label[self.key] = label_text

    def set_search_error_state(self, error: bool):
        search_style = self.navbar.search_entry.get_style_context()
        result_style = self.navbar.result_label.get_style_context()

        if error:
            search_style.add_class("search-error")
            result_style.add_class("search-error")
        else:
            search_style.remove_class("search-error")
            result_style.remove_class("search-error")

    def is_match(self, pattern, text, use_regex):
        if use_regex:
            try:
                return re.fullmatch(pattern, text) is not None
            except re.error:
                return False
        return text == pattern

    def button_status(self, status):
        for btn in (
            self.navbar.next_btn,
            self.navbar.prev_btn
        ):
            btn.set_sensitive(status)

    def on_search_entry_changed(self, entry):
        if self.block_signal or self.key is None:
            return

        text = entry.get_text()
        self.search_text[self.key] = text

        if not text or not self.value:
            self.update_result_label(-1, 0)
            self.search_error[self.key] = False
            self.context.set_highlight(False)
            self.context.get_settings().set_search_text(text)
            self.set_search_error_state(False)
            self.button_status(False)
            return

        settings = self.context.get_settings()

        case_active = self.case_sensitive.get(self.key, False)
        use_regex = self.use_regex.get(self.key, False)
        whole_word = self.whole_word.get(self.key, False)

        settings.set_case_sensitive(case_active)
        settings.set_wrap_around(True)

        if use_regex:
            pattern = r"\b(?:{})\b".format(text) if whole_word else text
            settings.set_regex_enabled(True)
        else:
            pattern = r"\b" + re.escape(text) + r"\b" if whole_word else text
            settings.set_regex_enabled(whole_word)

        settings.set_search_text(pattern)
        self.context.set_highlight(True)

    def on_occurrences_notify(self, context, pspec):
        settings = context.get_settings()
        text = settings.get_search_text()
        if not text:
            return

        buff = context.get_buffer()
        if getattr(buff, "_is_loading", False):
            return

        count = context.get_occurrences_count()
        if count < 0:
            return

        prev_button_status = getattr(self, "last_button_status", None)

        def update_ui():
            if count == 0:
                self.update_result_label(-1, 0)
                self.search_error[self.key] = True
                self.set_search_error_state(True)
                button_on = False
            else:
                try:
                    start, end = buff.get_selection_bounds()
                    selected_text = buff.get_text(start, end, False)
                    pos = context.get_occurrence_position(start, end)

                    has_match = (
                        pos != -1 and
                        self.is_match(text, selected_text,
                                      settings.get_regex_enabled())
                    )

                    self.update_result_label(pos if has_match else 0, count)
                except (ValueError, glib.Error):
                    self.update_result_label(0, count)

                self.search_error[self.key] = False
                self.set_search_error_state(False)
                button_on = True

            if prev_button_status != button_on:
                self.button_status(button_on)
                self.last_button_status = None

            return False

        glib.idle_add(update_ui, priority=glib.PRIORITY_HIGH_IDLE)

    def reset_cancellable(self):
        if (
            hasattr(self, "search_cancellable") and
            self.search_cancellable is not None
        ):
            self.search_cancellable.cancel()
            self.search_cancellable = None

        self.search_cancellable = gio.Cancellable()

    def on_match(self, context, result, user_data=None):
        if self.search_cancellable.is_cancelled():
            return

        try:
            found, start, end, wrapped = context.forward_finish(result)
        except glib.Error:
            self.update_result_label(-1, 0)
            return

        buff = context.get_buffer()
        if found:
            self._is_selecting = True

            buff.select_range(start, end)
            self.value.scroll_to_iter(start, 0.25, False, 0.0, 0.5)

            glib.idle_add(lambda: setattr(self, '_is_selecting', False))

            pos = context.get_occurrence_position(start, end)
            count = context.get_occurrences_count()
            self.update_result_label(pos, count)
        else:
            self.set_search_error_state(True)
            self.update_result_label(-1, 0)

    def on_next_clicked(self, btn):
        buff = self.context.get_buffer()

        if buff.get_has_selection():
            _, end = buff.get_selection_bounds()
        else:
            end = buff.get_iter_at_mark(buff.get_insert())

        self.reset_cancellable()
        self.context.forward_async(
            end, self.search_cancellable, self.on_match, None)

    def on_prev_clicked(self, btn):
        buff = self.context.get_buffer()

        if buff.get_has_selection():
            start, _ = buff.get_selection_bounds()
        else:
            start = buff.get_iter_at_mark(buff.get_insert())

        self.reset_cancellable()
        self.context.backward_async(
            start, self.search_cancellable, self.on_match, None)

    def on_case_sensitive_toggled(self, btn):
        if self.block_signal or self.key is None:
            return

        active = btn.get_active()
        self.case_sensitive[self.key] = active

        self.on_search_entry_changed(self.navbar.search_entry)

    def on_whole_word_toggled(self, btn):
        if self.block_signal or self.key is None:
            return

        active = btn.get_active()
        self.whole_word[self.key] = active

        self.on_search_entry_changed(self.navbar.search_entry)

    def on_regex_toggled(self, btn):
        if self.block_signal or self.key is None:
            return

        active = btn.get_active()
        self.use_regex[self.key] = active

        self.on_search_entry_changed(self.navbar.search_entry)

    def on_replace_clicked(self, btn):
        buff = self.context.get_buffer()
        if not buff.get_has_selection():
            return

        start, end = buff.get_selection_bounds()
        replace_text = self.navbar.replace_entry.get_text()
        unescaped_replace = gtksource.utils_unescape_search_text(replace_text)

        try:
            success = self.context.replace(start, end, unescaped_replace, -1)
            if not success:
                return
        except glib.Error:
            return

        self.on_next_clicked(None)

        def update_after_replace():
            count = self.context.get_occurrences_count()
            if count < 0:
                return True

            if buff.get_has_selection():
                try:
                    start, end = buff.get_selection_bounds()
                    pos = self.context.get_occurrence_position(start, end)
                    if pos != -1:
                        self.update_result_label(pos, count)
                        self.navbar.replace_btn.set_sensitive(True)
                    else:
                        self.update_result_label(0, count)
                        self.navbar.replace_btn.set_sensitive(False)
                except (ValueError, glib.Error):
                    self.update_result_label(0, count)
                    self.navbar.replace_btn.set_sensitive(False)
            else:
                self.update_result_label(0, count)
                self.navbar.replace_btn.set_sensitive(False)
            return False

        glib.timeout_add(300, update_after_replace)

    def on_replace_all_clicked(self, btn):
        replace_text = self.navbar.replace_entry.get_text()

        unescaped_replace = gtksource.utils_unescape_search_text(replace_text)

        def do_replace_all():
            try:
                buff = self.context.get_buffer()
                buff.handler_block_by_func(self.on_buffer_changed)
                count = self.context.get_occurrences_count()
                if count < 0:
                    return True

                if count == 0:
                    self.update_result_label(-1, 0)
                    return False

                buff.begin_user_action()
                self.context.replace_all(unescaped_replace, -1)
                buff.end_user_action()

                self.navbar.replace_btn.set_sensitive(False)
                self.navbar.replace_all_btn.set_sensitive(False)

            except glib.Error:
                self.update_result_label(0, 0)
                self.navbar.replace_btn.set_sensitive(False)
                self.navbar.replace_all_btn.set_sensitive(False)
            finally:
                buff.handler_unblock_by_func(self.on_buffer_changed)
                self.on_search_entry_changed(self.navbar.search_entry)
            return False

        do_replace_all()

    def go_to_line(self):
        line_text = self.navbar.gtl_entry.get_text().strip()
        if not line_text.isdigit():
            return

        line_num = int(line_text) - 1
        if line_num < 0:
            line_num = 0

        self.gtl_text[self.key] = str(line_num + 1)

        buff = self.value.get_buffer()
        max_line = buff.get_line_count() - 1
        line_num = min(line_num, max_line)

        success, iter_ = buff.get_iter_at_line(line_num)
        if success:
            self.close_gtlbar()
            self.value.scroll_to_iter(iter_, 0.2, False, 0, 0)
            buff.place_cursor(iter_)
            self.value.grab_focus()

    def close_findbar(self, btn):
        try:
            context = self.search_context.get(self.key)
            if context:
                context.set_highlight(False)
        except Exception:
            pass

        self.find_revealer.set_reveal_child(False)
        self.findbar_visible[self.key] = False
        editor = self.get_active_editor(self.get_current_tab())
        editor.grab_focus()

    def close_gtlbar(self):
        self.gtl_revealer.set_reveal_child(False)
        self.gtlbar_visible[self.key] = False

    def on_esc_key_press(self, action, param):
        self.close_findbar(None)
        self.close_gtlbar()

    def apply_global_css(self, path, **kwargs):
        with open(path, 'r') as f:
            css_template = f.read()

        css_string = css_template.format(**kwargs)

        provider = gtk.CssProvider()
        provider.load_from_data(css_string.encode())

        gtk.StyleContext.add_provider_for_display(
            gdk.Display.get_default(),
            provider,
            gtk.STYLE_PROVIDER_PRIORITY_USER)

    def get_active_editor(self, box):
        scroll = box.get_first_child()
        editor = scroll.get_child()
        return editor

    def get_all_editors(self):
        editors = []
        for page_num in range(self.get_n_pages()):
            hbox = self.get_nth_page(page_num)
            scroll = hbox.get_first_child()
            editor = scroll.get_child()
            editors.append(editor)

        return editors

    def on_switch_page_by_key(self, direction):
        current = self.get_current_page()
        total = self.get_n_pages()
        if total <= 1:
            return
        delta = -1 if direction == "prev" else 1
        next_page = (current + delta) % total
        self.set_current_page(next_page)

        hbox = self.get_nth_page(next_page)
        editor = self.get_active_editor(hbox)
        editor.grab_focus()

    def update_gtl_entry(self, key, editor):
        if not self.gtlbar_visible.get(key, False):
            return
        line = self.gtl_text.get(key)
        if line is None:
            buff = editor.get_buffer()
            iter_ = buff.get_iter_at_mark(buff.get_insert())
            line = str(iter_.get_line() + 1)
            self.gtl_text[key] = line
        self.navbar.gtl_entry.set_text(line)

    def on_switch_page(self, notebook, page, page_num):
        child = self.get_nth_page(page_num)

        key = getattr(child, "tab_key", None)
        editor = self.editor_instance.get(key)
        context = self.search_context.get(key)

        find_visible = self.findbar_visible.get(key, False)
        self.find_revealer.set_reveal_child(find_visible)

        gtl_visible = self.gtlbar_visible.get(key, False)
        self.gtl_revealer.set_reveal_child(gtl_visible)

        text = self.search_text.get(key, "")

        result_label = self.result_label.get(key, "")

        case_sensitive = self.case_sensitive.get(key, False)
        whole_word = self.whole_word.get(key, False)
        use_regex = self.use_regex.get(key, False)

        self.block_signal = True

        self.navbar.search_entry.set_text(text)
        self.navbar.case_sens_btn.set_active(case_sensitive)
        self.navbar.whole_word_btn.set_active(whole_word)
        self.navbar.regex_btn.set_active(use_regex)

        self.update_gtl_entry(key, editor)

        self.set_search_error_state(False)

        if self.search_error.get(key, False):
            self.set_search_error_state(True)

        self.navbar.result_label.set_text(result_label)

        self.block_signal = False

        has_result = (
            key in self.search_error and not self.search_error.get(key, False)
        )

        self.navbar.prev_btn.set_sensitive(has_result)
        self.navbar.next_btn.set_sensitive(has_result)

        if key is not None and editor is not None:
            self.key = key
            self.value = editor
            self.context = context

            box = self.get_tab_label(child)
            icon = box.get_first_child()
            tab_label = icon.get_next_sibling()
            label = tab_label.get_text()

            buff = self.value.get_buffer()
            loading = getattr(buff, "_is_loading", False)

            for w in (
                self.navbar.search_entry,
                self.navbar.gtl_entry,
            ):
                w.set_sensitive(not loading)

            if loading:
                self.update_window_title(label)
            else:
                self.update_window_title(label, buff.get_modified())
        else:
            pass

        if not hasattr(self.value, "_controller_insovr"):
            controller = gtk.EventControllerKey()
            controller.connect(
                "key-pressed", self.on_ins_key_pressed, self.value)
            editor.add_controller(controller)
            editor._controller_insovr = controller

        if not hasattr(buff, "_connected_signals"):
            buff.connect(
                "modified_changed",
                self.on_buffer_modified_changed, icon, label, self.key)
            buff.connect("changed", self.on_buffer_changed)
            buff.connect("mark_set", self.on_buffer_mark_set)
            buff._connected_signals = True

        if key in self.pending_reload:
            event_type = self.pending_reload.pop(key)
            gfile = getattr(child, "gfile", None)
            menu = self.app.get_active_window().menu
            if gfile:
                menu.handle_file_change(
                    event_type, gfile, self, key, editor)

    def on_ins_key_pressed(self, controller, keyval, keycode, state, ed):
        if keyval == gdk.KEY_Insert:
            ed.set_overwrite(not ed.get_overwrite())
            self.update_statusbar_cursor_info()
            return True

        return False

    def on_buffer_modified_changed(self, buff, icon, label, key):
        if getattr(buff, "_is_loading", False):
            return

        is_modified = buff.get_modified()

        if key in self.files:
            filename = self.files.get(key)
            label = os.path.basename(filename)
            if filename in self.admin_files:
                label = f"{label} [Admin]"

        self.update_window_title(label, is_modified)

        if is_modified:
            icon.set_from_icon_name(SAVE_ICON)
        else:
            icon.set_from_icon_name(EDIT_ICON)

    def on_buffer_changed(self, buff):
        if getattr(buff, "_is_loading", False):
            return

        if self.block_signal or self.key is None:
            return

        self.update_statusbar_cursor_info()

        if self.findbar_visible.get(self.key, False):
            self.on_search_entry_changed(self.navbar.search_entry)

    def on_buffer_mark_set(self, buff, loc, mark):
        if not hasattr(self, 'key') or self.key is None:
            return

        if getattr(buff, "_is_loading", False):
            return
        self.update_statusbar_cursor_info()

        if getattr(self, '_is_selecting', False) or \
                not buff.get_has_selection():
            return

        context = self.context

        if not context:
            return

        old_id = self.mark_set_timeout.get(self.key)
        if old_id:
            glib.source_remove(old_id)
            self.mark_set_timeout.pop(self.key, None)

        def delayed_mark_set():
            # Clear the stored ID since this timeout will auto-remove
            self.mark_set_timeout.pop(self.key, None)

            if getattr(self, '_is_selecting', False):
                return False

            count = context.get_occurrences_count()

            if not buff.get_has_selection():
                self.update_result_label(0 if count > 0 else -1, count)
                return False

            try:
                start, end = buff.get_selection_bounds()
                pos = context.get_occurrence_position(start, end)
                has_match = (pos > 0)

                self.update_result_label(pos if has_match else 0, count)
            except (ValueError, glib.Error):
                self.update_result_label(-1, count)

            return False

        # glib.timeout_add(100, delayed_mark_set)
        self.mark_set_timeout[self.key] = glib.timeout_add(
            100, delayed_mark_set)

    def update_statusbar_cursor_info(self):
        if not hasattr(self, "value") or self.value is None:
            return

        editor = self.value
        buff = editor.get_buffer()

        page = self.get_current_tab()
        filetype = getattr(page, "file_type", "")

        mode = "OVR" if editor.get_overwrite() else "INS"

        self.statusbar.show_line_col(buff, filetype, mode)

    def action_message(self, win, lbl_main, lbl_detail):
        dialog = gtk.Window()
        dialog.set_name("window")
        dialog.get_style_context().add_class("csd")
        dialog.set_transient_for(win)
        dialog.set_modal(True)
        dialog.set_resizable(False)
        dialog.set_hide_on_close(True)
        dialog.set_decorated(False)

        label_main = gtk.Label(label=lbl_main)
        label_main.set_css_classes(["title-3"])
        label_main.set_justify(gtk.Justification.CENTER)

        label_detail = gtk.Label(label=lbl_detail)
        label_detail.set_wrap(True)
        label_detail.set_justify(gtk.Justification.CENTER)

        box = gtk.Box(
            orientation=gtk.Orientation.VERTICAL, spacing=12,
            margin_top=15, margin_bottom=15,
            margin_start=15, margin_end=15)

        box.append(label_main)
        box.append(label_detail)

        return dialog, box

    def set_label(self, lbl, hbox, key, tooltip):
        tab_label_box = self.get_tab_label(hbox)
        label = tab_label_box.get_first_child().get_next_sibling()
        label.set_text(lbl)
        tab_label_box.set_tooltip_text(tooltip)

    def get_label(self):
        box = self.get_tab_label(self.get_current_tab())
        icon = box.get_first_child()
        tab_label = icon.get_next_sibling()
        return tab_label.get_text()

    def get_current_tab(self):
        return self.get_nth_page(self.get_current_page())

    def is_large_file(self, gfile):
        try:
            info = gfile.query_info(
                "standard::size",
                gio.FileQueryInfoFlags.NONE,
                None
            )
            return info.get_size() > 2 * 1024 * 1024
        except glib.Error:
            return False

    def new_tab(
        self, label, lang=None, tooltip=None,
        filetype=None, gfile=None, mimetype=None
    ):
        i = 0
        while i in self.editor_instance:
            i += 1
        key = i

        view = editor.Editor()

        buff = view.get_buffer()

        settings = gtksource.SearchSettings()
        context = gtksource.SearchContext.new(buff, settings)
        context.connect(
            "notify::occurrences-count", self.on_occurrences_notify)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.set_child(view)
        scroll.set_name("scroll_editor")

        hbox = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        hbox.set_size_request(100, -1)
        hbox.append(scroll)
        hbox.tab_key = key
        hbox.gfile = gfile
        if filetype:
            hbox.file_type = filetype

        self.editor_instance[key] = view
        self.search_context[key] = context

        box_lbl, lbl = self.create_tab_label(
            label, hbox, key, tooltip)

        self.append_page(hbox, box_lbl)
        self.set_tab_reorderable(hbox, True)

        self.set_current_page(self.page_num(hbox))

        if tooltip and os.path.exists(tooltip):
            if self.is_large_file(gfile):
                self.lazy_insert_file(
                    buff, gfile, lang, key, lbl, mimetype)
            else:
                try:
                    success, contents, _ = gfile.load_contents(None)
                    if success:
                        text = contents.decode("utf-8", "replace")
                        buff.set_text(text)
                        buff.set_language(self.get_language_for_buffer(lang, mimetype))
                        buff.place_cursor(buff.get_start_iter())
                        buff.set_modified(False)
                except glib.Error:
                    pass

        view.grab_focus()

        self.key = key
        self.value = self.editor_instance[key]
        self.context = self.search_context[key]

    def lazy_insert_file(self, buff, gfile, lang, key, label, mt):
        src_file = gtksource.File.new()
        src_file.set_location(gfile)
        loader = gtksource.FileLoader.new(buff, src_file)
        cancellable = gio.Cancellable()
        self.loader_cancellable[key] = cancellable

        def widget_status(status):
            for widget in (
                self.navbar.search_entry,
                self.navbar.gtl_entry,
            ):
                widget.set_sensitive(status)

        def buffer_commit_done():
            if getattr(buff, "_closed", False):
                return False
            label.get_style_context().remove_class("moving-gradient")
            buff._is_loading = False
            buff._is_buffer_ready = True
            buff.end_irreversible_action()
            buff.set_highlight_syntax(True)
            widget_status(True)

            glib.idle_add(
                lambda: self.on_search_entry_changed(self.navbar.search_entry),
                priority=glib.PRIORITY_HIGH_IDLE)
            return False

        def on_loaded(loader, result, *args):
            if cancellable.is_cancelled() or getattr(buff, "_closed", False):
                try:
                    loader.load_finish(result)
                except Exception:
                    pass
                return
            try:
                success = loader.load_finish(result)
                if success:
                    buff.set_language(self.get_language_for_buffer(lang, mt))
                    buff.place_cursor(buff.get_start_iter())
            except Exception:
                pass
            finally:
                self.loader_cancellable.pop(key, None)
                glib.idle_add(buffer_commit_done,
                              priority=glib.PRIORITY_HIGH_IDLE)

        buff.set_highlight_syntax(False)
        buff.begin_irreversible_action()
        buff._is_loading = True
        widget_status(False)
        label.get_style_context().add_class("moving-gradient")

        loader.load_async(
            glib.PRIORITY_LOW,
            cancellable,
            None,
            None,
            on_loaded,
            ()
        )

    def create_tab_label(self, label, hbox, data, tooltip=None, icon=None):
        if tooltip.startswith("Untitled"):
            val = 0
            while val in self.unsave.values():
                val += 1
            label = f"{label} {val + 1}"
            tooltip = f"{tooltip} {val + 1}"
            self.unsave[data] = val

        icon = icon or gtk.Image.new_from_icon_name(EDIT_ICON)
        icon.set_pixel_size(12)

        if tooltip in self.admin_files:
            label = f"{label} [Admin]"

        label_widget = gtk.Label(label=label)

        close_btn = gtk.Button.new_from_icon_name("window-close-symbolic")
        close_btn.set_focusable(False)
        close_btn.set_valign(gtk.Align.CENTER)
        close_btn.get_style_context().add_class("flat")
        close_btn.set_tooltip_text("Close Tab")
        close_btn.connect("clicked", self.close_tab, hbox)

        box_label = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=10)
        box_label.append(icon)
        box_label.append(label_widget)
        box_label.append(close_btn)
        box_label.set_tooltip_text(tooltip)

        return box_label, label_widget

    def close_tab(self, widget, child):
        data = None
        for key, _editor in self.editor_instance.items():
            if _editor == child.get_first_child().get_child():
                data = key
                break

        if data is None:
            return

        buff = self.editor_instance[data].get_buffer()
        label_tab = self.get_tab_label(
            child).get_first_child().get_next_sibling()
        tab_title = label_tab.get_text()

        def do_close():
            cancellable = self.loader_cancellable.pop(data, None)
            if cancellable:
                cancellable.cancel()

            self.close_the_tab(child, data)

            monitor = self.monitors.pop(data, None)
            if monitor:
                monitor.cancel()
            self.pending_reload.pop(data, None)

            path = self.files.pop(data, None)
            if path:
                self.app.unregister_file(path)

            if len(self.editor_instance) == 0:
                self.new_tab("Untitled", tooltip="Untitled")

        def after_confirm(response_id):
            if response_id == 0:
                return
            elif response_id == 2:
                self.save_current(
                    tab_title,
                    self.editor_instance[data],
                    data,
                    lambda success: success and do_close())
                return

            do_close()

        if (
            getattr(buff, "_is_loading", False) or not
            getattr(buff, "_is_buffer_ready", True)
        ):
            buff._closed = True
            do_close()
            return

        self.check_for_save(buff, data, after_confirm)
        self.value.grab_focus()

    def close_the_tab(self, box, data):
        text_view = self.editor_instance.get(data)
        if text_view:
            buff = text_view.get_buffer()

            try:
                buff.disconnect_by_func(self.on_buffer_modified_changed)
                buff.disconnect_by_func(self.on_buffer_changed)
                buff.disconnect_by_func(self.on_buffer_mark_set)
            except Exception:
                pass

            for attr in (
                "MARK_TYPE_1", "mark_attrs", "_controller_insovr", "buff"
            ):
                if hasattr(text_view, attr):
                    val = getattr(text_view, attr)
                    if isinstance(val, gtk.EventControllerKey):
                        text_view.remove_controller(val)
                    delattr(text_view, attr)

            text_view.set_buffer(None)

            if hasattr(text_view, "buff"):
                del text_view.buff

        del self.editor_instance[data]

        for d in (
            self.unsave,
            self.findbar_visible,
            self.search_text,
            self.result_label,
            self.case_sensitive,
            self.search_error,
            self.file_event_timer,
            self.whole_word,
            self.use_regex,
            self.search_context,
            self.gtlbar_visible,
            self.gtl_text
        ):
            d.pop(data, None)

        page_num = self.page_num(box)
        self.remove_page(page_num)

        gc.collect()

    def check_for_save(self, buff, key, callback):
        if not buff.get_modified():
            callback(None)
            return

        filename = (
            os.path.basename(self.files[key])
            if key in self.files
            else f"Untitled {self.unsave.get(key, 0) + 1}")

        dialog, box = self.action_message(
            self.app.get_active_window(),
            "Close Document",
            f'The document "{filename}" has been modified.\n'
            "Save changes before closing?\n"
            "Unsaved modifications will be lost.")

        btn_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_hexpand(True)
        btn_box.set_halign(gtk.Align.FILL)
        btn_box.set_homogeneous(True)

        def respond(response_id):
            dialog.destroy()
            callback(response_id)

        def make_button(label, response_id, name=None):
            btn = gtk.Button(label=label)
            btn.add_css_class("btn")
            if name:
                btn.get_style_context().add_class(name)
            btn.set_hexpand(True)
            btn.set_vexpand(False)
            btn.set_halign(gtk.Align.FILL)
            btn.set_margin_top(6)
            btn.set_margin_bottom(6)
            btn.connect("clicked", lambda *a: respond(response_id))
            return btn

        btn_cancel = make_button("Cancel", 0)
        btn_dont_save = make_button("Don't Save", 1, name="destructive-action")
        btn_save = make_button("Save", 2, name="suggested-action")

        btn_box.append(btn_cancel)
        btn_box.append(btn_dont_save)
        btn_box.append(btn_save)

        box.append(btn_box)

        dialog.set_child(box)
        dialog.present()
        btn_save.grab_focus()

    def save_as_file(self, editor, key, suggested_name, on_done):
        def after_file_chosen(dialog, result):
            try:
                _file = dialog.save_finish(result)
                self.save_the_file(_file.get_path(), editor, key)
                on_done(True)
            except Exception:
                on_done(False)

        dialog = gtk.FileDialog()
        dialog.set_initial_name(suggested_name)
        dialog.save(self.app.get_active_window(), None, after_file_chosen)

    def save_the_file(self, filename, editor, key):
        try:
            if key in self.monitors:
                self.monitors[key].cancel()
                del self.monitors[key]

            old_filename = self.files.get(key)

            buff = editor.get_buffer()
            start, end = buff.get_bounds()
            text = buff.get_text(start, end, False)

            text += "\n" if not text.endswith("\n") else ""

            try:
                gfile = gio.File.new_for_path(filename)
                gfile.replace_contents(
                    bytes(text, "utf-8"), None, False,
                    gio.FileCreateFlags.NONE, None)

                self.after_save(filename, editor, key, gfile, old_filename)
                return True
            except glib.Error as e:
                if e.code != 14:
                    self.show_save_error(
                        filename,
                        "Check that you have write access to this file!")
                    return False

                admin_uri = f"admin://{filename}"
                admin_file = gio.File.new_for_uri(admin_uri)

                def on_admin_mounted(file, res, data):
                    try:
                        file.mount_enclosing_volume_finish(res)
                    except glib.Error as e:
                        if e.code != 17:
                            self.show_save_error(filename, str(e))
                            return

                    try:
                        file.replace_contents(
                            bytes(text, "utf-8"),
                            None,
                            False,
                            gio.FileCreateFlags.NONE,
                            None)
                    except glib.Error as e:
                        if e.code == 14:
                            return

                        self.show_save_error(filename, str(e))
                        return

                    self.admin_files.add(filename)
                    self.after_save(filename, editor, key, file, old_filename)

                admin_file.mount_enclosing_volume(
                    gio.MountMountFlags.NONE,
                    None,
                    None,
                    on_admin_mounted,
                    None)
        except Exception as e:
            self.show_save_error(filename, str(e))
            return False

    def after_save(self, filename, editor, key, gfile, old_filename):
        if old_filename and old_filename != filename:
            self.app.unregister_file(old_filename)

        info = gfile.query_info(
            "standard::*", gio.FileQueryInfoFlags.NONE, None)
        mime_type = info.get_content_type()

        lang_man = gtksource.LanguageManager.get_default()
        lang = lang_man.guess_language(filename, mime_type)

        buff = editor.get_buffer()
        buff.set_language(self.get_language_for_buffer(lang, mime_type))
        buff.set_modified(False)

        subtype = mime_type.split("/", 1)[1]
        filetype = (subtype[2:].upper()
                    if subtype.startswith("x-")
                    else subtype.upper())

        page = self.get_current_tab()
        page.gfile = gfile
        page.file_type = filetype

        self.files[key] = filename

        old = self.monitors.pop(key, None)
        if old:
            old.cancel()
        monitor = gfile.monitor_file(gio.FileMonitorFlags.NONE, None)
        menu = self.app.get_active_window().menu
        monitor.connect("changed", menu.file_changed, self, key, page)
        self.monitors[key] = monitor

        if key in self.unsave:
            del self.unsave[key]

        label = os.path.basename(filename)
        if filename in self.admin_files:
            label = f"{label} [Admin]"
        self.set_label(label, editor.get_parent().get_parent(), key, filename)
        self.update_window_title(label)

        self.app.register_file(filename, self.app.get_active_window(), key)
        self.recently_saved[key] = time.monotonic()

    def show_save_error(self, filename, text):
        dialog, vbox = self.action_message(
            self.app.get_active_window(),
            "Error",
            f'Could not save file "{filename}"\n'
            f"{text}")
        menu = self.app.get_active_window().menu
        btn_close = menu.make_button(dialog, "Close")
        btn_close.get_style_context().add_class("suggested-action")
        vbox.append(btn_close)
        dialog.set_child(vbox)
        dialog.present()

    def save_current(self, tab_title, editor, key, on_done):
        if key not in self.files:
            self.save_as_file(editor, key, tab_title, on_done)
        else:
            success = self.save_the_file(self.files[key], editor, key)
            on_done(success)

    def update_window_title(self, title=None, modified=False):
        from .helper import config
        filepath = config.get_filepath()
        prefix = "* " if modified else ""
        title_text = f"{prefix}{filepath}"
        self.title_label.set_text(title_text)
        self.window.set_title(title_text)

    def on_close_window(self, window):
        # Check if there are any unsaved changes
        has_unsaved = False
        for key, _editor in self.editor_instance.items():
            buff = _editor.get_buffer()
            if buff.get_modified():
                has_unsaved = True
                break

        if not has_unsaved:
            self.finalize_close(window)
            return

        # Show Save/Exit/Cancel prompt
        dialog, vbox = self.action_message(
            window,
            "Unsaved Changes",
            "You have unsaved changes.")

        btn_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_hexpand(True)
        btn_box.set_halign(gtk.Align.FILL)
        btn_box.set_homogeneous(True)

        def on_save_and_exit():
            # Save the file then exit
            label = self.get_label()
            def on_saved(success):
                dialog.destroy()
                if success:
                    self.finalize_close(window)
                # If save failed, stay open (dialog already destroyed)

            self.save_current(label, self.value, self.key, on_saved)

        def on_exit_without_saving():
            dialog.destroy()
            self.finalize_close(window)

        def on_cancel():
            dialog.destroy()

        def make_button(label, callback, suggested=False):
            btn = gtk.Button(label=label)
            btn.add_css_class("btn")
            if suggested:
                btn.get_style_context().add_class("suggested-action")
            btn.set_hexpand(True)
            btn.set_vexpand(False)
            btn.set_halign(gtk.Align.FILL)
            btn.set_margin_top(6)
            btn.set_margin_bottom(6)
            btn.connect("clicked", lambda *a: callback())
            return btn

        btn_save = make_button("Save and Exit", on_save_and_exit, suggested=True)
        btn_exit = make_button("Exit Without Saving", on_exit_without_saving)
        btn_cancel = make_button("Cancel", on_cancel)

        btn_box.append(btn_save)
        btn_box.append(btn_exit)
        btn_box.append(btn_cancel)

        vbox.append(btn_box)

        dialog.set_child(vbox)
        dialog.present()
        btn_save.grab_focus()

    def show_unsaved_dialog(self, window, modified_tabs):
        dialog, vbox = self.action_message(
            window,
            "Save Documents",
            "The following documents have been modified.\n"
            "Save changes before closing?")

        store = gio.ListStore.new(TabRow)

        for tab in modified_tabs:
            item = TabRow(tab["label"], tab)
            store.append(item)

        listview = self.build_modified_listview(store)

        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.PolicyType.NEVER, gtk.PolicyType.AUTOMATIC)
        scroller.set_propagate_natural_height(True)
        scroller.set_vexpand(True)
        scroller.set_max_content_height(300)
        scroller.set_child(listview)
        vbox.append(scroller)

        btn_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_hexpand(True)
        btn_box.set_halign(gtk.Align.FILL)
        btn_box.set_homogeneous(True)

        def respond(response_id):
            self.handle_dialog_response(response_id, store, window, dialog)

        def make_button(label, response_id, name=None):
            btn = gtk.Button(label=label)
            btn.add_css_class("btn")
            if name:
                btn.get_style_context().add_class(name)
            btn.set_hexpand(True)
            btn.set_vexpand(False)
            btn.set_halign(gtk.Align.FILL)
            btn.set_margin_top(6)
            btn.set_margin_bottom(6)
            btn.connect("clicked", lambda *a: respond(response_id))
            return btn

        btn_cancel = make_button("Cancel", 0)
        btn_discard = make_button("Discard All", 1, name="destructive-action")
        btn_save = make_button("Save", 2, name="suggested-action")

        btn_box.append(btn_cancel)
        btn_box.append(btn_discard)
        btn_box.append(btn_save)
        vbox.append(btn_box)

        dialog.set_child(vbox)
        dialog.present()
        btn_save.grab_focus()

    def build_modified_listview(self, store):
        selection = gtk.SingleSelection(model=store)

        def create_item(factory):
            hbox = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=8)
            toggle = gtk.CheckButton()
            label = gtk.Label(xalign=0)
            hbox.append(toggle)
            hbox.append(label)
            return hbox

        def bind_item(factory, list_item):
            row = list_item.get_child()
            toggle = row.get_first_child()
            label = toggle.get_next_sibling()
            item = list_item.get_item()

            def on_toggled(btn):
                item.set_property("checked", btn.get_active())

            toggle.set_active(item.checked)
            toggle.connect("toggled", on_toggled)
            label.set_text(item.label)

        factory = gtk.SignalListItemFactory()
        factory.connect(
            "setup", lambda f, item: item.set_child(create_item(f)))
        factory.connect("bind", bind_item)

        listview = gtk.ListView(model=selection, factory=factory)
        listview.set_vexpand(True)
        return listview

    def handle_dialog_response(self, response_id, store, window, dialog):
        dialog.destroy()
        if response_id == 0:
            return

        if response_id == 2:
            total = store.get_n_items()
            to_save = [store.get_item(i)
                       for i in range(total) if store.get_item(i).checked]

            if not to_save:
                self.finalize_close(window)
                return

            remaining = {"count": len(to_save)}

            def on_done(success):
                if success:
                    remaining["count"] -= 1
                    if remaining["count"] == 0:
                        self.finalize_close(window)

            for item in to_save:
                tab = item.tabdata
                self.save_current(
                    tab["label"], tab["editor"], tab["key"], on_done)
        else:
            self.finalize_close(window)

    def finalize_close(self, window):
        if hasattr(self, "loader_cancellable"):
            for key, cancellable in list(self.loader_cancellable.items()):
                try:
                    if cancellable and not cancellable.is_cancelled():
                        cancellable.cancel()
                except Exception:
                    pass
            self.loader_cancellable.clear()

        nb = window.nb
        if hasattr(nb, "switch_id"):
            nb.disconnect(nb.switch_id)

        if window in self.app.windows:
            self.app.windows.remove(window)

        attrs_to_del = [
            "editor_instance", "files", "unsave", "key", "value",
            "monitors", "pending_reload", "recently_saved", "switch_id",
            "findbar_visible", "search_text", "result_label", "context"
            "case_sensitive", "whole_word", "use_regex",
            "search_error", "file_event_timer",
            "block_signal", "search_context", "gtlbar_visible", "gtl_text",
            "search_cancellable", "loader_cancellable", "last_button_status"
        ]

        for attr in attrs_to_del:
            if hasattr(self, attr):
                delattr(self, attr)

        del window.nb
        del window.menu

        config.unregister_widgets_by_window(window)
        window.destroy()
        del window

        gc.collect()
