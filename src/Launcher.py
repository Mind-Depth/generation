import UI
import sys
import Generation

class Launcher:

	def __init__(self):
		self.app = UI.create_app(sys.argv)
		self.gen = Generation.create()
		self.window = None

	def exec(self):
		try:
			return self._run_main()
		except:
			raise
		finally:
			self._stop()

	def _replace_window(self, window):
		if self.window is not None:
			self.window.close()
		self.window = window
		self.window.show()

	def _run_main(self):
		self._replace_window(UI.LauncherWindow(start=self._run_secondary))
		self.gen.start(thread=True)
		return self.app()

	def _run_secondary(self):
		self._replace_window(UI.StatusWindow())
		# TODO launch env & acq

	def _stop(self):
		self.gen.stop()
		# TODO close env & acq

if __name__ == '__main__':
	sys.exit(Launcher().exec())