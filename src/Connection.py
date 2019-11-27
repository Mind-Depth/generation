#

import json
import queue
import logging
import win32file
import win32pipe
import pywintypes
import win32event
import ExceptionHook
from attrdict import AttrDict

from Configuration import Configuration

class Connection:
	'''Double read & write pipes wrapper'''

	CONNECTION_TIMEOUT = 100
	MAX_STRING_SIZE = 200

	def __init__(self, name):
		'''Creates pipes objects'''
		self.name = name
		self.running = False
		self.log = logging.getLogger(f'Connection({self.name})')
		self.pipe_in = win32pipe.CreateNamedPipe(
			r'\\.\pipe\{}_{}'.format(self.name, Configuration.connection.client_to_server),
			win32pipe.PIPE_ACCESS_INBOUND |  win32file.FILE_FLAG_OVERLAPPED,
			win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
		1, Configuration.connection.chunk_size, Configuration.connection.chunk_size, 0, None)
		self.pipe_out = win32pipe.CreateNamedPipe(
			r'\\.\pipe\{}_{}'.format(self.name, Configuration.connection.server_to_client),
			win32pipe.PIPE_ACCESS_OUTBOUND | win32file.FILE_FLAG_OVERLAPPED,
			win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
		1, Configuration.connection.chunk_size, Configuration.connection.chunk_size, 0, None)
		self.pipes = [self.pipe_in, self.pipe_out]
		self.log.info('Created')

	def _hide_legitimate_errors(f):
		def func(self, *args, **kwargs):
			try:
				return f(self, *args, **kwargs)
			except pywintypes.error as e:
				if self.running:
					raise
		func.__name__ = f.__name__
		return func

	@_hide_legitimate_errors
	def read(self):
		'''Reads a json object'''
		error, msg = win32file.ReadFile(self.pipe_in, Configuration.connection.chunk_size)
		assert not error, error
		s = msg.rstrip(b'\x00').decode()
		preview = s[:self.MAX_STRING_SIZE-3] + '...' if len(s) > self.MAX_STRING_SIZE else s
		self.log.info(f'Recv:{preview}')
		return None if not s else AttrDict(json.loads(s))

	@_hide_legitimate_errors
	def write(self, msg):
		'''Writes a json object'''
		s = json.dumps(msg)
		win32file.WriteFile(self.pipe_out, (s + '\r\n').encode())
		self.log.info(f'Send:{s}')

	def start(self):
		'''Connects pipes'''
		self.log.info('Blocked')
		self.running = True
		overlapped = pywintypes.OVERLAPPED()
		for pipe in self.pipes:
			win32pipe.ConnectNamedPipe(pipe, overlapped)
		unconnected = list(self.pipes)
		while unconnected:
			code = win32event.WaitForMultipleObjects(unconnected, True, self.CONNECTION_TIMEOUT)
			if code != win32event.WAIT_TIMEOUT:
				break
			for i in range(len(unconnected)):
				pipe = unconnected.pop(0)
				try:
					win32pipe.GetNamedPipeClientProcessId(pipe)
				except pywintypes.error as e:
					unconnected.append(pipe)
		self.log.info('Unblocked')

	def stop(self):
		'''Closes pipes'''
		if not self.running:
			return
		self.running = False
		for pipe in self.pipes:
			win32file.CloseHandle(pipe)
		self.log.info('Stopped')

class ConnectionGroup:
    '''Manages several Connection objects with threads'''

    def __init__(self, *names):
        '''Creates sevral Connection objects'''
        self.conns = {}
        self.running = False
        self.readers = []
        self.q = queue.Queue()
        for name in names:
            self.conns[name] = Connection(name)

    def start(self, thread=False, *args, **kwargs):
        '''Starts Connections and threads'''
        if thread:
            t = ExceptionHook.Thread(target=self.start, args=args, kwargs=kwargs)
            t.start()
            return t
        self.running = True
        for name, conn in self.conns.items():
            conn.start()
            if not self.running:
                return
        for name, conn in self.conns.items():
            reader = ExceptionHook.Thread(
                target=self._loop_running,
                args=(f'ConnectionGroup(Read-{name})', self._reader, name, conn)
            )
            reader.start()
            self.readers.append(reader)
        self._start(*args, **kwargs)
        self._loop_running('ConnectionGroup(Write)', self._update)

    def stop(self):
        '''Stops Connections and threads'''
        if not self.running:
            return
        self.running = False
        self._stop()
        for name, conn in self.conns.items():
            conn.stop()
        for reader in self.readers:
            try:
                reader.join()
            except RuntimeError:
                pass

    def _loop_running(self, name, f, *args):
        '''Wrapper for threads' callback'''
        log = logging.getLogger(name)
        log.info('Started')
        try:
            while self.running:
                f(*args)
        except:
            log.error('Broke')
            self.stop()
            raise
        log.info('Stopped')

    def _reader(self, name, conn):
        '''Thread's callback to read and add to a queue'''
        obj = conn.read()
        if obj:
            self.q.put((name, obj))

    def _start(self, *args, **kwargs):
        '''Called right after connections are made'''
        raise NotImplementedError()

    def _stop(self):
        '''Called right before connections are closed'''
        raise NotImplementedError()

    def _update(self):
        '''Callback that takes over the main thread'''
        raise NotImplementedError()
