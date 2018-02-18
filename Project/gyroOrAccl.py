#!/usr/bin/env python3

import os
from parse import Log
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import numpy as np
import peakutils
from peakutils.plot import plot as pplot
from math import sqrt

class GyroOrAccel(object):
    measTypes = ["Gyroscope", "Accelerometer"]
    measurements = ["xs", "ys", "zs", "mags"]

    def __init__(self, measType, rawdata, filename=None):
        assert measType in self.measTypes
        if filename:
            self.filename = filename
        self.measType = measType
        log = Log(rawdata)
        data = list(filter(lambda x: x[0] == measType, log.data))
        self.times = []
        self.xs = []
        self.ys = []
        self.zs = []
        self.mags = []
        for point in data:
            self.times.append(point[1])
            dp = point[2]
            self.xs.append(dp[0])
            self.ys.append(dp[1])
            self.zs.append(dp[2])
            mag = sqrt(dp[0]**2 + dp[1]**2 + dp[2]**2)
            self.mags.append(mag)

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

    def findImpulse(self):
        i=1
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        for ylabel in self.measurements:
            plt.subplot(len(self.measurements),1,i)
            ys = np.array(self.__dict__[ylabel])
            # ys = savgol_filter(ys, 41, 12)
            indexes = peakutils.indexes(ys, thres=0.9)
            pplot(xs,ys,indexes)
            plt.title("%s for %s" % (ylabel, self.filename))
            i += 1
        plt.show()

if __name__ == '__main__':
    folder = "data"
    for file in os.listdir("data"):
        if file[0] != "_":
            continue       
        filepath = os.path.join(folder, file)
        print(file)
        with open(filepath) as f:
            data = f.read().split("\n")
        accl = GyroOrAccel("Accelerometer", data, file)
        gyro = GyroOrAccel("Gyroscope", data, file)
        accl.findImpulse()
        gyro.findImpulse()