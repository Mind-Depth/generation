#
import queue
import random
from attrdict import AttrDict
from collections import defaultdict
from Connection import ConnectionGroup
from Configuration import Configuration

class Generation(ConnectionGroup):

	# CLASS

	def __init__(self, use_acq=True, use_env=True):
		self.use_acq = use_acq
		self.use_env = use_env
		self.clients = []
		if self.use_acq:
			self.clients.append(Configuration.connection.acquisition)
		if self.use_env:
			self.clients.append(Configuration.connection.environment)
		self.disconnected_clients = len(self.clients)
		self.acq_message_type = AttrDict({key: key for key in {'INIT', 'CONTROL_SESSION', 'PROGRAM_STATE', 'FEAR_EVENT'}})
		self.env_enums = AttrDict({
			'EnvironmentMessageType': { 'Terminate': 0, 'Initialize': 1 },
			'GenerationMessageType': { 'Terminate': 0, 'Initialize': 1}
		})
		self.reverse_env_enums = AttrDict()
		self.reset()
		super().__init__(*self.clients)

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.stop()

	# CONNECTION GROUP

	def _start(self):
		if self.use_acq:
			self.send_acq_initialize()
		if self.use_env:
			self.send_env_initialize()

	def _stop(self):
		for condition, callback, *args in (
			(self.use_acq, self.send_acq_control_session, False),
			(self.use_env, self.send_env_terminate),
		):
			if condition:
				try:
					callback(*args)
				except Exception:
					pass
		Configuration.remove_generated()

	def _update(self):
		try:
			who, obj = self.q.get(block=True, timeout=1)
		except queue.Empty:
			pass
		else:
			if who == Configuration.connection.environment:
				self.handle_env_msg(obj)
			elif who == Configuration.connection.acquisition:
				self.handle_acq_msg(obj)
		self.handle_background_tasks()

	# GEN WORKFLOW

	def reset(self):
		self.fears = {}
		self.afraid = False
		self.fear = None

	def start_game(self):
		# TODO grey out buttons
		if self.use_acq:
			self.send_acq_control_session(True)
		if self.use_env:
			self.fears = {fear: 0 for fear in self.env_enums.Fears.values()}
			self.send_env_start()

	def stop_game(self):
		# TODO grey out buttons
		# TODO send to ACQ
		if self.use_env:
			self.send_env_quit()
		self.reset()

	def handle_background_tasks(self):

		# Start game
		if not self.disconnected_clients:
			# TODO activate button
			self.disconnected_clients -= 1

		# Update fear level
		if self.afraid and self.fear:
			# TODO real computation
			value = min(max(self.fears[self.fear] + 0.05, 0.0), 1.0)
			self.fears[self.fear] = value
			print(self.reverse_env_enums.Fears[self.fear] + ': ' + str(value))

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

	def send_env_start(self):
		self.send_env_message(type=self.env_enums.GenerationMessageType.Start)

	def send_env_quit(self):
		self.send_env_message(type=self.env_enums.GenerationMessageType.Quit)

	def send_env_room(self, m, models, events, fear, fearIntensity):
		model_dict = defaultdict(list)
		for model in models:
			model_dict[model.type].append(model.id)
		self.send_env_message(
			type = self.env_enums.GenerationMessageType.RoomConfiguration,
			mapId = m.id,
			modelGroups = [{'type': key, 'modelIds': value} for key, value in model_dict.items()],
			eventIds = [event.id for event in events],
			fear = fear,
			fearIntensity = fearIntensity,
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
		self.disconnected_clients -= 1

	def handle_env_request_room(self):

		# TODO base decision differently
		tested = {}
		untested = {}
		for fear, value in self.fears.items():
			(untested if value == -1 else tested)[fear] = value
		fears = list((untested if untested else tested).items())
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
			kvs = [(kv['key'], kv['value']) for kv in content]
			self.env_enums[enum] = {kv[0]: kv[1] for kv in kvs}
			self.reverse_env_enums[enum] = {kv[1]: kv[0] for kv in kvs}
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
		if obj.message_type == self.acq_message_type.FEAR_EVENT:
			return self.handler_acq_fear_event(obj)
		raise NotImplementedError(obj)

	def handle_acq_program_state(self, obj):
		if obj.status:
			self.disconnected_clients -= 1
		else:
			self.stop()

	def handler_acq_fear_event(self, obj):
		# TODO real computation
		# obj.fear_accuracy
		self.afraid = obj.status_fear
		# TODO plot
