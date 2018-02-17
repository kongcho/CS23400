#!/usr/bin/env python3

import os
from parse import Log
import matplotlib.pyplot as plt

class GyroOrAccel(object):
	measTypes = ["Gyroscope", "Accelerometer"]
	measurements = ["xs", "ys", "zs"]

	def __init__(self, measType, rawdata):
		assert measType in self.measTypes
		self.measType = measType
		log = Log(rawdata)
		data = list(filter(lambda x: x[0] == measType, log.data))
		self.times = []
		self.xs = []
		self.ys = []
		self.zs = []
		for point in data:
			self.times.append(point[1])
			dataPoint = point[2]
			self.xs.append(dataPoint[0])
			self.ys.append(dataPoint[1])
			self.zs.append(dataPoint[2])

	def plot(self):
         i=1
         plt.figure(1).set_size_inches(24,48)
         for ylabel in self.measurements:
             m = self.__dict__[ylabel]
             plt.subplot(len(self.measurements),1,i)
             i += 1
             plt.plot(self.times,m,label=ylabel)
             plt.title("magnitude for %s from %s" % (ylabel, file))
             plt.grid(True)
         plt.show()

if __name__ == '__main__':
    folder = "data"
    for file in os.listdir("data"):
        filepath = os.path.join(folder, file)
        print(file)
        with open(filepath) as f:
            data = f.read().split("\n")
        gyro = GyroOrAccel("Gyroscope", data)
        gyro.plot()