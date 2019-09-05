#

import os
import sys
import logging
import qdarkstyle
import PyQtToolBox
import ExceptionHook
from PyQt5 import QtCore
from attrdict import AttrDict
import PyQt5.QtWidgets as QtW
from Generation import Generation
from WindowAlgo import WindowAlgo
from WindowGame import WindowGame
from Configuration import Configuration
from WindowFakeAcq import WindowFakeAcq
from WindowFakeEnv import WindowFakeEnv
from subprocess import Popen, PIPE, STDOUT, CalledProcessError

os.chdir(os.path.split(__file__)[0] or '.')

def _forward_to(name, game=False, algo=False, fake_env=False):
    '''
        The launcher set to receive all of the main thread's Qt signals.
        This allows us to redirect a signal to any window
    '''
    def wrap(cls):
        def f(self, *args, **kwargs):
            call = lambda child: getattr(child, name)(*args, **kwargs)
            if game: call(self.win_game)
            if algo: call(self.win_algo)
            if fake_env and self.env.mocked: call(self.env.win)
        f.__name__ = name
        setattr(cls, name, f)
        return cls
    return wrap

class ThreadedCommand(ExceptionHook.Thread):
    '''Executes a command in a thread while logging the outputs'''

    def __init__(self, cmd, name=None, cwd=None):
        super().__init__(name=f'Command({name or " ".join(cmd)})')
        self.log = logging.getLogger(self.name)
        self.process = Popen(cmd, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True, cwd=cwd)

    def hooked_run(self):
        self.running = True
        self.log.info('Started')
        with self.process:
            for line in self.process.stdout:
                self.log.info(f'|> {line.rstrip()}')
        if self.process.returncode and self.running:
            raise CalledProcessError(self.process.returncode, self.process.args)

    def stop(self):
        self.log.info('Stopped')
        self.running = False
        self.process.kill()

