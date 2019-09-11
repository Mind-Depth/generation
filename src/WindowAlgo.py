#

import PyQtToolBox
from PyQt5 import QtCore
import PyQt5.QtWidgets as QtW
from collections import Counter, defaultdict

class Asset:
    '''Informations about a given asset in a given map'''

    def __init__(self):
        self.progress_bar = PyQtToolBox.ProgressBar()
        self.label = QtW.QLabel()
        self.count = PyQtToolBox.IntegerSelector(mini=0)
        self.progress = PyQtToolBox.FlagedObject(self.progress_bar, self.label)

    def bind(self, asset, cat):
        self.asset = asset
        self.cat = cat
        self.label.setText(self.asset.description)
        self.count.maxi = self.cat.cat.use_max
        self.count.callback = self.cat.set_count

@PyQtToolBox.ui_factory(Asset, 30)
class Category(PyQtToolBox.GridLayout):
    '''Possible content for a given object type (minimum amount, maximum, etc.)'''

    def __init__(self):
        super().__init__(stretches=[1, 6, 1, 1, 1], alignments=[
            QtCore.Qt.AlignCenter, None,
            QtCore.Qt.AlignRight, QtCore.Qt.AlignCenter, QtCore.Qt.AlignLeft
        ])
        self.title = PyQtToolBox.Title()
        self.label = QtW.QLabel()
        self.count = PyQtToolBox.FlagedValue(0, self.label)
        self.label_min = QtW.QLabel()
        self.label_max = QtW.QLabel()
        self.add_row(self.title, None, self.label_min, self.count.text, self.label_max)

    def bind(self, cat):
        self.cat = cat

        # Colored amount
        self.count.trigger = PyQtToolBox.FlagedValue.Outside(self.cat.use_min, self.cat.use_max)

        # Amount labels
        self.title.setText(self.cat.name)
        self.label_min.setText(f'{self.cat.use_min} <=')
        self.label_max.setText(f'>= {self.cat.use_max}')

        # Assets
        self.assets = []
        for asset in self.cat.assets:
            asset_obj = self.instanciate(Asset)
            asset_obj.bind(asset, self)
            # Amount buttons
            self.add_row(
                asset_obj.progress.text, asset_obj.progress.obj,
                asset_obj.count.less, asset_obj.count.label, asset_obj.count.more
            )
            self.assets.append(asset_obj)
        self.set_count()

    def set_count(self):
        self.count.set(sum(asset.count.value for asset in self.assets))

@PyQtToolBox.ui_factory(Category, 10)
class Room:
    '''Content of a specific room instance'''

    def __init__(self):
        self.progress_bar = PyQtToolBox.ProgressBar()
        self.scrollable = PyQtToolBox.ScrollableArea()
        self.button = QtW.QRadioButton()
        self.progress = PyQtToolBox.FlagedObject(self.progress_bar, self.button)

    def bind(self, m, map_callback):
        self.map = m
        self.map_callback = map_callback
        self.button.toggled.connect(self.map_selected)

        # Categories
        self.cats = []
        for cat in self.map.categories_config:
            category = self.instanciate(Category)
            category.bind(cat)
            self.scrollable.layout.addLayout(category)
            self.cats.append(category)
        self.show(False)

    def show(self, b):
        self.scrollable.setHidden(not b)

    def map_selected(self):
        self.map_callback(self)

