#
import queue
from attrdict import AttrDict
from collections import defaultdict
from Connection import ConnectionGroup
from Configuration import Configuration

class Generation(ConnectionGroup):
	def __init__(self):
		ConnectionGroup.__init__(self, Configuration.connection.environment)
		self.env_enums = AttrDict({
			'QueueTypeGeneration': { 'Ping': 0 },
			'QueueTypeWatcher': { 'Ping': 0 },
			'WatcherDataType': { 'Empty': 0 },
		})

	def _start(self):
		self.send_env_ping(True)

	def _stop(self):
		try:
			self.send_env_ping(False)
		except Exception:
			pass
		Configuration.remove_generated()

	def _update(self):
		try:
			who, obj = self.q.get(block=True, timeout=1)
		except queue.Empty:
			return
		if who == Configuration.connection.environment:
			return self.handle_env_msg(obj)
		raise ValueError(f'"{who}" is not a valid client (its message was: {obj})')

	def send_env_message(self, queueType=0, message='',
		idsAssets=[], idsEvents=[],
		idMapAsset=-1, idMapInstance=-1,
		idEventToTrigger=-1
	):
		self.conns[Configuration.connection.environment].write({
			'queueType': queueType,
			'message': message,
			'idsAssets': idsAssets,
			'idsEvents': idsEvents,
			'idMapAsset': idMapAsset,
			'idMapInstance': idMapInstance,
			'idEventToTrigger': idEventToTrigger,
		})

	def send_env_ping(self, ok=True):
		msg = 'OK' if ok else 'KO'
		self.send_env_message(queueType=self.env_enums.QueueTypeGeneration.Ping, message=msg)

	def handle_env_msg(self, obj):
		qtype = obj.queueType
		wtype = obj.watcherType
		fears = obj.fears
		msg = obj.message
		if qtype == self.env_enums.QueueTypeWatcher.Ping:
			assert wtype == self.env_enums.WatcherDataType.Empty, f'Watchers should not send pings: {obj}'
			assert msg == 'OK', f'Environment encountered an error: {obj}'
			return self.handle_env_ping()
		raise NotImplementedError(obj)

	def handle_env_ping(self):
		self.load_env_config()
		self.send_env_ping()

	def load_env_config(self):
		Configuration.load_generated()

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.stop()

if __name__ == '__main__':
    with Generation() as gen:
        gen.start()
