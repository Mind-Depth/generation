#

import time
import queue
import random
import numpy as np
from attrdict import AttrDict
from numpy.random import choice
from collections import defaultdict
from Connection import ConnectionGroup
from Configuration import Configuration

def random_choice_using_score(choices, score_callback, filter_callback=None, mini=1, maxi=None, as_list=True):
    '''
        Picks a random set of element from a list, using a score function to dermine each probability.
        We can filter which elements can or cannot be picked, as well as how many elements we want.
    '''

    # Check args
    if maxi is None:
        maxi = mini
    assert as_list or (mini == 1 and maxi == 1), f'A list is mandatory to store [{mini},{maxi}] element(s).'

    # Pre process
    if filter_callback is not None:
        mask = [filter_callback(c) for c in choices]
        real_size = len(choices)
        choices = np.array(choices)[mask]

    assert len(choices), f'None of the following elements could be used: {choices}'

    # Compute
    scores = np.array(list(score_callback(elem) for elem in choices))
    total = sum(scores)
    if total:
        # TODO Smooth differently, coef ?
        scores += 0.1 * total
        scores /= sum(scores)
    else:
        size = len(choices)
        scores = np.full(size, 1 / size)
    indices = choice(range(len(choices)), random.randint(mini, maxi), p=scores)
    values = np.array(choices)[indices]

    # Post process
    if filter_callback is not None:
        real_scores = np.zeros(real_size)
        real_scores[mask] = scores
        scores = real_scores
        indices = np.arange(real_size)[mask][indices]

    # Return
    if as_list:
        return scores, indices, values
    return scores, indices[0], values[0]

class MockGUISignals:
    '''
        Qt's UIs cannot be updated from threads, thus Qt uses signals to trigger events inside the main thread.
        In order to be able to run the Generation class in either GUI or command line (without ifs everywhere),
        we mock our GUI launcher with this class.
    '''
    class QtEmitter:
        def emit(self):
            pass
    def __getattr__(self, attr):
        return self.QtEmitter()