class WindowAlgo(PyQtToolBox.Window):
    '''
        Contains informations about the probability of choosing any map or asset.
        Also allows to take control over the decision making process
    '''

    WIDTH = 1200
    HEIGHT = 800

    FEAR_BGCOLOR = '#192025'
    ROOM_BGCOLOR = '#1e252e'

    _NB_FEARS=20
    @PyQtToolBox.ui_factory(QtW.QLabel, _NB_FEARS)
    @PyQtToolBox.ui_factory(PyQtToolBox.Slider, _NB_FEARS)
    class LayoutFear(PyQtToolBox.LoadableControlLayout):
        '''Part of the UI related to the fear levels'''

        def __init__(self, root):
            super().__init__('Fears')
            self.root = root
            self.scroll = PyQtToolBox.ScrollableArea(QtW.QFormLayout)
            self.addWidget(self.scroll)
            self.sliders = {}
            self._force_ui_on_manual = self.root.gen.ui_force_fears

            # TODO
            self.events = PyQtToolBox.ScrollableArea(QtW.QVBoxLayout)
            self.addWidget(self.events)

        def _slider_changed(self, key):
            if self.is_auto():
                return
            # Force the algorithms decisions
            value = self.sliders[key].get()
            self.root.gen.ui_set_fear(key, value)
            self.root.reloadGeneration.emit()

        def _reload(self):
            '''Callback for the parent'''
            if not self.is_auto():
                return
            # Fetch the algorithms decisions
            for key, value in self.root.gen.ui_get_fears().items():
                self.sliders[key].set(value)

        def _create(self):
            '''Callback for the parent: adds the sliders to the UI'''
            for key in self.root.gen.ui_get_fears():
                slider = self.instanciate(PyQtToolBox.Slider)
                slider.set_callback(self._slider_changed, key)
                self.sliders[key] = slider
                label = self.instanciate(QtW.QLabel)
                label.setText(key)
                self.scroll.layout.addRow(label, slider)
            self._enable_on_manual.extend(self.sliders.values())
            
            # TODO
            import random
            for event in self.root.gen.ui_get_events():
                layout = QtW.QVBoxLayout()
                layout.addWidget(QtW.QLabel(f'{event.description} [{event.min} - {event.max}]'))
                button = QtW.QPushButton('Trigger')
                layout.addWidget(button)
                self.events.layout.addLayout(layout)
                def callback(*args, event=event):
                    self.root.gen.ui_send_event(event, random.randint(event.min, event.max))
                button.clicked.connect(callback)

    @PyQtToolBox.ui_factory(Room, 30)
    class LayoutRoom(PyQtToolBox.LoadableControlLayout):
        '''Part of the UI related to rooms'''

        def __init__(self, root):
            super().__init__('Rooms')
            self.root = root

            # Main control
            self.layout_buttons = QtW.QHBoxLayout()
            self.refresh_rooms = QtW.QPushButton('Refresh')
            self.refresh_rooms.clicked.connect(self._refresh)
            self.layout_buttons.addWidget(self.refresh_rooms)
            self.requests = PyQtToolBox.Title()
            self.layout_buttons.addWidget(self.requests)
            self.send_room = QtW.QPushButton('Send Room')
            self.send_room.clicked.connect(self._send_room)
            self.send_room.setEnabled(self.is_auto())
            self.layout_buttons.addWidget(self.send_room)
            self.addLayout(self.layout_buttons)

            # Mode selection
            self._enable_on_manual.append(self.send_room)
            self._enable_on_auto.append(self.refresh_rooms)

            # Reserved space for the above classes
            self.layout_rooms = QtW.QHBoxLayout()
            self.scroll_maps = PyQtToolBox.ScrollableArea(QtW.QFormLayout)
            self.layout_rooms.addWidget(self.scroll_maps, 1)
            self.layout_assets = QtW.QHBoxLayout()
            self.layout_rooms.addLayout(self.layout_assets, 2)
            self.addLayout(self.layout_rooms)

            self.rooms = []
            self.room_ids = {}
            self.radio_maps = PyQtToolBox.RadioGroup()

            self._force_ui_on_manual = self.root.gen.ui_force_rooms

        def room_preprocess(self):
            for room in self.factory[Room]:
                widget = room.scrollable
                self.layout_assets.addWidget(widget)
                widget.setHidden(True)

        def _send_room(self):
            if not self.rooms:
                return
            # Force the algorithms decisions
            room = self._current_room()
            chosen_map = room.map
            chosen_assets = []
            for cat in room.cats:
                for asset in cat.assets:
                    chosen_assets.extend([asset.asset]*asset.count.value)
            self.root.gen.ui_send_room(chosen_assets, chosen_map)

        def _current_room(self):
            return self.room_ids[self.radio_maps.checkedId()]

        def _map_selected(self, room):
            visible = room == self._current_room()
            room.show(visible)
            if visible:
                self._set_assets()

        def _reload(self):
            '''Callback for the parent'''
            if not self.rooms:
                return
            # Fetch the algorithms decisions
            probas, index = self.root.gen.ui_get_map()
            for proba, room in zip(probas, self.rooms):
                room.progress.set(proba)
            if self.is_auto():
                room = self.rooms[index]
                if room != self._current_room():
                    return room.button.setChecked(True)
            self._set_assets()

        def _set_assets(self):
            auto = self.is_auto()
            room = self._current_room()
            assets = self.root.gen.ui_get_assets(room.map)
            for (probas, indices), cat in zip(assets, room.cats):
                for proba, asset in zip(probas, cat.assets):
                    asset.progress.set(proba)
                if not auto:
                    continue
                count = defaultdict(int, Counter(indices))
                for index, asset in enumerate(cat.assets):
                    asset.count.set(count[index])
                cat.set_count()

        def _create(self):
            '''Callback for the parent: instantiate all the Rooms and Assets'''
            for i, m in enumerate(self.root.gen.maps):
                room = self.instanciate(Room)
                self.radio_maps.add_button(room.button, m.description, m.id, not i)
                room.bind(m, self._map_selected)
                self.rooms.append(room)
                self.room_ids[room.map.id] = room
                self.scroll_maps.layout.addRow(room.progress.text, room.progress.obj)
            self.radio_maps.buttons[0].setChecked(True)
            self._enable_on_manual.extend(self.radio_maps.buttons)
            self.rooms[0].show(True)
            self.set_room_request()
            self._enable_on_manual.extend([
                asset.count
                for room in self.rooms
                for cat in room.cats
                for asset in cat.assets
            ])

        def set_room_request(self):
            # Show the pending requests
            count = self.root.gen.room_requests
            self.requests.setText(f'{count} room{"s" * (count > 1)} requested')

    def __init__(self, root):
        super().__init__('Algorithm State', QtW.QHBoxLayout(), wmin=self.WIDTH, hmin=self.HEIGHT)
        self.root = root
        self.layout_fear = self.LayoutFear(self.root)
        self.layout_rooms = self.LayoutRoom(self.root)
        self.layout_rooms.room_preprocess()
        self.layout.addWidget(PyQtToolBox.Colored(self.layout_fear, background=self.FEAR_BGCOLOR), 1)
        self.layout.addWidget(PyQtToolBox.Colored(self.layout_rooms, background=self.ROOM_BGCOLOR), 4)

    # Signal callbacks

    def load_env_config(self):
        self.layout_fear._load()
        self.layout_rooms._load()

    def reload_generation(self):
        self.layout_fear._reload()
        self.layout_rooms._reload()

    def request_room(self):
        self.layout_rooms.set_room_request()
