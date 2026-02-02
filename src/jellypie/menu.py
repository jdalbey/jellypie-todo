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
import time
from . import window
from .helper import (
    gtk, gio, glib, gtksource, switchmenu, stylescheme, config, gdk,
    get_icon_dir, get_css_path, get_app_version)


LICENSE = """
Copyright (c) 2010-2025 Zulfian <zulfian1732@gmail.com>

Jollpi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Jollpi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with Jollpi. if not, see <https://www.gnu.org/licenses/>.
"""

MENU_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="menubar">
    <section>
      <item>
        <attribute name="action">win.new_window</attribute>
        <attribute name="label" translatable="yes">New Window</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name="action">win.save</attribute>
        <attribute name="label" translatable="yes">Save</attribute>
      </item>
      <item>
        <attribute name="action">win.save_as</attribute>
        <attribute name="label" translatable="yes">Save As...</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name="action">win.find</attribute>
        <attribute name="label" translatable="yes">Find...</attribute>
      </item>
      <item>
        <attribute name="action">win.replace</attribute>
        <attribute name="label" translatable="yes">Replace...</attribute>
      </item>
      <item>
        <attribute name="action">win.go_to_line</attribute>
        <attribute name="label" translatable="yes">Go to Line...</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name="action">win.print</attribute>
        <attribute name="label" translatable="yes">Print</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name="action">win.font</attribute>
        <attribute name="label" translatable="yes">Select Font...</attribute>
      </item>
      <submenu>
        <attribute name="label" translatable="yes">View Options</attribute>
          <section>
            <!-- VIEW_OPTIONS_HERE -->
          </section>
      </submenu>
      <submenu>
        <attribute name="label" translatable="yes">Style Scheme</attribute>
        <section>
          <item>
            <attribute name="custom">radio</attribute>
          </item>
        </section>
      </submenu>
    </section>
    <section>
      <item>
        <attribute name="action">win.key_sc</attribute>
      <attribute name="label" translatable="yes">Keyboard Shortcuts</attribute>
      </item>
      <item>
        <attribute name="action">win.support</attribute>
      <attribute name="label" translatable="yes">Support Developer</attribute>
      </item>
      <item>
        <attribute name="action">win.about</attribute>
        <attribute name="label" translatable="yes">About Jollpi</attribute>
      </item>
    </section>
  </menu>
</interface>
"""

MENU_XML = MENU_XML.replace(
    "<!-- VIEW_OPTIONS_HERE -->", switchmenu.generate_switch_menu())

SC_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkShortcutsWindow" id="shortcuts-windows">
    <property name="modal">1</property>
    <child>
      <object class="GtkShortcutsSection">
        <property name="section-name">page1</property>
        <property name="max-height">13</property>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title">Window and Tab Management</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;N</property>
                <property name="title" translatable="yes">New window</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;T</property>
                <property name="title" translatable="yes">New tab</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;Page_Down</property>
                <property name="title">Move to the next tab</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;Page_Up</property>
                <property name="title">Move to the previous tab</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;W</property>
                <property name="title">Close document</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;comma</property>
                <property name="title">Show keyboard shortcuts</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title">Document Navigation</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;G</property>
                <property name="title" translatable="yes">Go to line</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;Home</property>
                <property name="title">Move to beginning of document</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;End</property>
                <property name="title">Move to end of document</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;Up</property>
          <property name="title">Move to start of previous paragraph</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;Down</property>
                <property name="title">Move to end of next paragraph</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title">Text Editing and Deletion</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;BackSpace</property>
            <property name="title">Delete from cursor to word start</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;Delete</property>
              <property name="title">Delete from cursor to word end</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
    <property name="accelerator">&lt;ctrl&gt;&lt;Shift&gt;BackSpace</property>
        <property name="title">Delete from cursor to paragraph start</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
      <property name="accelerator">&lt;ctrl&gt;&lt;Shift&gt;Delete</property>
          <property name="title">Delete from cursor to paragraph end</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;Alt&gt;Up</property>
                <property name="title">Move selected lines up</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;Alt&gt;Down</property>
                <property name="title">Move selected lines down</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title">File Operations</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;O</property>
                <property name="title" translatable="yes">Open file</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;S</property>
                <property name="title" translatable="yes">Save</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
            <property name="accelerator">&lt;ctrl&gt;&lt;shift&gt;S</property>
                <property name="title">Save as</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;P</property>
                <property name="title">Print Document</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title">Clipboard Operations</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;C</property>
                <property name="title" translatable="yes">Copy</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;X</property>
                <property name="title" translatable="yes">Cut</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;V</property>
                <property name="title" translatable="yes">Paste</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;A</property>
                <property name="title" translatable="yes">Select all</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
            <property name="accelerator">&lt;ctrl&gt;&lt;shift&gt;A</property>
                <property name="title">Unselect all</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;period</property>
                <property name="title">Insert emoji</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title">Search and Replace</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;F</property>
                <property name="title" translatable="yes">Search</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;R</property>
                <property name="title">Search and replace</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">Up</property>
            <property name="title">Select previous match in document</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">Down</property>
                <property name="title">Select next match in document</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes">Undo and Redo</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">&lt;ctrl&gt;Z</property>
                <property name="title">Undo previous command</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
            <property name="accelerator">&lt;ctrl&gt;&lt;shift&gt;Z</property>
                <property name="title">Redo previous command</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes">Miscellaneous</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">Insert</property>
                <property name="title">Toggle insert/overwrite</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="accelerator">F6</property>
                <property name="title">Select font</property>
              </object>
            </child>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>
"""


