import time
import pyqtgraph
import status_ui
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore

class TimeAxis(pyqtgraph.AxisItem):
	def tickStrings(self, values, *args):
		return [datetime.fromtimestamp(value).strftime('%H:%M:%S') for value in values]

class StatusWindow(QtWidgets.QMainWindow):

	def __init__(self, start_callback, stop_callback):
		super().__init__()
		status_ui.Ui_MainWindow().setupUi(self)
		self.setFixedSize(self.size())

		# Callbacks
		self.start_button = self.findChild(QtWidgets.QPushButton, 'Start')
		self.stop_button = self.findChild(QtWidgets.QPushButton, 'Stop')
		self.start_button.clicked.connect(start_callback)
		self.stop_button.clicked.connect(stop_callback)

		# ColorMap
		colors = [(0, 255, 0), (255, 255, 0), (255, 0, 0)]
		nb_colors = len(colors)
		pos = [i / (nb_colors - 1) for i in range(nb_colors)]
		self.colormap = pyqtgraph.ColorMap(pos, colors)

		# Progress Bars
		self.fears = {i.objectName(): i for i in self.findChildren(QtWidgets.QProgressBar)}

		# Preview
		self.preview = self.findChild(QtWidgets.QLabel, 'Preview')
		geometry = self.preview.geometry()
		self.preview_width = geometry.width()
		self.preview_height = geometry.height()
		self.previewPixmap = QtGui.QPixmap()

		# Graph
		self.plot = pyqtgraph.PlotWidget(background='#111111', axisItems={'bottom': TimeAxis(orientation='bottom')})
		self.findChild(QtWidgets.QVBoxLayout, 'GraphLayout').addWidget(self.plot)
		self.plot.hideAxis('left')
		self.plot.setMouseEnabled(y=False)
		self.y_delta = 0.3
		y_range = 1 + self.y_delta
		self.plot_x_minrange = 100
		self.plot_x_maxrange = 1000
		self.plot.setLimits(
			yMin = 0,
			yMax = 1 + self.y_delta,
			xMin = 0,
			xMax = self.plot_x_minrange,
			minYRange = y_range,
			maxYRange = y_range,
			minXRange = self.plot_x_minrange,
			maxXRange = self.plot_x_maxrange,
		)
		self.resetPlot()

		# Refresh
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self._refreshPlot)
		self.timer.start(1000)

	def updatePreview(self, value):
		self.previewPixmap.loadFromData(value)
		self.preview.setPixmap(self.previewPixmap.scaled(self.preview_width, self.preview_height, QtCore.Qt.KeepAspectRatio))

	def updateFear(self, name, value):
		self.fears[name].setValue(int(100 * value))

	def initSession(self):
		self.start_button.setEnabled(True)

	def startSession(self):
		self.start_button.setEnabled(False)
		self.stop_button.setEnabled(True)

	def stopSession(self):
		self.resetPlot()
		for bar in self.fears.values():
			bar.setValue(0)
		self.preview.clear()
		self.start_button.setEnabled(True)
		self.stop_button.setEnabled(False)

	def resetPlot(self):
		self.plot.clear()
		self.plot_x = []
		self.plot_y = []
		self.plot_text_items = []

	def plotText(self, x, text):
		item = pyqtgraph.TextItem(html=f'<div style="text-align: center;color: #FFFFFF;font-size: 16pt;">{text}</div>', anchor=(0, 0), border='w')
		item.setPos(x, 1 + self.y_delta)
		self.plot_text_items.append(item)
		self.plot_text_items.append(pyqtgraph.InfiniteLine(pos=(x, 0), angle=90))

	def plotXY(self, x, y):
		assert not self.plot_x or self.plot_x[-1] <= x
		self.plot_x.append(x)
		self.plot_y.append(y)

	def _refreshPlot(self):

		if not self.plot_x:
			return

		# Copy to prevent external update
		x = list(self.plot_x)
		y = list(self.plot_y[:len(x)])

		# Biofeedbacks
		xmin = x[0]
		xmax = x[-1]
		miss = xmin + self.plot_x_minrange - xmax
		if miss > 0:
			xmax += miss
		self.plot.setLimits(xMin=xmin, xMax=xmax)
		self.plot.clear()
		brushes = [pyqtgraph.mkBrush(c) for c in self.colormap.map(y)]
		self.plot.plot(x, y, symbolBrush=brushes)

		# Rooms
		for item in self.plot_text_items:
			self.plot.addItem(item)

def quit_app():
	QtWidgets.QApplication.quit()

def create_app(*args, **kwargs):
	app = QtWidgets.QApplication(*args, **kwargs)
	QtGui.QFontDatabase.addApplicationFont(':font/gorestep.ttf')
	return app.exec_