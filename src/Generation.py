#
import queue
import random
from attrdict import AttrDict
from collections import defaultdict
from Connection import ConnectionGroup
from Configuration import Configuration

class Generation(ConnectionGroup):

	# CLASS

	def __init__(self):
		ConnectionGroup.__init__(self, Configuration.connection.environment, Configuration.connection.acquisition)
		self.acq_message_type = AttrDict({key: key for key in {'INIT', 'CONTROL_SESSION', 'PROGRAM_STATE', 'FEAR_EVENT'}})
		self.env_enums = AttrDict({
			'EnvironmentMessageType': { 'Terminate': 0, 'Initialize': 1 },
			'GenerationMessageType': { 'Terminate': 0, 'Initialize': 1}
		})

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.stop()

	# CONNECTION GROUP

	def _start(self):
		self.send_env_initialize()
		self.send_acq_initialize()

	def _stop(self):
		try:
			self.send_env_terminate()
			self.send_acq_control_session(False)
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
		if who == Configuration.connection.acquisition:
			return self.handle_acq_msg(obj)
		raise ValueError(f'"{who}" is not a valid client (its message was: {obj})')

	# GEN WORKFLOW

	def start_game(self):
		self.send_env_message(type=self.env_enums.GenerationMessageType.Start)
		self.fears = {fear: 0 for fear in self.env_enums.Fears.values()}

	# TODO quit message type

	# ENV SEND

	def send_env_message(self, **kw):
		defaults = {
			'type': 0,
			'message': '',
			'mapId': '',
			'eventIds': [],
			'modelGroups': [],
			'fear': -1,
			'fearIntensity': 0
		}
		defaults.update(kw)
		self.conns[Configuration.connection.environment].write(defaults)

	def send_env_initialize(self):
		self.send_env_message(type=self.env_enums.GenerationMessageType.Initialize)

	def send_env_terminate(self):
		self.send_env_message(type=self.env_enums.GenerationMessageType.Terminate)

	def send_env_room(self, m, models, events, fear, fearIntensity):
		model_dict = defaultdict(list)
		for model in models:
			model_dict[model.type].append(model.id)
		self.send_env_message(
			type = self.env_enums.GenerationMessageType.RoomConfiguration,
			mapId = m.id,
			modelGroups = [{'type': key, 'modelIds': value} for key, value in model_dict.items()],
			eventIds = [event.id for event in events]
		)

	# ENV RECV

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
		# TODO unlock start button instead
		self.start_game()

	def handle_env_request_room(self):

		# TODO base decision differently
		tested = {}
		untested = {}
		for fear, value in self.fears.items():
			(tested if value else untested)[fear] = value
		fears = list((untested if untested else test).items())
		fear, value = max(fears, key=lambda kv: kv[1])

		# TODO score each map potential
		m = random.choice(self.maps)

		# TODO score models
		filtered_models = {
			mtype: list(filter(lambda model: fear in model.fears, models))
			for mtype, models in self.models.items()
		}

		# TODO try to prevent duplicates
		models = [
				random.choice(filtered_models[category_config.type])
				for category_config in m.categories_config
				for _ in range(random.randint(category_config.use_min, category_config.use_max))
		]

		self.fear = fear
		self.send_env_room(m, models, [], fear, value)

	# ENV MISC

	def load_env_config(self):
		Configuration.load_generated()
		for enum, content in Configuration.loaded.enums.items():
			self.env_enums[enum] = {kv['key']: kv['value'] for kv in content}
		self.env_enums.update()
		self.maps = Configuration.loaded.maps
		self.models = defaultdict(list)
		for model in Configuration.loaded.models:
			self.models[model.type].append(model)

	# ACQ SEND

	def send_acq_message(self, **kwargs):
		self.conns[Configuration.connection.acquisition].write(kwargs)

	def send_acq_initialize(self):
		self.send_acq_message(message_type=self.acq_message_type.INIT)

	def send_acq_control_session(self, ok):
		self.send_acq_message(message_type=self.acq_message_type.CONTROL_SESSION, status=ok)

	# ACQ RECV

	def handle_acq_msg(self, obj):
		'''Redirects messages to the right handler'''
		if obj.message_type == self.acq_message_type.PROGRAM_STATE:
			return self.handle_acq_program_state(obj)
		if mtype == self.acq_message_type.FEAR_EVENT:
			return self.handler_acq_fear_event(obj)
		raise NotImplementedError(obj)

	def handle_acq_program_state(self, obj):
		if obj.status:
			return self.send_acq_control_session(True)
		return self.stop()

	def handler_acq_fear_event(self, obj):
		# TODO real computation
		value = obj.fear_accuracy / 2
		if not obj.status_fear:
			value *= -1
		value /= 10
		self.fears[self.fear] = min(max(self.fears[self.fear] + value, 0.0), 1.0)
		# TODO plot

def create():
	return Generation()
