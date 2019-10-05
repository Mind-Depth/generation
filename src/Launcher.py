import UI
import sys
import Generation
import ExceptionHook

class Launcher:

	def __init__(self, *a, **kw):
		self.app = UI.create_app(sys.argv)
		self.gen = Generation.Generation(*a, **kw)
		self.window = None
		ExceptionHook.add_after(self._error_handler)

	def exec(self):
		self._replace_window(UI.StatusWindow(self.gen.start_game, self.gen.stop_game))
		self.gen.start(thread=True)
		ecode = self.app()
		self._stop()
		return ecode

	def _close_window(self):
		if self.window is not None:
			self.window.close()

	def _replace_window(self, window):
		self._close_window()
		self.window = window
		self.window.show()

	def _stop(self):
		self._close_window()
		self.gen.stop()
		# TODO close env & acq

	def _error_handler(self, *exception):
		# TODO better handling
		self._stop()

if __name__ == '__main__':
	sys.exit(Launcher(use_acq = '--no-acq' not in sys.argv, use_env = '--no-env' not in sys.argv).exec())