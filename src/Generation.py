#
import queue
import random
from attrdict import AttrDict
from collections import defaultdict
from Connection import ConnectionGroup
from Configuration import Configuration

class Generation(ConnectionGroup):
	def __init__(self):
		ConnectionGroup.__init__(self, Configuration.connection.environment)
		self.env_enums = AttrDict({
			'EnvironmentMessageType': { 'Terminate': 0, 'Initialize': 1 },
			'GenerationMessageType': { 'Terminate': 0, 'Initialize': 1}
		})

	def _start(self):
		self.send_env_initialize()

	def _stop(self):
		try:
			self.send_env_terminate()
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

	def send_env_message(self, **kw):
		defaults = {
			'type': 0,
			'message': '',
			'mapId': '',
			'eventIds': [],
			'modelGroupIds': {},
			'fear': -1,
			'fearIntensity': 0
		}
		defaults.update(kw)
		self.conns[Configuration.connection.environment].write(defaults)

	def send_env_initialize(self):
		self.send_env_message(type=self.env_enums.GenerationMessageType.Initialize)

	def send_env_terminate(self):
		self.send_env_message(type=self.env_enums.GenerationMessageType.Terminate)

	def send_env_room(self, m, models, events):
		model_dict = defaultdict(list)
		for model in models:
			model_dict[model.type].append(model.id)
		self.send_env_message(
			type = self.env_enums.GenerationMessageType.RoomConfiguration,
			mapId = m.id,
			modelGroupIds = [{'type': key, 'modelIds': value} for key, value in model_dict.items()],
			eventIds = [event.id for event in events]
		)

	def handle_env_msg(self, obj):
		if obj.type == self.env_enums.EnvironmentMessageType.Terminate:
			return self.stop()
		if obj.type == self.env_enums.EnvironmentMessageType.Initialize:
			return self.handle_env_initialize()
		if obj.type == self.env_enums.EnvironmentMessageType.RequestRoom:
			return self.handle_env_request_room()
		raise NotImplementedError(obj)

	def handle_env_initialize(self):
		self.load_env_config()
		self.start_game()

	def handle_env_request_room(self):
		# TODO base decision on phobias
		m = random.choice(self.maps)
		models = [
				random.choice(self.models[category_config.type])
				for category_config in m.categories_config
				for _ in range(random.randint(category_config.use_min, category_config.use_max))
		]
		self.send_env_room(m, models, [])

	def load_env_config(self):
		Configuration.load_generated()
		for enum, content in Configuration.loaded.enums.items():
			self.env_enums[enum] = {kv['key']: kv['value'] for kv in content}
		self.env_enums.update()
		self.maps = Configuration.loaded.maps
		self.models = defaultdict(list)
		for model in Configuration.loaded.models:
			self.models[model.type].append(model)

	def start_game(self):
		self.send_env_message(type=self.env_enums.GenerationMessageType.Start)

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.stop()

if __name__ == '__main__':
    with Generation() as gen:
        gen.start()
