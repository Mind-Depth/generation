#

'''
Each uncaugh error pass through an 'excepthook' supposed to dump the error
Here are a few functions letting us run callbacks right before / right after / instead of the usual hook
'''

import sys
import logging
import threading
import traceback

def _update(*handlers):
    def f(*exception):
        for handler in handlers:
            handler(*exception)
    global _excepthook
    _excepthook = f

def add_before(handler):
    _update(handler, _excepthook)

def add_after(handler):
    _update(_excepthook, handler)

def replace(handler):
    _update(handler)

_log = logging.getLogger()
def _base_hook(*exception):
    for line in ''.join(traceback.format_exception(*exception)).split('\n'):
        _log.error(line)
_excepthook = _base_hook

def excepthook(*exception):
    _excepthook(*exception)
sys.excepthook = excepthook

class Thread(threading.Thread):
    '''Makes threads errors be handled by out custom excepthook'''

    def hooked_run(self):
        '''Meant to be overloaded'''
        super().run()

    def run(self):
        try:
            self.hooked_run()
        except SystemExit:
            pass
        except:
            sys.excepthook(*self._exc_info())
