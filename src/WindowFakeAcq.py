#

import time
import PyQtToolBox
from PyQt5 import QtCore
import PyQt5.QtWidgets as QtW
from Connection import ConnectionMock
from Configuration import Configuration

class AcqConnectionMock(ConnectionMock):
    '''Formats and sends messages in the same way the real biofeedbacks would'''

    def __init__(self, group):
        super().__init__(Configuration.connection.acquisition, group)

    def queue_message(self, **kwargs):
        super().queue_message(kwargs)

    def program_state(self, status=True, message=''):
        self.queue_message(message_type='PROGRAM_STATE', status=status, message=message)

    def fear_event(self, status_fear, fear_accuracy):
        self.queue_message(
            message_type='FEAR_EVENT',
            status_fear=status_fear,
            fear_accuracy=fear_accuracy,
            timestamp=int(time.time())
        )

class WindowFakeAcq(PyQtToolBox.Window):
    '''UI to emulate the sending of messages from the biofeedbacks'''

    WIDTH = 500
    HEIGHT = 100

    def __init__(self, root, name):
        self.root = root
        self.name = name
        super().__init__(f'Fake {self.name}', QtW.QGridLayout(), wmin=self.WIDTH, hmin=self.HEIGHT)

        self.mock = AcqConnectionMock(self.root.gen)
        self.layout.setAlignment(QtCore.Qt.AlignVCenter)
        self.slider = PyQtToolBox.Slider()
        self.layout.addWidget(self.slider, 0, 0, 1, 2)
        self.begin = QtW.QPushButton('Scared')
        self.begin.clicked.connect(self._button_callback(True))
        self.layout.addWidget(self.begin, 1, 0, 1, 1)
        self.end = QtW.QPushButton('Calmed')
        self.end.clicked.connect(self._button_callback(False))
        self.layout.addWidget(self.end, 1, 1, 1, 1)

    # Callback wrapper adding UI selected accuracy into messages

    def _button_callback(self, status):
        def f(*args):
            self.mock.fear_event(status, self.slider.get())
        return f

    def start(self):
        '''Emulates a handshake'''
        self.mock.connect()
        self.mock.program_state()
