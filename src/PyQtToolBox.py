#

import traceback
import ExceptionHook
from PyQt5.Qt import Qt
from PyQt5 import QtCore, QtGui
import PyQt5.QtWidgets as QtW

def _sneak2camel(name):
    '''Transforms a sneak_case string to a camelCase one (used to automatically generate signal names)'''
    head, *tail = name.split('_')
    return head + ''.join(t[0].upper() + t[1:] for t in tail)

def add_signals(*args):
    '''Add Qt signals and to a given class'''
    signals = [(name, _sneak2camel(name)) for name in args]
    def wrap(cls):
        class Cls(cls):
            locals().update({camel: QtCore.pyqtSignal() for _, camel in signals})
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for name, camel in signals:
                    getattr(self, camel).connect(getattr(self, name))
        return Cls
    return wrap

def ui_factory(obj, count):
    '''Preallocate widgets or layouts in the UI thread'''
    def wrap(cls):
        class Cls(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.factory = getattr(self, 'factory', {})
                assert obj not in self.factory, f'{cls} already contains a factory for {obj}'
                self.factory[obj] = [obj() for _ in range(count)]
            def instanciate(self, obj):
                return self.factory[obj].pop()
        Cls.__name__ = f'{cls.__name__}[{obj} factory]'
        return Cls
    return wrap

class OkBox(QtW.QMessageBox):
    '''Message box with a 'ok' and a 'details' buttons'''
    def __init__(self, title, text, info=None, detail=None, detail_size=None):
        super().__init__()
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(self.Ok)
        if info is not None:
            self.setInformativeText(info)
        if detail is not None:
            self.setDetailedText(detail)
            if detail_size is not None:
                self.findChild(QtW.QTextEdit).setFixedSize(*detail_size)

class Image(QtW.QLabel):
    '''Image loaded from a file'''
    def __init__(self, path, width=None, height=None, alignment=Qt.AlignCenter):
        super().__init__()
        pix = QtGui.QPixmap(path)
        if width is not None:
            pix = pix.scaledToWidth(width)
        if height is not None:
            pix = pix.scaledToHeight(height)
        self.setPixmap(pix)
        self.setAlignment(alignment)

class Title(QtW.QLabel):
    '''Label with extra configuration'''
    def __init__(self, text='', size=8, bold=True, alignment=Qt.AlignCenter):
        super().__init__(text)
        self.font = QtGui.QFont('Times', size)
        self.font.setBold(bold)
        self.setFont(self.font)
        self.setAlignment(alignment)

class RadioGroup(QtW.QButtonGroup):
    '''Group of radio button sharing a logic'''
    def __init__(self, names=[], ids=[], check=0):
        super().__init__()
        ids = list(ids) + [-1]*(len(names)-len(ids))
        self.buttons = []
        for name, bid in zip(names, ids):
            self.add(name, bid)
        if names and check is not None:
            self.buttons[check].setChecked(True)
    def add_button(self, button, name=None, bid=-1, checked=False):
        if name is not None:
            button.setText(name)
        self.buttons.append(button)
        self.addButton(button, bid)
        button.setChecked(checked)
    def add(self, *args, **kwargs):
        button = QtW.QRadioButton()
        self.add_button(button, *args, **kwargs)
        return button

class ComboBox(QtW.QComboBox):
    '''Entry that expand into a list of choices. Fonctions relatedto research and focus were added'''

    def reset(self, items):
        '''Changes the choices available'''
        self.clear()
        self.addItems(items)

    def find_text(self, text, raise_error=False):
        '''Return the index of the given text within the combo box'''
        idx = self.findText(text, Qt.MatchFixedString)
        if idx < 0 and raise_error:
            raise AttributeError(f'"{text}" not in ComboBox')
        return idx

    def select_text(self, text, ignore_if_missing=False, empty_if_missing=False):
        '''Select the given text from the combo box choices'''
        if ignore_if_missing and empty_if_missing:
            raise ValueError('"ignore_if_missing" and "empty_if_missing" cannot both be set to True')
        idx = self.find_text(text, raise_error = not(ignore_if_missing or empty_if_missing))
        if idx < 0 and ignore_if_missing:
            return
        self.setCurrentIndex(idx)

    def text(self):
        '''Returns the current text'''
        return str(self.currentText())

class Colored(QtW.QWidget):
    '''Layout with a background color'''
    def __init__(self, layout, background=None):
        super().__init__()
        self.layout = layout
        self.setLayout(self.layout)
        if background is not None:
            self.setStyleSheet('background-color:' + background)

def _radio_layout(cls):
    class C(cls):
        '''Layout with a group of radio buttons'''
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.radio = RadioGroup(*args, **kwargs)
            for button in self.radio.buttons:
                self.addWidget(button)
    return C
HRadioLayout = _radio_layout(QtW.QHBoxLayout)
VRadioLayout = _radio_layout(QtW.QVBoxLayout)

class ScrollableArea(QtW.QScrollArea):
    '''Layout with a scrollbar'''
    def __init__(self, layout=QtW.QVBoxLayout):
        super().__init__()
        self.layout = layout()
        self.content = QtW.QWidget()
        self.content.setLayout(self.layout)
        self.setWidgetResizable(True)
        self.setWidget(self.content)

class ProgressBar(QtW.QProgressBar):
    '''A scalable progress bar'''
    def __init__(self, progress_max=100):
        super().__init__()
        self.progress_max = progress_max
        self.setMaximum(self.progress_max)
    def set(self, value):
        self.setValue(int(value * self.progress_max))

class Slider(QtW.QSlider):
    '''A scalable slider with a callback'''
    def __init__(self, orientation=Qt.Horizontal, slider_max=100, step_count=10, callback=None):
        super().__init__(orientation)
        self.slider_max = slider_max
        self.setRange(0, self.slider_max)
        self.setSingleStep(self.slider_max // step_count)
        self.setValue(0)
        if callback is not None:
            if isinstance(callback, tuple):
                callback, *args = callback
            else:
                args = tuple()
            self.set_callback(callback, *args)
    def set(self, value):
        self.setValue(int(value * self.slider_max))
    def get(self):
        return self.value() / self.slider_max
    def set_callback(self, callback, *args):
        self.valueChanged.connect(lambda: callback(*args))

class IntegerSelector:
    '''A group of buttons and labels allowing the selection of an integer'''

    def __init__(self, mini=None, maxi=None, callback=None, button_limit=32):
        self.mini = mini
        self.maxi = maxi
        self.callback = callback
        self.label = QtW.QLabel('0')
        self.value = 0
        self.less = QtW.QPushButton('<')
        self.less.clicked.connect(self._less)
        self.less.setMaximumWidth(button_limit)
        self.more = QtW.QPushButton('>')
        self.more.clicked.connect(self._more)
        self.more.setMaximumWidth(button_limit)

    def set(self, value):
        '''Sets the value and calls an eventual callback'''
        self.value = value
        self.label.setText(str(self.value))
        if self.callback is not None:
            self.callback()

    def _less(self):
        '''Decreases with a limit'''
        if self.mini is None or self.value > self.mini:
            self.set(self.value - 1)

    def _more(self):
        '''Increases with a limit'''
        if self.maxi is None or self.value < self.maxi:
            self.set(self.value + 1)

    def setEnabled(self, b):
        '''Toggles the setters'''
        self.less.setEnabled(b)
        self.more.setEnabled(b)

class FlagedInterface:
    '''Abstract class that triggers upon going out of given bound. A label color is then changed'''

    def Outside(mini, maxi):
        '''Callback creactor to check if a number is within a given range'''
        def f(value):
            return value < mini or value > maxi
        return f

    def Null(value):
        return not value

    def __init__(self, obj, text, trigger=Null, triggered_color='#990000'):
        self.obj = obj
        self.text = text
        self.trigger = trigger
        self.triggered_color = triggered_color

    def set(self, value):
        '''Sets the value and updates the color and font of the binded label'''
        self._set(value)
        trigger = self.trigger(value)
        self.text.setStyleSheet(('color:' + self.triggered_color) * trigger)
        font = self.text.font
        if callable(font):
            font=font()
        font.setBold(trigger)
        self.text.setFont(font)

    def _set(self, value):
        raise NotImplementedError('_set')

class FlagedObject(FlagedInterface):
    def _set(self, value):
        self.obj.set(value)

class FlagedValue(FlagedInterface):
    def _set(self, value):
        self.obj = value
        self.text.setText(str(value))

class GridLayout(QtW.QGridLayout):
    '''Grid with constant stretches and alignments on each rows'''

    def __init__(self, stretches=[], alignments=[]):
        super().__init__()
        for stretch in enumerate(stretches):
            self.setColumnStretch(*stretch)
        self.alignments = alignments
        self.rows = 0

    def add_row(self, *widgets):
        '''Adds the widgets while applying the given constraints'''
        alignments = self.alignments + [None]*len(widgets)
        for col, (widget, alignment) in enumerate(zip(widgets, alignments)):
            if widget is None:
                continue
            kw = {}
            if alignment is not None:
                kw['alignment'] = alignment
            self.addWidget(widget, self.rows, col, **kw)
        self.rows += 1

class Window(QtW.QWidget):
    '''Window with extra parameters'''
    def __init__(self, title, layout, wmin=0, hmin=0):
        super().__init__()
        self.setMinimumSize(wmin, hmin)
        self.setWindowTitle(title)
        self.layout = layout
        self.setLayout(self.layout)

class ChoiceBasedLayout(QtW.QVBoxLayout):
    '''Layout with a radio button group'''
    def __init__(self, title, choices, title_size=12):
        super().__init__()
        self.addWidget(Title(title, size=title_size))
        self.radio_layout = HRadioLayout(choices)
        self.addLayout(self.radio_layout)
        self.choice_buttons = self.radio_layout.radio.buttons

class AutoManualLayout(ChoiceBasedLayout):
    '''Layout with a binary auto/manual selector'''
    def __init__(self, title):
        super().__init__(title, ['Automatically computed', 'Manualy set'])
        self.auto, self.manual = self.choice_buttons
    def is_auto(self):
        return self.auto.isChecked()

class LoadableControlLayout(AutoManualLayout):
    '''Layout designed to be loaded at runtime and changed between manual and automatic mode'''

    def __init__(self, title):
        super().__init__(title)
        self._toggle_choice_base(False)
        self.auto.toggled.connect(self._refresh)
        self._enable_on_manual = []
        self._enable_on_auto = []

    def _toggle_choice_base(self, toggle):
        '''Changes the mode'''
        self.auto.setEnabled(toggle)
        self.manual.setEnabled(toggle)

    def _refresh(self):
        '''Toggles objects corresponding to the current mode, and reloads the ui'''
        auto = self.is_auto()
        for obj in self._enable_on_manual:
            obj.setEnabled(not auto)
        for obj in self._enable_on_auto:
            obj.setEnabled(auto)
        self._force_ui_on_manual(not auto)
        self._reload()

    def _load(self):
        '''Creates the UI'''
        self._toggle_choice_base(True)
        self._create()
        self._refresh()

    def _reload(self):
        raise NotImplementedError('_reload')

    def _force_ui_on_manual(self, manual):
        raise NotImplementedError('_force_ui_on_manual')

@add_signals('excepthook_handler')
class App(QtW.QApplication):
    '''Application able to to display uncaught errors in a message box before quitting properly'''

    MSGBOX_SIZE=(600, 600)

    def __init__(self, style=None, excepthook=False, msgbox_size=MSGBOX_SIZE):
        super().__init__([])
        self.msgbox_size = msgbox_size
        if style is not None:
            self.setStyleSheet(style)
        if excepthook:
            ExceptionHook.add_after(self.excepthook)

    def excepthook_handler(self):
        '''Handler callbale from the main thread only'''
        exctype, value, _ = self.exception
        text = 'The following error was not catched and killed its thread:'
        info = str(value)
        if info:
            info = ': ' + info
        detail = ''.join(traceback.format_exception(*self.exception))
        msg = OkBox('Error', text, exctype.__name__ + info, detail, self.msgbox_size)
        msg.exec_()
        self.quit()

    def excepthook(self, *exception):
        '''Handler callbale from any thread'''
        self.exception = exception
        self.excepthookHandler.emit()

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        if not any(exception):
            self.exec_()