class Generation(ConnectionGroup):
    '''
        Connects to the environment and biofeedbacks using a system of queue.
        It reacts to events and decides which maps and assets should be used to optimize the feedbacks.
    '''

    def __init__(self):

        # Connections
        ConnectionGroup.__init__(self, Configuration.connection.acquisition, Configuration.connection.environment)
        self.connected = set()

        # Minimal agreement in order to handshake with env
        self.acq_message_type = AttrDict({key: key for key in {'CONTROL_SESSION', 'PROGRAM_STATE', 'FEAR_EVENT'}})
        self.env_enums = AttrDict({
            'QueueType': { 'Ping': 0 },
            'WatcherDataType': { 'Empty': 0 },
        })

        # Fears
        self.fears = {}
        self.ui_fears = {}
        self.ui_forced_fears = False

        # Maps
        self.maps = []
        self.assets = []

        # Rooms
        self.rooms = {}
        self.room_requests = 0
        self.current_room = None
        self.ui_forced_rooms = False

        # History
        self.feedback_history = []
        self.interaction_history = []

    # Callbacks for the parent

    def _start(self, gui_signals=MockGUISignals()):
        '''Starts the communication with the other parts'''
        self.gui_signals = gui_signals
        self.gui_signals.clientsConnected.emit()
        self.alert_all_clients(True)

    def _stop(self):
        '''Stops the communication with the other parts'''
        self.alert_all_clients(False)
        Configuration.remove_generated()

    def _update(self):
        '''Pops elements from the queue and calls the right callback'''

        try:
            who, obj = self.q.get(block=True, timeout=1) # Wait for data
        except queue.Empty:
            return # Check if the pipe is still alive

        if who == Configuration.connection.environment:
            return self.handle_env_msg(obj)

        if who == Configuration.connection.acquisition:
            return self.handle_acq_msg(obj)

        raise ValueError(f'"{who}" is not a valid client (its message was: {obj})')

    # Callbacks to send to pipes

    def send_acq_message(self, **kwargs):
        self.conns[Configuration.connection.acquisition].write(kwargs)

    def send_acq_control_session(self, ok=True):
        self.send_acq_message(message_type=self.acq_message_type.CONTROL_SESSION, status=ok)

    def send_env_message(self, queueType=0, message='', idsAssets=[], idMapAsset=-1, idMapInstance=-1):
        self.conns[Configuration.connection.environment].write({
            'queueType': queueType,
            'message': message,
            'idsAssets': idsAssets,
            'idMapAsset': idMapAsset,
            'idMapInstance': idMapInstance,
        })

    def send_env_ping(self, ok=True):
        msg = 'OK' if ok else 'KO'
        self.send_env_message(queueType=self.env_enums.QueueType.Ping, message=msg)

    def send_env_room(self, chosen_assets, chosen_map):
        '''Sends the selected map and assets and saves them to be able to track their effect afterward'''

        # Sanity check
        room_id = f'map{len(self.rooms):03d}-asset{chosen_map.id}'
        assert room_id not in self.rooms, f'Duplicate Room ID "{chosen_map.instance_id}"'

        # Keep track
        t = int(time.time())
        self.rooms[room_id] = AttrDict({
            'created': t,
            'deleted': None,
            'entered': None,
            'assets': chosen_assets,
            'map': chosen_map,
            'active_times': [t],
        })
        self.current_map = chosen_map.id

        # Broadcast
        self.send_env_message(
            queueType = self.env_enums.QueueType.Data,
            idsAssets = [a.id for a in chosen_assets],
            idMapAsset = chosen_map.id,
            idMapInstance=room_id
        )
        self.gui_signals.refreshGame.emit()

    def alert_all_clients(self, ok=True):
        '''Sends the current program state to the other parts'''
        for f in (self.send_acq_control_session, self.send_env_ping):
            if ok:
                f(ok)
                continue
            # In some cases, clients stop before the server (e.g. if they encountered an internal error)
            # Sending errors are irrelevant at this point because the message is for them to stop anyway.
            try:
                f(ok)
            except Exception:
                pass

    def are_clients_ready(self):
        return len(self.connected) == 2

    # Handlers for different message types

    def handle_alive_connection(self, name, alert, *callbacks):
        '''Asserts the connection is still valid, used as part of the handshake process'''

        # Keep alive
        if name in self.connected:
            return alert(self.are_clients_ready())

        self.connected.add(name)
        for callback in callbacks:
            callback()

        # Respond now
        if self.are_clients_ready():
            self.alert_all_clients()

    def handle_acq_msg(self, obj):
        '''Redirects messages to the right handler'''
        mtype = obj.message_type
        if mtype == self.acq_message_type.PROGRAM_STATE:
            assert obj.status, f'Acquisition encountered an error: {obj}'
            return self.handle_acq_program_state()

        if mtype == self.acq_message_type.FEAR_EVENT:
            return self.handler_acq_fear_event(obj)
        raise ValueError(f'Acquisition sent an invalid type "{mtype}": {obj}')

    def handle_acq_program_state(self):
        self.handle_alive_connection(
            Configuration.connection.acquisition,
            self.send_acq_control_session,
            self.gui_signals.acqHandshake.emit
        )

    def handler_acq_fear_event(self, obj):
        # TODO real computation
        t = obj.timestamp
        value = obj.fear_accuracy / 2
        if not obj.status_fear:
            value *= -1
        self.feedback_history.append((t, value + 0.5))
        self.gui_signals.refreshGraph.emit()
        value /= 10
        fears = set()
        for interaction_time, interaction_fears in reversed(self.interaction_history):
            if interaction_time + 5 < t:
                break
            fears.update(interaction_fears)
        for fear in fears:
            self.fears[fear] = min(max(self.fears[fear] + value, 0.0), 1.0)
        if fears and not self.ui_forced_fears:
            self.gui_signals.reloadGeneration.emit()

    def handle_env_msg(self, obj):
        '''Redirects messages to the right handler'''

        qtype = obj.queueType
        wtype = obj.watcherType
        fears = obj.fears
        msg = obj.message

        # Simple handshake
        if qtype == self.env_enums.QueueType.Ping:
            assert wtype == self.env_enums.WatcherDataType.Empty, f'Watchers should not send pings: {obj}'
            assert msg == 'OK', f'Environment encountered an error: {obj}'
            return self.handle_env_ping()

        assert qtype == self.env_enums.QueueType.Data, obj

        # Room management

        if wtype == self.env_enums.WatcherDataType.ChangedRoom:
            return self.handle_env_changed_room(obj.time, msg)
        if wtype == self.env_enums.WatcherDataType.DeletedRoom:
            return self.handle_env_deleted_room(obj.time, msg)

        assert not msg, obj

        if wtype == self.env_enums.WatcherDataType.RequestRoom:
            return self.handle_env_request_room()

        # Fear management

        if wtype == self.env_enums.WatcherDataType.ActivePlayerInteraction:
            return self.handle_env_active_player_interaction(obj.time, fears)

        if wtype == self.env_enums.WatcherDataType.PassivePlayerInteraction:
            return self.handle_env_passive_player_interaction(obj.time, fears)

        # Player management

        if wtype == self.env_enums.WatcherDataType.ActivePlayer:
            return self.handle_env_active_player(obj.time)

        if wtype == self.env_enums.WatcherDataType.PassivePlayer:
            return self.handle_env_passive_player(obj.time)

        raise ValueError(f'Environment sent an invalid type "{wtype}": {obj}')

    def handle_env_ping(self):
        self.handle_alive_connection(
            Configuration.connection.environment,
            self.send_env_ping,
            self.gui_signals.envHandshake.emit,
            self.load_env_config
        )

    # Callbacks for lower functions

    def _can_use_map(self, m):
        return self.current_map not in m.banned_ids

    def _can_use_asset(self, m, a):
        return len(m.fears.intersection(a.fears)) > 0

    def _compute_score(self, obj):
        fears = self.ui_fears if self.ui_forced_fears else self.fears
        return sum(fears[fear] for fear in obj.fears)

    def get_map_proposition(self):
        return random_choice_using_score(
            self.maps,
            self._compute_score,
            filter_callback=self._can_use_map,
            as_list=False
        )

    def get_assets_proposition(self, map_ref):
        def usable(a):
            return self._can_use_asset(map_ref, a)
        return [
            random_choice_using_score(
                cat.assets,
                self._compute_score,
                filter_callback=usable,
                mini=cat.use_min,
                maxi=cat.use_max
            ) for cat in map_ref.categories_config
        ]

    def handle_env_request_room(self):
        '''Callback for messages of type RequestRoom'''

        # Ask the UI
        if self.ui_forced_rooms:
            self.room_requests += 1
            self.gui_signals.requestRoom.emit()
            return

        # Get a random room
        _, _, best_map = self.get_map_proposition()
        best_assets = []
        for _, _, assets in self.get_assets_proposition(best_map):
            best_assets.extend(assets)
        self.send_env_room(best_assets, best_map)

    def _add_room_activity(self, room, t):
        times = room['active_times']
        assert not times or times[-1] <= t, (room, t)
        times.append(t)

    def handle_env_changed_room(self, t, room_id):
        '''Callback for messages of type ChangedRoom'''

        # Sanity check
        room = self.rooms.get(room_id)
        assert room is not None, f'Unknown room "{room_id}"'
        assert room_id != self.current_room, f'Already in "{room_id}"'
        assert room.deleted is None, f'Cannot move into "{room_id}": was deleted at timestamp {room.deleted}'

        # Keep track
        current = self.rooms.get(self.current_room)
        if current is not None:
            current.entered = None
            self._add_room_activity(current, t)
        room.entered = t
        self._add_room_activity(room, t)
        self.current_room = room_id

        # Broadcast
        self.gui_signals.refreshGame.emit()

    def handle_env_deleted_room(self, t, room_id):
        '''Callback for messages of type DeletedRoom'''

        # Sanity check
        room = self.rooms.get(room_id)
        assert room is not None, f'Unknown room "{room_id}"'
        assert room.entered is None, f'Cannot delete an active room "{room_id}"'

        # Keep track
        room.deleted = t
        self._add_room_activity(room, t)

        # Broadcast
        self.gui_signals.refreshGame.emit()

    def _interaction_handler(self, t, fears):
        self.interaction_history.append((t, fears)) # TODO Real computation

    def handle_env_active_player_interaction(self, *args):
        return self._interaction_handler(*args) # TODO ActivePlayerInteraction

    def handle_env_passive_player_interaction(self, *args):
        return self._interaction_handler(*args) # TODO PassivePlayerInteraction

    def handle_env_active_player(self, t):
        pass # TODO ActivePlayer

    def handle_env_passive_player(self, t):
        pass # TODO PassivePlayer

    def load_env_config(self):
        '''Loads runtime-generated configuration'''

        Configuration.load_generated()

        # Fills internal mapping type->assets
        self.assets = list(Configuration.loaded.models)
        self.maps = list(Configuration.loaded.maps)
        self.current_map = -1
        self.type_to_assets = defaultdict(list)
        for asset in self.assets:
            asset.fears = set(asset.fears)
            self.type_to_assets[asset.object_type].append(asset)

        # Fills internal mapping name->enum and enum->name
        def enums_to_dict(reverse=False):
            key = 'key'
            value = 'value'
            if reverse:
                key, value = value, key
            return AttrDict({
                name: {
                    kv[key]: kv[value] for kv in enum
                } for name, enum in Configuration.loaded.enums.items()
            })
        self.env_enums.update(enums_to_dict())
        self.reverse_enums = enums_to_dict(reverse=True)

        # Combines into a single object
        for m in self.maps:
            categories = list(m.categories_config)
            m.fears = set(m.fears)
            for category in categories:
                category.name = self.reverse_enums.ObjectType[category.type]
                category.assets = self.type_to_assets.get(category.type, [])
            m.categories_config = categories
            m.id = int(m.id)

        self.fears = {fear: 0 for fear in self.reverse_enums.Fears}
        self.ui_fears = dict(self.fears)

        self.gui_signals.loadEnvConfig.emit()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    # Callbacks to handle the manual/automatic UI modes

    #       Fears

    def ui_get_fears(self):
        if not self.fears:
            return {}
        return {self.reverse_enums.Fears[k]: v for k, v in self.fears.items()}

    def ui_set_fear(self, key, value):
        self.ui_fears[self.env_enums.Fears[key]] = value

    def ui_force_fears(self, toggled):
        self.ui_forced_fears = toggled
        if not toggled:
            self.ui_fears = dict(self.fears)

    #       Room & Maps bindings

    def ui_get_map(self):
        return self.get_map_proposition()[:-1]

    def ui_get_assets(self, map_ref):
        return [cat[:-1] for cat in self.get_assets_proposition(map_ref)]

    def ui_force_rooms(self, toggled):
        self.ui_forced_rooms = toggled
        if not toggled:
            for _ in range(self.room_requests):
                self.handle_env_request_room()
            self.room_requests = 0
            self.gui_signals.requestRoom.emit()

    def ui_send_room(self, chosen_assets, chosen_map):
        if self.room_requests:
            self.room_requests -= 1
            self.send_env_room(chosen_assets, chosen_map)
            self.gui_signals.requestRoom.emit()

if __name__ == '__main__':
    with Generation() as gen:
        gen.start()
