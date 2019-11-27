#
import time
import queue
import base64
import random
from UI import quit_app
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
		Configuration.remove_generated()
		self.reverse_env_enums = AttrDict()
		self.ui = None
		self.reset()
		super().__init__(*self.clients)

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.stop()

	# CONNECTION GROUP

	def _start(self, ui):
		self.ui = ui
		if self.use_acq:
			self.send_acq_initialize()
		if self.use_env:
			self.send_env_initialize()

	def _stop(self):
		if self.use_env:
			try:
				self.send_env_terminate()
			except Exception:
				pass
		Configuration.remove_generated()
		if self.ui:
			quit_app()

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
		self.fear_level = 0
		self.paused = True
		self.fear = None

	def start_game(self):
		if self.ui:
			self.ui.startSession()
		if self.use_acq:
			self.send_acq_control_session(True)
		if self.use_env:
			self.fears = {fear: -1 for fear in self.env_enums.Fears.values()}
			self.send_env_start()
		self.paused = False

	def stop_game(self):
		if self.ui:
			self.ui.stopSession()
		if self.use_acq:
			self.send_acq_control_session(False)
		if self.use_env:
			self.send_env_quit()
		self.reset()

	def handle_background_tasks(self):

		# Start game
		if not self.disconnected_clients:
			self.disconnected_clients -= 1
			if self.ui:
				self.ui.initSession()

		if self.paused:
			return

		# Update fear level
		if self.afraid and self.fear is not None:
			# TODO real computation
			value = min(max(self.fears[self.fear] + 0.05, 0.0), 1.0)
			self.fears[self.fear] = value
			if self.ui:
				self.ui.updateFear(self.reverse_env_enums.Fears[self.fear], value)

		if self.ui:
			self.ui.plotXY(time.time(), self.fear_level)

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
		if obj.type == self.env_enums.EnvironmentMessageType.ScreenShotStart:
			return self.handle_env_screen_shot_start()
		if obj.type == self.env_enums.EnvironmentMessageType.ScreenShotChunk:
			return self.handle_env_screen_shot_chunk(obj.message)
		if obj.type == self.env_enums.EnvironmentMessageType.ScreenShotEnd:
			return self.handle_env_screen_shot_end()
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
				random.choice(filtered_models[category_config.type] or self.models[category_config.type]) # TODO handle empty list in another way
				for category_config in m.categories_config
				for _ in range(random.randint(category_config.use_min, category_config.use_max))
		]

		# TODO clean
		value *= value > 0
		self.fears[fear] = value
		self.fear = fear
		self.ui.plotText(time.time(), self.reverse_env_enums.Fears[self.fear])
		self.send_env_room(m, models, [], fear, value)

	def handle_env_screen_shot_start(self):
		self.screen_shot_chunks = ''

	def handle_env_screen_shot_chunk(self, chunk):
		self.screen_shot_chunks += chunk

	def handle_env_screen_shot_end(self):
		if self.ui:
			self.ui.updatePreview(base64.b64decode(self.screen_shot_chunks))

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
		# obj.status_fear
		# obj.timestamp # TODO handle older timestamp
		self.afraid = obj.status_fear
		self.fear_level = int(self.afraid)