@PyQtToolBox.add_signals(
    'clients_connected', # Namedpipes connected
    'env_handshake', # Environment is ready
    'acq_handshake', # Acquisition is ready
    'load_env_config', # Config files are loaded
    'refresh_game', # New data about the rooms
    'refresh_graph', # New data about the biofeedbacks
    'reload_generation', # Manual values where set in UI
    'request_room', # UI needs to pick a room
)
@_forward_to('request_room', algo=True)
@_forward_to('reload_generation', algo=True)
@_forward_to('load_env_config', algo=True)
@_forward_to('refresh_game', game=True, fake_env=True)
@_forward_to('refresh_graph', game=True)
class WindowLauncher(PyQtToolBox.Window):
    '''Main window: receives Qt signals and instantiate the rest of the UI'''

    def _cmd(root_idx, *cmd):
        cmd = list(cmd)
        root, arg = os.path.split(cmd[root_idx])
        if root_idx:
            cmd[root_idx] = arg
        return cmd, root

    WIDTH = 500
    HEIGHT = 500
    ENV_CMD = _cmd(0, Configuration.entry_point.environment)
    ACQ_CMD = _cmd(2, sys.executable, '-u', Configuration.entry_point.acquisition,
                   Configuration.connection.acquisition,
                   Configuration.connection.server_to_client,
                   Configuration.connection.client_to_server)
    ORE_CMD = _cmd(2, sys.executable, '-u', Configuration.entry_point.orengine)
    ANDROID_CMD = _cmd(2, sys.executable, '-u', Configuration.entry_point.android)

    class MockableWindow:

        BUTTON_COLOR = '#995555'
        RADIO_MODE = AttrDict({value: idx for idx, value in enumerate([
            'Automatic', 'External', 'Mocked'
        ])})

        def __init__(self, win, cmd):
            self.win = win
            self.cmd = cmd
            self.name = self.win.name
            self.mocked = False
            self.thread = None

            # Header
            self.title = PyQtToolBox.Title(self.name)
            self.radio_layout = PyQtToolBox.VRadioLayout(*zip(*self.RADIO_MODE.items()))
            self.header = QtW.QVBoxLayout()
            self.header.setAlignment(QtCore.Qt.AlignCenter)
            self.header.addWidget(self.title)
            self.header.addLayout(self.radio_layout)

            # Button
            self.button = QtW.QPushButton(f'Show Fake {self.name}')
            self.button.setStyleSheet('background-color:' + self.BUTTON_COLOR)
            self.button.clicked.connect(self.win.show)

            # Wait label
            self.wait = PyQtToolBox.Title(f'{self.name} handshake incomplete (waiting)')

        def mode(self):
            return self.radio_layout.radio.checkedId()

        def start(self, button_layout):
            mode = self.mode()

            if mode == self.RADIO_MODE.Mocked:
                self.mocked = True
                button_layout.addWidget(self.button)
                self.win.start()
                return

            if mode == self.RADIO_MODE.Automatic:
                cmd, cwd = self.cmd
                self.thread = ThreadedCommand(cmd, self.name, cwd)
                self.thread.start()

        def close(self):
            self.win.close()
            if self.thread is not None:
                self.thread.stop()
                self.thread.join()

    # Signal callbacks that does not redirect to a child

    def clients_connected(self):
        self.wait.setHidden(True)
        for mockable in (self.env, self.acq):
            self.layout.addWidget(mockable.wait)

    def env_handshake(self):
        self.env.wait.setHidden(True)

    def acq_handshake(self):
        self.acq.wait.setHidden(True)

    def __init__(self, gen):
        super().__init__('MindDepth Launcher', QtW.QVBoxLayout(), wmin=self.WIDTH, hmin=self.HEIGHT)

        # Instantiate windows
        self.gen = gen
        self.win_game = WindowGame(self)
        self.win_algo = WindowAlgo(self)
        self.env = self.MockableWindow(WindowFakeEnv(self, 'Environment'), self.ENV_CMD)
        self.acq = self.MockableWindow(WindowFakeAcq(self, 'Biofeedback'), self.ACQ_CMD)
        self.ore = None
        self.android = None

        def close(self):
            self.win.close()
            if self.thread is not None:
                self.thread.stop()
                self.thread.join()

        # Logo
        self.layout.addWidget(PyQtToolBox.Image(r'images\logo.png', width=self.WIDTH))

        # Radio Buttons
        radio_layout = QtW.QHBoxLayout()
        for mockable in (self.env, self.acq):
            radio_layout.addLayout(mockable.header)
        self.layout.addLayout(radio_layout)

        # Show windows
        self.menu_layout = QtW.QVBoxLayout()
        self.menu_layout.setAlignment(QtCore.Qt.AlignVCenter)
        self.start = QtW.QPushButton('Start')
        self.scene = QtW.QPushButton('Show Game State')
        self.algo = QtW.QPushButton('Show Algorithm State')
        self.start.clicked.connect(self.start_all)
        self.scene.clicked.connect(self.win_game.show)
        self.algo.clicked.connect(self.win_algo.show)
        for button in (self.start, self.scene, self.algo):
            self.menu_layout.addWidget(button)
        self.layout.addLayout(self.menu_layout)

        # Wait label
        self.wait = PyQtToolBox.Title(f'Clients not connected yet')
        self.layout.addWidget(self.wait)

        self.show()

    def start_all(self):
        '''Starts every parts of the project'''

        # Freeze settings and start mocks
        self.start.setEnabled(False)
        for mockable in (self.env, self.acq):
            for button in mockable.radio_layout.radio.buttons:
                button.setEnabled(False)
            mockable.start(self.menu_layout)

        if self.acq.mode() == self.acq.RADIO_MODE.Automatic:

            # Starts the server
            self.ore = ThreadedCommand(self.ORE_CMD[0], 'OREngine', self.ORE_CMD[1])
            self.ore.start()

            # Starts the android mock
            self.android = ThreadedCommand(self.ANDROID_CMD[0], 'Android', self.ANDROID_CMD[1])
            self.android.start()

        # Starts the Generation
        self.gen.start(thread=True, gui_signals=self)

    def close_all(self):
        '''Closes all the other windows'''
        self.gen.stop()
        self.win_game.close()
        self.win_algo.close()
        for mockable in (self.env, self.acq):
            mockable.close()
        if self.ore is not None:
            self.ore.stop()
            self.ore.join()
        if self.android is not None:
            self.android.stop()
            self.android.join()

    def closeEvent(self, event):
        self.close_all()
        event.accept()

def launcher():
    with Generation() as gen:
        with PyQtToolBox.App(style=qdarkstyle.load_stylesheet_pyqt5(), excepthook=True):
            launcher = WindowLauncher(gen)
        launcher.close_all()

if __name__ == '__main__':
    launcher()
