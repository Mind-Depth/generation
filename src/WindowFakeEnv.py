#

import time
import random
import PyQtToolBox
from PyQt5 import QtCore
from attrdict import AttrDict
import PyQt5.QtWidgets as QtW
from Connection import ConnectionMock
from Configuration import Configuration

class FakeEnums:

    def _make_attr_dict(*values):
        return AttrDict({key: value for value, key in enumerate(values)})

    Fears = _make_attr_dict('Arachnophobia', 'Acrophobia', 'Nyctophobia', 'Claustrophobia')
    QueueTypeWatcher = _make_attr_dict('Ping', 'Data')
    QueueTypeGeneration = _make_attr_dict('Ping', 'Assets', 'Event')
    ObjectType = _make_attr_dict('Ground', 'Wall', 'Light', 'SpiderSpawner')
    WatcherDataType = _make_attr_dict(
        'Empty', 'RequestRoom', 'ChangedRoom', 'DeletedRoom',
        'ActivePlayer', 'PassivePlayer', 'ActivePlayerInteraction', 'PassivePlayerInteraction',
        'TriggerableEvent'
    )

    def _make_kv_pairs(enum):
        return [{'key': key, 'value': value} for key, value in enum.items()]

    DUMPABLE = {
        'Fears': _make_kv_pairs(Fears),
        'QueueTypeWatcher': _make_kv_pairs(QueueTypeWatcher),
        'QueueTypeGeneration': _make_kv_pairs(QueueTypeGeneration),
        'ObjectType': _make_kv_pairs(ObjectType),
        'WatcherDataType': _make_kv_pairs(WatcherDataType),
    }

    @classmethod
    def get_shuffled_fears(cls, mini=None, maxi=None):
        f = list(cls.Fears.items())
        random.shuffle(f)
        if mini is None:
            mini = len(f)
        if maxi is None:
            maxi = mini
        f = f[:random.randint(mini, maxi)]
        return zip(*f)

class EnvConnectionMock(ConnectionMock):
    '''Formats and sends messages in the same way the real environment would'''

    def __init__(self, group):
        super().__init__(Configuration.connection.environment, group)

    def queue_message(self, queueType=0, watcherType=0, fears=[], message=''):
        super().queue_message({
            'time': int(time.time()),
            'queueType': queueType,
            'watcherType': watcherType,
            'fears': fears,
            'message': message,
        })

    def ping(self, msg='OK'):
        self.queue_message(message=msg)

    def queue_data(self, type_name, **kw):
        '''Mocks a message created by a given watcher type'''
        watcher = FakeEnums.WatcherDataType[type_name]
        self.queue_message(queueType=FakeEnums.QueueTypeWatcher.Data, watcherType=watcher, **kw)

    def _sender(name, arg_name=None):
        '''Simplifies watchers mocking right below the function'''
        if arg_name is None:
            return lambda self: self.queue_data(name)
        return lambda self, arg: self.queue_data(name, **{arg_name: arg})

    request_room = _sender('RequestRoom')
    active_player = _sender('ActivePlayer')
    passive_player = _sender('PassivePlayer')
    changed_room = _sender('ChangedRoom', 'message')
    deleted_room = _sender('DeletedRoom', 'message')
    active_player_interaction = _sender('ActivePlayerInteraction', 'fears')
    passive_player_interaction = _sender('PassivePlayerInteraction', 'fears')

