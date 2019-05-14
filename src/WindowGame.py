#

import time
import datetime
import PyQtToolBox
import pyqtgraph as pg
from PyQt5 import QtCore
import PyQt5.QtWidgets as QtW

class RelativeTimeAxis(pg.AxisItem):
    '''Custom ticks to make timestamps readable'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t0 = time.time()

    def tickStrings(self, values, *args):
        return [int(value - self.t0) for value in values]

@PyQtToolBox.ui_factory(PyQtToolBox.Title, 20)
class AssetPreview(QtW.QHBoxLayout):
    '''Informations of an asset'''

    def __init__(self):
        super().__init__()

        # Description
        self.title = PyQtToolBox.Title()
        self.label = PyQtToolBox.Title(bold=False)
        self.addWidget(self.title, 1)
        self.addWidget(self.label, 1)

        self.fears = PyQtToolBox.ScrollableArea()
        self.addWidget(self.fears, 1)

    def title_preprocess(self):
        for title in self.factory[PyQtToolBox.Title]:
            title.font.setBold(False)
            title.setHidden(True)
            self.fears.layout.addWidget(title)

    def bind(self, asset, enums):
        self.asset = asset
        self.title.setText(self.asset.description)
        self.label.setText(enums.ObjectType[self.asset.object_type])

        #Tags
        for fear in self.asset.fears:
            title = self.instanciate(PyQtToolBox.Title)
            title.setText(enums.Fears[fear])
            title.setHidden(False)

@PyQtToolBox.ui_factory(AssetPreview, 30)
class RoomPreview(PyQtToolBox.ScrollableArea):
    '''Content of a room'''

    RECTANGLES_CONFIG = [
        (pg.mkPen(None), pg.mkBrush('#501510')),
        (pg.mkPen(None), pg.mkBrush('#105010'))
    ]

    def create_rectangle(self, toggled, *args, **kwargs):
        '''Creates a drawable rectangle whose color is based on the room activity'''
        rect = pg.QtGui.QGraphicsRectItem(*args, **kwargs)
        pen, brush = self.RECTANGLES_CONFIG[bool(toggled)]
        rect.setPen(pen)
        rect.setBrush(brush)
        return rect

    def __init__(self):
        super().__init__()

        # Description
        self.layout_title = QtW.QHBoxLayout()
        self.title = PyQtToolBox.Title()
        self.layout_title.addWidget(self.title)

        # Timestamps
        self.label_start = PyQtToolBox.Title(bold=False)
        self.label_stop = PyQtToolBox.Title(bold=False)
        self.layout_title.addWidget(self.label_start)
        self.layout_title.addWidget(self.label_stop)
        self.layout.addLayout(self.layout_title)

        self.items = []
        self.items_showed = []

    def bind(self, room, enums, button):
        self.room = room
        self.button = button
        self.title.setText(f'{self.room.map.description} (ID: {self.room.map.id})')

        # Assets
        for asset in self.room.assets:
            preview = self.instanciate(AssetPreview)
            preview.bind(asset, enums)
            self.layout.addLayout(preview)
        self.update_time()

    def update_time(self):
        '''Updates the timestamp related UI elements'''
        def fmt(t):
            if t is None:
                return 'TBD'
            return datetime.datetime.fromtimestamp(t).strftime("%d/%m/%Y, %H:%M:%S") + f' ({t})'
        # Labels
        self.label_start.setText(f'Creation time: {fmt(self.room.created)}')
        self.label_stop.setText(f'Deletion time: {fmt(self.room.deleted)}')
        # Colored rectangles
        times = self.room.active_times
        chunks = list(zip(times[:], times[1:]))
        for i in range(len(self.items), len(chunks)):
            mini, maxi = chunks[i]
            self.items.append(self.create_rectangle(i % 2, mini, 0, maxi - mini, 1))

    def show(self, toggled, view_box):
        '''Removes/Adds rectangles from/to the graph'''
        if toggled:
            self.items_showed = list(self.items)
            if not self.room.deleted:
                rect = self.create_rectangle(self.room.entered, self.room.active_times[-1], 0.25, 0.5, 0.5)
                self.items_showed.append(rect)
        callback = view_box.addItem if toggled else view_box.removeItem
        for time_range in self.items_showed:
            callback(time_range)

class WindowGame(PyQtToolBox.Window):
    '''Displays informations about the current and past biofeedbacks and rooms'''

    WIDTH = 1200
    HEIGHT = 800

    class LayoutBiofeedback(QtW.QHBoxLayout):
        '''Part of the UI related to biofeedbacks'''

        def __init__(self, root, view_box):
            super().__init__()
            self.root = root

            # Points colors
            colors = [(0, 255, 0), (255, 255, 0), (255, 0, 0)]
            nb_colors = len(colors)
            pos = [i/(nb_colors-1) for i in range(nb_colors)]
            self.colormap = pg.ColorMap(pos, colors)

            # Biofeedbacks
            graph_plot = pg.GraphicsLayoutWidget()
            self.plot = graph_plot.addPlot(axisItems={'bottom': RelativeTimeAxis(orientation='bottom')})
            self.plot.hideAxis('left')
            self.addWidget(graph_plot, 3)

            # Room activity
            self.view_box = view_box
            self.view_box.setXLink(self.plot)

            # Plots limits
            self.plot_y_delta = 0.05
            self.plot_x_minrange = 30
            self.plot_x_maxrange = 100
            self.plot_x = []
            self.plot_y = []
            yrange = 1 + 2 * self.plot_y_delta
            self.plot.setMouseEnabled(y=False)
            self._set_limits(
                yMin=-self.plot_y_delta, yMax=1+self.plot_y_delta, minYRange=yrange, maxYRange=yrange,
                xMin=0, xMax=self.plot_x_minrange, minXRange=self.plot_x_minrange, maxXRange=self.plot_x_maxrange,
            )

            # Additional labels
            self.layout_text = QtW.QVBoxLayout()
            self.layout_text.addWidget(PyQtToolBox.Title('Biofeedback', size=12))
            self.label = PyQtToolBox.Title()
            self.layout_text.addWidget(self.label)
            self.focus = QtW.QCheckBox('Focus graphs on new elements')
            self.focus.setChecked(True)
            self.layout_text.addWidget(self.focus, alignment=QtCore.Qt.AlignCenter)
            self.addLayout(self.layout_text, 1)

        def _set_limits(self, *args, **kwargs):
            '''Synchronizes the biofeedback and room graphs'''
            self.plot.setLimits(*args, **kwargs)
            self.view_box.setLimits(*args, **kwargs)

        def refresh(self):
            '''Adds biofeedbacks to the graph'''

            # Fetch new data
            data = self.root.gen.feedback_history[len(self.plot_x):]
            if not data:
                return
            xs, ys = zip(*data)

            # Sanity check
            assert list(xs) == sorted(xs)
            assert not self.plot_x or self.plot_x[-1] <= xs[0]

            # Limit update
            self.plot_x.extend(xs)
            self.plot_y.extend(ys)

            xmin = self.plot_x[0]
            xmax = xs[-1]
            miss = xmin + self.plot_x_minrange - xmax
            if miss > 0:
                xmax += miss
            self._set_limits(xMin=xmin, xMax=xmax)

            # Drawing
            self.plot.clear()
            brushes = [pg.mkBrush(c) for c in self.colormap.map(self.plot_y)]
            self.plot.plot(self.plot_x, self.plot_y, symbolBrush=brushes)

            # Auto-focus
            (xrmin, xrmax), _ = self.plot.viewRange()
            if self.focus.isChecked() and xrmax < xmax:
                self.plot.setXRange(xrmin + xmax - xrmax, xmax)

            # Labels update
            value = ys[-1]
            self.label.setText(f'Current : {value:.3f}')
            color = ''.join(f'{c:02x}' for c in self.colormap.map(value))
            self.label.setStyleSheet('background-color:#000000;color:#' + color)

    _NB_ROOMS=30
    @PyQtToolBox.ui_factory(RoomPreview, _NB_ROOMS)
    @PyQtToolBox.ui_factory(QtW.QRadioButton, _NB_ROOMS)
    class LayoutEnvironment(QtW.QVBoxLayout):
        '''Part of the UI related to rooms'''

        def __init__(self, root):
            super().__init__()
            self.root = root

            # Graph
            self.layout_time = QtW.QHBoxLayout()
            graph_view_box = pg.GraphicsLayoutWidget()
            self.view_box = graph_view_box.addViewBox()
            self.view_box.setMouseEnabled(y=False)
            self.layout_time.addWidget(graph_view_box, 3)
            self.layout_time.addWidget(PyQtToolBox.Title('Room activity', size=12), 1)
            self.addLayout(self.layout_time, 1)

            self.layout_rooms = QtW.QHBoxLayout()
            self.addLayout(self.layout_rooms, 9)

            # Deleted rooms
            self.layout_old = QtW.QVBoxLayout()
            self.layout_old.addWidget(PyQtToolBox.Title('Past rooms'))
            self.scroll_old = PyQtToolBox.ScrollableArea()
            self.layout_old.addWidget(self.scroll_old)
            self.layout_rooms.addLayout(self.layout_old, 1)

            # Current room
            self.layout_current = QtW.QVBoxLayout()
            self.previews = {}
            self.buffered_rooms = set()
            self.selected_room = None
            self.current_room = None
            self.radio_group = PyQtToolBox.RadioGroup()
            self.layout_current_container = QtW.QHBoxLayout()
            self.layout_current_container.addWidget(PyQtToolBox.Title('Current room'))
            self.layout_current.addLayout(self.layout_current_container)
            self.layout_current.addWidget(PyQtToolBox.Title('Room preview'))
            self.layout_rooms.addLayout(self.layout_current, 5)

            # Possible rooms
            self.layout_new = QtW.QVBoxLayout()
            self.layout_new.addWidget(PyQtToolBox.Title('Next rooms'))
            self.scroll_new = PyQtToolBox.ScrollableArea()
            self.layout_new.addWidget(self.scroll_new)
            self.layout_rooms.addLayout(self.layout_new, 1)

        def preview_preprocess(self):
            for room_preview in self.factory[RoomPreview]:
                self.layout_current.addWidget(room_preview)
                room_preview.setHidden(True)
                for asset_preview in room_preview.factory[AssetPreview]:
                    asset_preview.title_preprocess()

        def refresh(self):
            '''Synchronizes with the algorithms'''

            focus_current_room = self.selected_room == self.current_room

            # Fetch from the algorithmes
            rooms = list(self.root.gen.rooms.items())
            for room_id, room in rooms:

                # Instantiate a new room preview
                if room_id not in self.previews:
                    preview = self.instanciate(RoomPreview)
                    button = self.instanciate(QtW.QRadioButton)
                    self.radio_group.add_button(button, room_id)
                    preview.bind(room, self.root.gen.reverse_enums, button)
                    def show(toggled, room_id=room_id, preview=preview):
                        if toggled:
                            self.selected_room = room_id
                        preview.setHidden(not toggled)
                        preview.show(toggled, self.view_box)
                    button.toggled.connect(show)
                    self.previews[room_id] = preview
                    if not room.deleted:
                        self.buffered_rooms.add(room_id)

                # Delete from possible rooms
                elif room_id in self.buffered_rooms:
                    if room.deleted:
                        self.buffered_rooms.remove(room_id)
                    self.previews[room_id].update_time()

                # Place button on the right panel
                button = self.previews[room_id].button
                self.scroll_old.layout.removeWidget(button)
                self.layout_current_container.removeWidget(button)
                self.scroll_new.layout.removeWidget(button)
                if room.deleted:
                    self.scroll_old.layout.addWidget(button)
                elif room.entered:
                    self.current_room = room_id
                    self.layout_current_container.addWidget(button)
                else:
                    self.scroll_new.layout.addWidget(button)

            # Focus on the right room
            focus = self.current_room if focus_current_room else self.selected_room
            if focus is not None:
                room = self.previews[focus]
                if focus == self.selected_room:
                    room.show(False, self.view_box)
                    room.show(True, self.view_box)
                else:
                    room.button.setChecked(True)

    def __init__(self, root):
        super().__init__('Game State', QtW.QVBoxLayout(), wmin=self.WIDTH, hmin=self.HEIGHT)
        self.root = root

        # Instantiate UI parts
        self.environment = self.LayoutEnvironment(self.root)
        self.environment.preview_preprocess()
        self.biofeedback = self.LayoutBiofeedback(self.root, self.environment.view_box)
        self.layout.addLayout(self.biofeedback, 1)
        self.layout.addLayout(self.environment, 4)

    # Signal callbacks

    def refresh_game(self):
        self.environment.refresh()

    def refresh_graph(self):
        self.biofeedback.refresh()