class Menu():
    def __init__(self, window, nav, find_rev, gtl_rev):
        self.window = window
        self.app = window.get_application()
        self.navbar = nav
        self.find_revealer = find_rev
        self.gtl_revealer = gtl_rev
        self.header = gtk.HeaderBar()

        self.add_actions()

    def get_tab(self):
        return self.app.get_active_window().nb

    def create_menu_popover(self, items):
        menu = gio.Menu()
        for label, action_name in items:
            menu.append(label, action_name)

        popover = gtk.PopoverMenu.new_from_model(menu)
        popover.set_offset(50, 0)
        return popover

    # View options are now hardcoded and not user-configurable
    # def create_switch(self, custom_ids, callback=None):
    #     switches = {}
    #     for cid in custom_ids:
    #         box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=6)
    #         box.set_hexpand(True)
    #         box.set_margin_start(12)
    #         box.set_margin_end(12)
    #         box.set_valign(gtk.Align.CENTER)
    #
    #         label = gtk.Label(label=f"{cid.replace('_', ' ').title()}")
    #         label.set_halign(gtk.Align.START)
    #         label.set_hexpand(True)
    #
    #         switch = gtk.Switch()
    #         switch.set_halign(gtk.Align.END)
    #         switch.set_active(config.get_config(cid))
    #
    #         config.register(switch, cid, mode="switch")
    #
    #         if callback:
    #             switch.connect("state-set", callback, cid)
    #
    #         box.append(label)
    #         box.append(switch)
    #         switches[cid] = box
    #
    #     return switches

    # View options are now hardcoded and not user-configurable
    # def on_toggled(self, switch, state, cid):
    #     config.set_config(cid, state)
    #     for win in self.app.windows:
    #         for editor in win.nb.get_all_editors():
    #             match cid:
    #                 case "wrap_mode":
    #                     wc = gtk.WrapMode.WORD_CHAR
    #                     nn = gtk.WrapMode.NONE
    #                     editor.set_wrap_mode(wc if state else nn)
    #                 case "auto_indent":
    #                     editor.set_auto_indent(state)
    #                 case "line_number":
    #                     editor.set_show_line_numbers(state)
    #                 case "right_margin":
    #                     editor.set_show_right_margin(state)
    #                 case "line_mark":
    #                     editor.set_show_line_marks(state)
    #
    #     config.update_all_widget(cid, state, mode="switch")

    def create_scheme_radio(self, schemes, default_scheme, callback):
        buttons = []
        group = None

        for label, scheme in schemes.items():
            btn = gtk.CheckButton(label=f"    {label}")
            if group:
                btn.set_group(group)
            else:
                group = btn

            btn.connect("toggled", callback, scheme, label)
            if scheme == default_scheme:
                btn.set_active(True)

            buttons.append(btn)

        config.register(buttons, "scheme", mode="radio")
        return buttons

    def on_scheme_toggled(self, button, scheme_name, label_name):
        config.set_config("scheme", scheme_name)
        if button.get_active():
            for win in self.app.windows:
                for editor in win.nb.get_all_editors():
                    buff = editor.get_buffer()
                    sch_obj = gtksource.StyleSchemeManager()
                    style = sch_obj.get_scheme(scheme_name)
                    buff.set_style_scheme(style)

            config.update_all_widget("scheme", label_name, mode="radio")

    def add_actions(self):
        shortcuts = config.get_config("shortcuts")
        if not shortcuts:
            shortcuts = {}

        self.create_action(
            "save", self.on_save, shortcuts.get("save", "<Control>s"))
        self.create_action(
            "find", self.on_find, shortcuts.get("find", "<Control>f"))
        self.create_action(
            "go_to_line", self.on_go_to_line, shortcuts.get("go_to_line", "<Control>g"))
        self.create_action(
            "font", self.on_select_font, shortcuts.get("font", "F6"))
        self.create_action(
            "quick_help", self.on_quick_help, shortcuts.get("quick_help", "F1"))
        self.create_action(
            "quit", self.on_quit, shortcuts.get("quit", "<Control>q"))
        self.create_action(
            "mark_done", self.on_mark_done, shortcuts.get("mark_done", "<Control>d"))
        self.create_action(
            "format_bold", self.on_format_bold, shortcuts.get("format_bold", "<Control>b"))
        self.create_action(
            "format_italic", self.on_format_italic, shortcuts.get("format_italic", "<Control>i"))
        self.create_action(
            "format_monospace", self.on_format_monospace, shortcuts.get("format_monospace", "<Control>t"))

    def create_action(self, name, callback, shortcut=None):
        action = gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.window.add_action(action)

        if shortcut:
            self.app.set_accels_for_action(f"win.{name}", [shortcut])

    def on_tab_prev(self, action, param):
        print("tab prev")
        tab = self.get_tab()
        tab.on_switch_page_by_key("prev")

    def on_tab_next(self, action, param):
        tab = self.get_tab()
        tab.on_switch_page_by_key("next")

    def on_open_file(self, action, param):
        def on_files_opened(dialog, result):
            try:
                files = dialog.open_multiple_finish(result)
                paths = [f.get_path() for f in files]
                self.open_file(paths)
            except glib.Error as e:
                print("Dialog error:", e.message)

        dialog = gtk.FileDialog()
        dialog.set_title("Open File")
        dialog.set_modal(True)

        text_filter = gtk.FileFilter()
        text_filter.set_name("Text Files")
        text_filter.add_mime_type("text/plain")
        text_filter.add_suffix("txt")

        all_filter = gtk.FileFilter()
        all_filter.set_name("All Files")
        all_filter.add_pattern("*")

        filters = gio.ListStore.new(gtk.FileFilter)
        filters.append(text_filter)
        filters.append(all_filter)

        dialog.set_filters(filters)

        dialog.open_multiple(
            self.app.get_active_window(), None, on_files_opened)

    def make_button(self, dialog, lbl, editor=None):
        btn_close = gtk.Button(label=lbl)
        btn_close.add_css_class("btn")
        if editor:
            btn_close.connect(
                "clicked",
                lambda btn: (dialog.close(), editor.grab_focus()))
        else:
            btn_close.connect(
                "clicked", lambda btn: dialog.close())
        return btn_close

    def open_file(self, paths):
        tab = self.get_tab()

        for filename in paths:
            basename = os.path.basename(filename)

            if filename in tab.files.values():
                continue

            if self.app.is_file_open(filename):
                dialog, vbox = tab.action_message(
                    self.app.get_active_window(),
                    "File already open",
                    f'This file "{basename}" '
                    "is already open in another window")

                btn_close = self.make_button(dialog, "Close")
                btn_close.get_style_context().add_class("suggested-action")
                vbox.append(btn_close)
                dialog.set_child(vbox)
                dialog.present()

                continue

            try:
                if filename in tab.admin_files:
                    gfile = gio.File.new_for_uri(f"admin://{filename}")
                else:
                    gfile = gio.File.new_for_path(filename)
                info = gfile.query_info(
                    "standard::content-type",
                    gio.FileQueryInfoFlags.NONE, None)
                mime_type = info.get_content_type()
            except glib.Error:
                mime_type = "text/plain"

            lang_man = gtksource.LanguageManager()
            lang = lang_man.get_default().guess_language(
                filename, mime_type)
            is_text = True

            if not lang and not mime_type.startswith("text"):
                try:
                    with open(filename, "rb") as f:
                        snippet = f.read(2048)
                        snippet.decode("utf-8")
                except (UnicodeDecodeError, OSError):
                    is_text = False

            if not is_text:
                dialog, vbox = tab.action_message(
                    self.app.get_active_window(),
                    "Binary file opened",
                    f'The file "{basename}" is a binary file.\n'
                    "Its content cannot be displayed")

                btn_close = self.make_button(dialog, "Close")
                btn_close.get_style_context().add_class("suggested-action")
                vbox.append(btn_close)
                dialog.set_child(vbox)
                dialog.present()
            else:
                try:
                    subtype = mime_type.split("/", 1)[1]
                    filetype = (subtype[2:].upper()
                                if subtype.startswith("x-")
                                else subtype.upper())
                    tab.new_tab(
                        basename, lang, filename, filetype, gfile, mime_type)
                    tab.files[tab.key] = filename

                    hbox = tab.get_current_tab()

                    if tab.monitors.get(tab.key) is None:
                        monitor = gfile.monitor_file(
                            gio.FileMonitorFlags.NONE, None)
                        monitor.connect(
                            "changed", self.file_changed,
                            tab, tab.key, hbox)
                        tab.monitors[tab.key] = monitor

                    self.app.register_file(
                        filename, self.app.get_active_window(), tab.key)

                except Exception as e:
                    dialog, vbox = tab.action_message(
                        self.app.get_active_window(),
                        f'Could not open file: "{basename}".\n{str(e)}')

                    btn_close = self.make_button(dialog, "Close")
                    btn_close.get_style_context().add_class("suggested-action")
                    vbox.append(btn_close)
                    dialog.set_child(vbox)
                    dialog.present()

    def file_changed(self, monitor, _file, otr_file, event_type, tab, key, hb):
        if key not in tab.files:
            return

        if event_type not in {
            gio.FileMonitorEvent.CHANGED,
            gio.FileMonitorEvent.DELETED,
            gio.FileMonitorEvent.RENAMED,
        }:
            return

        last_saved = tab.recently_saved.get(key)
        if last_saved and time.monotonic() - last_saved < 1.5:
            return

        if key in tab.file_event_timer:
            return

        gfile = getattr(hb, "gfile", None)
        if gfile is None:
            return

        ed = tab.get_active_editor(hb)

        def delayed_handler():
            del tab.file_event_timer[key]
            exists = gfile.query_exists(None)
            event = "changed" if exists else "removed"

            if key == tab.key:
                self.handle_file_change(event, gfile, tab, key, ed)
            else:
                tab.pending_reload[key] = event
            return False

        timeout_id = glib.timeout_add(300, delayed_handler)
        tab.file_event_timer[key] = timeout_id

    def handle_file_change(self, event, gfile, tab, key, editor):
        basename = gfile.get_basename()

        def on_action_response(dialog, default_btn):
            def handler(button):
                dialog.close()
                if default_btn == "Reload":
                    try:
                        success, contents, etag = gfile.load_contents(None)
                        text = contents.decode("utf-8", errors="replace")
                        editor = tab.editor_instance[key]
                        buff = editor.get_buffer()
                        buff.set_text(text)
                        buff.set_modified(False)
                    except Exception:
                        pass
                elif default_btn == "Save As":
                    editor = tab.editor_instance[key]
                    tab.save_as_file(editor, key, basename, self.on_save_done)
            return handler

        def do_action(message, detail, default_btn):
            dialog, vbox = tab.action_message(self.window, message, detail)

            btn_box = gtk.Box(
                orientation=gtk.Orientation.HORIZONTAL, spacing=12)
            btn_box.set_hexpand(True)
            btn_box.set_halign(gtk.Align.FILL)
            btn_box.set_homogeneous(True)

            btn_cancel = self.make_button(dialog, "Cancel", editor)
            btn_action = gtk.Button(label=default_btn)
            btn_action.get_style_context().add_class("suggested-action")
            btn_action.connect(
                "clicked", on_action_response(dialog, default_btn))
            btn_box.append(btn_cancel)
            btn_box.append(btn_action)

            vbox.append(btn_box)

            dialog.set_child(vbox)
            dialog.present()
            btn_action.grab_focus()

        if event == "changed":
            do_action(
                "File Changed",
                f'The file "{basename}" was modified on disk.\n'
                "Do you want to reload it?",
                "Reload")

        elif event == "removed":
            do_action(
                "File Removed",
                f'The file "{basename}" is no longer available.\n'
                '(renamed, moved, or deleted).',
                "Save As")

    def on_new_tab(self, action, param):
        tab = self.get_tab()
        tab.new_tab("Untitled", tooltip="Untitled")

    def on_new_window(self, action, param):
        win = window.MainWindow(application=self.app)
        if win not in self.app.windows:
            self.app.windows.append(win)
        win.present()

    def on_save(self, action, param):
        tab = self.get_tab()
        label = tab.get_label()
        tab.save_current(label, tab.value, tab.key, self.on_save_done)

    def on_save_as(self, action, param):
        tab = self.get_tab()
        tab_label = tab.get_label()
        tab.save_as_file(tab.value, tab.key, tab_label, self.on_save_done)

    def on_save_done(self, success):
        if success:
            pass

    def on_find(self, action, param):
        self.show_find_replace()

    def show_find_replace(self):
        tab = self.get_tab()
        tab.findbar_visible[tab.key] = True
        tab.gtlbar_visible[tab.key] = False

        try:
            context = tab.search_context.get(tab.key)
            if context:
                context.set_highlight(True)
        except Exception:
            pass

        self.find_revealer.set_reveal_child(True)
        self.gtl_revealer.set_reveal_child(False)
        self.navbar.search_entry.grab_focus()

    def on_go_to_line(self, action, param):
        tab = self.get_tab()
        tab.gtlbar_visible[tab.key] = True
        tab.findbar_visible[tab.key] = False

        buff = tab.value.get_buffer()
        iter_ = buff.get_iter_at_mark(buff.get_insert())
        current_line = iter_.get_line() + 1

        self.navbar.gtl_entry.set_text(str(current_line))
        tab.gtl_text[tab.key] = str(current_line)

        self.gtl_revealer.set_reveal_child(True)
        self.find_revealer.set_reveal_child(False)
        self.navbar.gtl_entry.grab_focus()

    def on_print(self, action, param):
        tab = self.get_tab()
        hbox = tab.get_current_tab()
        editor = tab.get_active_editor(hbox)
        font_desc = editor.get_pango_context().get_font_description()

        if font_desc:
            size = font_desc.get_size() / 1024
            size = max(6, size - 4)
            font_desc.set_size(int(size * 1024))
            font_name = font_desc.to_string()

        compositor = gtksource.PrintCompositor.new_from_view(editor)
        compositor.set_wrap_mode(gtk.WrapMode.CHAR)
        compositor.set_highlight_syntax(True)
        compositor.set_print_line_numbers(True)
        compositor.set_header_format(
            True, "Printed on %A, %d-%m-%Y", None, "by Jollpi")

        try:
            name = os.path.basename(tab.files[tab.key])
        except (KeyError, AttributeError):
            name = "Untitled"

        compositor.set_footer_format(True, "%T", name, "Page %N/%Q")
        compositor.set_print_header(True)
        compositor.set_print_footer(True)
        compositor.set_body_font_name(font_name)

        print_op = gtk.PrintOperation()
        print_op.set_show_progress(True)
        print_op.connect("begin-print", self.begin_print, compositor)
        print_op.connect("draw-page", self.draw_page, compositor)

        res = print_op.run(
            gtk.PrintOperationAction.PRINT_DIALOG,
            self.app.get_active_window())

        if res == gtk.PrintOperationResult.ERROR:
            dialog, vbox = tab.action_message(
                self.app.get_active_window(),
                "Error", f'Error printing file: "{name}"')
        elif res == gtk.PrintOperationResult.APPLY:
            dialog, vbox = tab.action_message(
                self.app.get_active_window(),
                "Information", f'File printed: "{name}"')
        else:
            return

        btn_close = self.make_button(dialog, "Close", editor)
        btn_close.get_style_context().add_class("suggested-action")
        vbox.append(btn_close)
        dialog.set_child(vbox)
        dialog.present()

    def begin_print(self, operation, context, compositor):
        while not compositor.paginate(context):
            pass
        n_pages = compositor.get_n_pages()
        operation.set_n_pages(n_pages)

    def draw_page(self, operation, context, page_nr, compositor):
        compositor.draw_page(context, page_nr)

    def on_select_font(self, action, param):
        from gi.repository import Pango

        font_dialog = gtk.FontDialog()
        font_dialog.set_modal(True)

        # Get current font settings from config
        current_family = config.get_config("font_family") or "Noto Sans Mono"
        current_size = config.get_config("font_size") or 14
        current_weight = config.get_config("font_weight") or 400

        # Map weight to style word for proper font string
        weight_to_style = {
            700: "Bold",
            600: "SemiBold",
            500: "Medium",
            400: "",  # Regular/Normal - omit
            300: "Light",
        }
        style_word = weight_to_style.get(current_weight, "")

        # Create font string in format: "FAMILY [STYLE] SIZE"
        if style_word:
            font_string = f"{current_family} {style_word} {current_size}"
        else:
            font_string = f"{current_family} {current_size}"

        font_desc = Pango.FontDescription.from_string(font_string)

        def on_response(dialog, result):
            try:
                font = dialog.choose_font_finish(result)

                # Use the family directly from the font description
                family = font.get_family()
                ukuran = int(font.get_size() / 1024)
                tebal = int(font.get_weight())  # Convert enum to integer

                win = self.app.get_active_window()
                css_path = get_css_path()
                win.nb.apply_global_css(
                    css_path, family=family, size=ukuran, weight=tebal)

                config.set_config("font_family", family)
                config.set_config("font_size", ukuran)
                config.set_config("font_weight", tebal)
            except glib.Error:
                pass

        # Pass current font as initial value
        font_dialog.choose_font(
            self.app.get_active_window(), font_desc, None, on_response)

    def on_quit(self, action, param):
        self.window.close()

    def on_mark_done(self, action, param):
        from datetime import datetime

        tab = self.get_tab()
        editor = tab.value
        if not editor:
            return

        buff = editor.get_buffer()

        # Get cursor position
        cursor_mark = buff.get_insert()
        cursor_iter = buff.get_iter_at_mark(cursor_mark)
        line_num = cursor_iter.get_line()

        # Get start and end of current line
        success, line_start = buff.get_iter_at_line(line_num)
        if not success:
            return

        success, line_end = buff.get_iter_at_line(line_num)
        if not success:
            return

        if not line_end.ends_line():
            line_end.forward_to_line_end()

        # Get line text
        line_text = buff.get_text(line_start, line_end, False)

        # Skip if line is empty
        if not line_text.strip():
            return

        # Create marked line with checkmark and timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        marked_line = f"✓ {line_text} [{timestamp}]"

        # Begin user action for undo grouping
        buff.begin_user_action()

        # Delete current line (including newline if not last line)
        success, delete_start = buff.get_iter_at_line(line_num)
        if not success:
            buff.end_user_action()
            return

        success, delete_end = buff.get_iter_at_line(line_num)
        if not success:
            buff.end_user_action()
            return

        if not delete_end.ends_line():
            delete_end.forward_to_line_end()
        # Include the newline character if there is one
        if not delete_end.is_end():
            delete_end.forward_char()
        buff.delete(delete_start, delete_end)

        # Move to end of buffer
        end_iter = buff.get_end_iter()

        # Add newline before if buffer doesn't end with one
        if not end_iter.starts_line() and end_iter.get_offset() > 0:
            buff.insert(end_iter, "\n")
            end_iter = buff.get_end_iter()

        # Insert marked line at end
        buff.insert(end_iter, marked_line + "\n")

        buff.end_user_action()

    def on_format_bold(self, action, param):
        """Wrap selection with **text** for bold formatting"""
        self._apply_formatting("**", "**")

    def on_format_italic(self, action, param):
        """Wrap selection with *text* for italic formatting"""
        self._apply_formatting("*", "*")

    def on_format_monospace(self, action, param):
        """Wrap selection with `text` for monospace formatting"""
        self._apply_formatting("`", "`")

    def _apply_formatting(self, prefix, suffix):
        """Apply formatting markers around selected text or at cursor"""
        tab = self.get_tab()
        editor = tab.value
        if not editor:
            return

        buff = editor.get_buffer()

        # Check if text is selected
        if buff.get_has_selection():
            # Get selection bounds
            start_iter, end_iter = buff.get_selection_bounds()

            # Get selected text
            selected_text = buff.get_text(start_iter, end_iter, False)

            # Begin user action for undo grouping
            buff.begin_user_action()

            # Delete selection
            buff.delete(start_iter, end_iter)

            # Insert formatted text
            insert_mark = buff.get_insert()
            insert_iter = buff.get_iter_at_mark(insert_mark)
            buff.insert(insert_iter, f"{prefix}{selected_text}{suffix}")

            buff.end_user_action()
        else:
            # No selection - insert markers and position cursor between them
            buff.begin_user_action()

            insert_mark = buff.get_insert()
            insert_iter = buff.get_iter_at_mark(insert_mark)

            # Insert prefix + suffix
            buff.insert(insert_iter, prefix + suffix)

            # Move cursor between markers
            insert_iter = buff.get_iter_at_mark(insert_mark)
            insert_iter.backward_chars(len(suffix))
            buff.place_cursor(insert_iter)

            buff.end_user_action()

    def on_quick_help(self, action, param):
        from .helper import CONFIG_PATH

        config_path = CONFIG_PATH
        manual_url = "https://github.com/jdalbey/jellypie-todo/blob/main/USERMANUAL.md"

        dialog = gtk.Window()
        dialog.set_name("window")
        dialog.get_style_context().add_class("csd")
        dialog.set_transient_for(self.app.get_active_window())
        dialog.set_modal(True)
        dialog.set_resizable(False)
        dialog.set_hide_on_close(True)
        dialog.set_decorated(False)
        dialog.set_default_size(500, -1)

        title_label = gtk.Label(label="Quick Help")
        title_label.set_css_classes(["title-3"])
        title_label.set_justify(gtk.Justification.CENTER)

        info_box = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=12)
        info_box.set_halign(gtk.Align.START)

        # Current font
        font_label = gtk.Label(label="Current Font:")
        font_label.set_halign(gtk.Align.START)
        font_label.get_style_context().add_class("heading")

        # Get current font settings
        font_family = config.get_config("font_family") or "Noto Sans Mono"
        font_size = config.get_config("font_size") or 10
        font_weight = config.get_config("font_weight") or 400

        # Map weight to style word for display
        weight_names = {
            100: "Thin",
            200: "Extra Light",
            300: "Light",
            400: "Regular",
            500: "Medium",
            600: "Semi Bold",
            700: "Bold",
            800: "Extra Bold",
            900: "Black",
        }
        weight_name = weight_names.get(font_weight, str(font_weight))

        font_info = f"{font_family} {weight_name} {font_size}"
        font_info_label = gtk.Label(label=font_info)
        font_info_label.set_halign(gtk.Align.START)
        font_info_label.set_selectable(True)
        font_info_label.set_can_focus(False)

        # Config file path
        config_label = gtk.Label(label="Config File:")
        config_label.set_halign(gtk.Align.START)
        config_label.get_style_context().add_class("heading")

        config_path_label = gtk.Label(label=config_path)
        config_path_label.set_halign(gtk.Align.START)
        config_path_label.set_selectable(True)
        config_path_label.set_can_focus(False)
        config_path_label.set_wrap(True)
        config_path_label.set_max_width_chars(60)
        config_path_label.get_style_context().add_class("monospace")

        # User manual URL
        manual_label = gtk.Label(label="User Manual:")
        manual_label.set_halign(gtk.Align.START)
        manual_label.get_style_context().add_class("heading")

        manual_url_label = gtk.Label(label=manual_url)
        manual_url_label.set_halign(gtk.Align.START)
        manual_url_label.set_selectable(True)
        manual_url_label.set_can_focus(False)
        manual_url_label.set_wrap(True)
        manual_url_label.set_max_width_chars(60)
        manual_url_label.get_style_context().add_class("monospace")

        info_box.append(font_label)
        info_box.append(font_info_label)
        info_box.append(config_label)
        info_box.append(config_path_label)
        info_box.append(manual_label)
        info_box.append(manual_url_label)

        btn_close = gtk.Button(label="Close")
        btn_close.add_css_class("btn")
        btn_close.get_style_context().add_class("suggested-action")
        btn_close.connect("clicked", lambda btn: dialog.close())

        main_box = gtk.Box(
            orientation=gtk.Orientation.VERTICAL, spacing=18,
            margin_top=20, margin_bottom=20,
            margin_start=20, margin_end=20)

        main_box.append(title_label)
        main_box.append(info_box)
        main_box.append(btn_close)

        dialog.set_child(main_box)
        dialog.present()

        # Set focus to Close button to prevent selection highlight on font label
        btn_close.grab_focus()

    def on_keyboard_shortcut(self, action, param):
        builder = gtk.Builder.new_from_string(SC_XML, -1)
        shortcuts_window = builder.get_object("shortcuts-windows")
        shortcuts_window.set_transient_for(self.window)
        shortcuts_window.present()

    def on_support(self, action, param):
        import webbrowser
        webbrowser.open("https://ko-fi.com/zulfian1732")

    def on_about(self, action, param):
        dialog = gtk.AboutDialog()
        dialog.set_transient_for(self.app.get_active_window())
        dialog.set_modal(True)

        dialog.set_program_name("Jollpi")
        dialog.set_version(get_app_version())
        dialog.set_comments(
            "A lightweight, simple, and reliable text editor\n"
            "Built with Python 3, GTK4, and GtkSourceView 5")
        dialog.set_website("https://github.com/jdalbey/jellypie-todo/")
        dialog.set_website_label("Manual")
        #dialog.set_copyright("© 2010-2025 Zulfian")
        dialog.set_license(LICENSE)

        dialog.set_authors([
            "Zulfian <zulfian1732@gmail.com>",
        ])
        dialog.set_documenters([
            "Zulfian",
        ])
        dialog.set_artists([
            "KWD",
        ])

        icon_theme = gtk.IconTheme.get_for_display(gdk.Display.get_default())
        icon_source = get_icon_dir()
        icon_theme.add_search_path(icon_source)
        app_id = self.app.get_application_id()

        if icon_theme.has_icon(app_id):
            paintable = icon_theme.lookup_icon(
                app_id,
                None,
                256,
                1,
                gtk.TextDirection.NONE,
                gtk.IconLookupFlags.PRELOAD
            )
            if paintable:
                dialog.set_logo(paintable)

        dialog.present()
