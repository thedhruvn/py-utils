import time, logging
from util.ColorLogBase import ColorLogBase
from statistics import mean


class MovingAverageNumber(ColorLogBase):

	def __init__(self, window=24, seed=0):
		super().__init__()
		self.buffer = []
		self.window = window
		self.seed = seed
		self.threshold = 0.5
		self.__initialize_buffer()


		
	def __initialize_buffer(self):
		for i in range(0, self.window):
			self.buffer.append(self.seed)

	def update_window(self, new_window):
		self.window = new_window
		self.__initialize_buffer()

	def update_seed(self, new_seed):
		self.seed = new_seed
		self.__initialize_buffer()

	def update_threshold(self, new_threshold):
		self.threshold = new_threshold

	def add(self, value):
		"""
		New values always added to the last index in buffer
		"""
		self.buffer = self.buffer[1:] + [value]

	def get_avg(self, rounding=None):
		mn = mean(self.buffer)
		if rounding:
			return round(mn, rounding)
		else:
			return mn

	def get_average(self, rounding=None):
		return self.get_avg(rounding)

	def get_bool_average(self, threshold=self.threshold, rounding=None):
		"""
		If Moving Average >= threshold, return True
		"""
		return self.get_avg(rounding) >= threshold
