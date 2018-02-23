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

    def getPeakIndexes(self, ylabel):
        ys = np.array(self.__dict__[ylabel])
        ys = savgol_filter(ys, 41, 12)
        indexes = peakutils.indexes(ys, thres=0.8)
        return indexes        

    def findImpulse(self):
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        ylabel = "mags"
        ys = np.array(self.__dict__[ylabel])
        indexes = self.getPeakIndexes(ylabel)
        pplot(xs,ys,indexes)
        plt.title("%s %s for %s" % (self.measType, ylabel, self.filename))
        plt.show()

    def removeClosePeaks(self, idxs, ylabel, minDipHeight):
        if len(idxs) in [0,1]:
            return idxs
        
        ys = self.__dict__[ylabel]
        peaksWithDips = [idxs[0]]
        
        for i in range(1, len(idxs)):
            for j in range(idxs[i-1], idxs[i]):
                if ys[j] < minDipHeight:
                    peaksWithDips.append(idxs[i])
                    continue
        return peaksWithDips

    def getSingularPeaks(self, ylabel, timeInterval, minPeakHeight):
        idxs = self.getPeakIndexes(ylabel)
        ys = self.__dict__[ylabel]
        
        ## only take the peaks above a certain height
        idxs = list(filter(lambda x: ys[x] > minPeakHeight, idxs))

        ## turn peaks that don't dip in between into one peak
        idxs = self.removeClosePeaks(idxs, ylabel, minPeakHeight)

        ## only take solitary peaks
        if len(idxs) == 0:
            return []
        if len(idxs) == 1:
            return idxs
        singularPeaks = []
        numIdxs = len(idxs)
        for i in range(numIdxs):
            if i == 0:
                if self.times[idxs[i+1]] - self.times[idxs[i]] > timeInterval:
                    singularPeaks.append(idxs[i])
                continue
            elif i == numIdxs - 1:
                if self.times[idxs[i]] - self.times[idxs[i-1]] > timeInterval:
                    singularPeaks.append(idxs[i])
                continue
            elif self.times[idxs[i+1]] - self.times[idxs[i]] > timeInterval and \
             self.times[idxs[i]] - self.times[idxs[i-1]] > timeInterval:
                singularPeaks.append(idxs[i])
        return singularPeaks


    def hasPeak(self):
        return len(self.getSingularPeaks("mags",1.5,25)) > 0

    def plotSingluarPeaks(self, timeInterval, minPeakHeight):
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        ys = np.array(self.mags)
        ys = savgol_filter(ys, 41, 12)
        indexes = self.getSingularPeaks("mags", timeInterval, minPeakHeight)
        pplot(xs,ys,indexes)
        plt.title("%s %s for %s" % (self.measType, "mags", self.filename))
        plt.show()

if __name__ == '__main__':
    folder = "olddata"
    for file in os.listdir(folder):     
        print(file)
        filepath = os.path.join(folder, file)
        with open(filepath) as f:
            data = f.read().split("\n")
        accl = GyroOrAccel("Accelerometer", data, file)
        gyro = GyroOrAccel("Gyroscope", data, file)
        # accl.findImpulse()
        # accl.plotSingluarPeaks(1.5, 25)
        if accl.hasPeak():
            print("\t%s" % "Peak found!")