class WindowFakeEnv(PyQtToolBox.Window):
    '''UI to emulate the sending of messages from the environement's watchers'''

    WIDTH = 500
    HEIGHT = 500

    def __init__(self, root, name):
        self.root = root
        self.name = name
        super().__init__(f'Fake {self.name}', QtW.QVBoxLayout(), wmin=self.WIDTH, hmin=self.HEIGHT)

        # Link to Generation's communication queues
        self.mock = EnvConnectionMock(self.root.gen)
        self.rooms = set()

        # Warning message
        self.title_layout = QtW.QVBoxLayout()
        self.title_layout.setAlignment(QtCore.Qt.AlignVCenter)
        self.title_layout.addWidget(PyQtToolBox.Title('WARNING: Used for debuging'))
        self.title_layout.addWidget(PyQtToolBox.Title('Invalid / Incoherent messages can be send with this UI'))
        self.layout.addLayout(self.title_layout, 1)

        def button_factory(layout, wrapper=lambda f: f):
            '''Simplifies the creation of button and callback right below'''
            def f(name, callback, *args):
                button = QtW.QPushButton(name)
                button.clicked.connect(wrapper(callback))
                layout.addWidget(button, *args)
            return f

        # Room-Related watchers
        self.room_layout = QtW.QGridLayout()
        self.room_layout.setAlignment(QtCore.Qt.AlignVCenter)
        with_room = button_factory(self.room_layout, self._callback_with_room)
        button = QtW.QPushButton('Request Room')
        button.clicked.connect(self.mock.request_room)
        self.room_layout.addWidget(button, 0, 0, 1, 2)
        self.room_layout.addWidget(QtW.QLabel('Rooms'), 1, 0)
        self.room_picker = PyQtToolBox.ComboBox()
        self.room_layout.addWidget(self.room_picker, 1, 1)
        with_room('Changed Room', self.mock.changed_room, 2, 0)
        with_room('Deleted Room', self.mock.deleted_room, 2, 1)
        self.layout.addLayout(self.room_layout, 1)

        # Fear-Related watchers
        self.fears = {}
        self.action_layout = QtW.QGridLayout()
        self.action_layout.setAlignment(QtCore.Qt.AlignVCenter)
        with_fears = button_factory(self.action_layout, self._callback_with_fears)
        normal = button_factory(self.action_layout)
        scrollable = PyQtToolBox.ScrollableArea()
        for fear, fear_id in FakeEnums.Fears.items():
            check = QtW.QCheckBox(fear)
            scrollable.layout.addWidget(check)
            self.fears[fear_id] = check
        self.action_layout.addWidget(scrollable, 0, 0, 1, 2, QtCore.Qt.AlignVCenter)
        with_fears('Active Interaction', self.mock.active_player_interaction, 1, 0)
        with_fears('Passive Interaction', self.mock.passive_player_interaction, 1, 1)
        normal('Active Player', self.mock.active_player, 2, 0)
        normal('Passive Player', self.mock.passive_player, 2, 1)
        self.layout.addLayout(self.action_layout, 2)

    # Callback wrappers adding UI selected informations into watchers messages

    def _callback_with_room(self, callback):
        def f(*args):
            return callback(self.room_picker.text())
        return f

    def _callback_with_fears(self, callback):
        def f(*args):
            return callback([fear_id for fear_id, check in self.fears.items() if check.isChecked()])
        return f

    def _dump_config(self):
        '''Dumps fake assets and enums'''

        def random_objects(path, name, obj_count, fear_count):
            '''
                Yields a random amount of assets, linked to a random amount of phobias. (One exception nonetheless:
                The first asset contains every phobias to ensure they are used at least once)
            '''
            for i in range(random.randint(*obj_count)):
                names, values = FakeEnums.get_shuffled_fears(*fear_count*bool(i))
                obj_id = f'{i:03d}'
                desc = ' '.join([f'{name}:'] + list(names))
                obj = AttrDict({'id': obj_id, 'description': desc, 'fears': values})
                yield obj
                Configuration.dump(obj, path, f'{obj.id}.json')

        # Enums
        Configuration.dump(FakeEnums.DUMPABLE, Configuration.generated.enums)

        # Models
        for obj_name, obj_type in FakeEnums.ObjectType.items():
            for obj in random_objects(Configuration.generated.models, obj_name, (5, 10), (1, 2)):
                obj.id += f'{obj_type:03d}'
                obj.object_type = obj_type

        # Maps
        for obj in random_objects(Configuration.generated.maps, 'map', (5, 10), (1, 4)):
            obj.banned_ids = []
            obj.categories_config = [
                {'type': obj_type, 'use_min': random.randint(0, 2), 'use_max': random.randint(3, 4)}
                for obj_type in FakeEnums.ObjectType.values()
            ]

        # Events
        for obj in random_objects(Configuration.generated.events, 'event', (5, 10), (1, 2)):
			# TODO more random configuration
            obj.id_assets_needed = []
            obj.id_maps_needed = []
            obj.min = random.randint(0, 40)
            obj.max = random.randint(60, 100)
            obj.wait_for_trigger = False
            obj.cooldown = 0
            obj.maximum_use = 0

    def start(self):
        '''Emulates a handshake'''
        self.mock.connect()
        self._dump_config()
        self.mock.ping()

    # Signal callbacks

    def refresh_game(self):
        rooms = [room_id for room_id, room in self.root.gen.rooms.items() if room.deleted is None]
        set_rooms = set(rooms)
        if self.rooms != set_rooms:
            room = self.room_picker.text()
            self.rooms = set_rooms
            self.room_picker.reset(rooms)
            self.room_picker.select_text(room, ignore_if_missing=True)
