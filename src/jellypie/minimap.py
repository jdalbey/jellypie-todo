from .helper import gtk, gdk, gtksource, Graphene


class EditorSourceMap(gtk.Widget):
    def __init__(self):
        super().__init__()
        self.map = gtksource.Map()
        self.map.set_name("map")
        self.set_layout_manager(gtk.BinLayout())
        self.map.set_parent(self)

        self.vadj = None
        self.slider = None
        self.is_pressed = False

    def set_view(self, view):
        self.map.set_view(view)

        for child in self.map.observe_children():
            css = child.get_css_name()
            if css in ("slider", "map-slider"):
                self.slider = child
                break
        if view:
            self.vadj = view.get_vadjustment()
            if self.vadj:
                self.vadj.connect("value-changed", lambda _: self.queue_draw())
                self.vadj.connect("changed", lambda _: self.queue_draw())

        self.queue_draw()

    def do_snapshot(self, snapshot):
        w = self.get_width()
        h = self.get_height()

        gtk.Widget.snapshot_child(self, self.map, snapshot)

        if not self.slider:
            return

        alloc = self.slider.get_allocation()

        map_height = self.map.get_height()
        if map_height == 0:
            return

        scaled_y = (alloc.y / map_height) * h
        scaled_height = (alloc.height / map_height) * h

        color = gdk.RGBA()
        color.parse("#57595B")
        color.alpha = 0.35
        rect = Graphene.Rect().init(0, scaled_y, w, scaled_height)
        snapshot.append_color(color, rect)

    def do_measure(self, orientation, for_size):
        return self.map.measure(orientation, for_size)

    def do_size_allocate(self, width, height, baseline):
        alloc = gdk.Rectangle()
        alloc.width = width
        alloc.height = height
        self.map.size_allocate(alloc, baseline)

    def do_unparent(self):
        self.map.unparent()
        super().do_unparent()
