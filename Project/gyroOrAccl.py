#!/usr/bin/env python3

import os
from parse import Log
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import numpy as np
import peakutils
from peakutils.plot import plot as pplot
from math import sqrt
from evaluate import separate_files

class GyroOrAccel(object):
    measTypes = ["Linear", "Absolute"]
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
             plt.title("%s magnitude for %s from %s" % (self.measType, ylabel, file))
             plt.grid(True)
         plt.show()

    def getPeakIndexes(self, ylabel, window_length, polyorder):
        ys = np.array(self.__dict__[ylabel])
        ys = savgol_filter(ys, window_length, polyorder)
        indexes = peakutils.indexes(ys, thres=0.8)
        return indexes

    def findImpulse(self, window_length=41, polyorder=12):
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        ylabel = "mags"
        ys = np.array(self.__dict__[ylabel])
        indexes = self.getPeakIndexes(ylabel, window_length, polyorder)
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

    def getSingularPeaks(self, ylabel, timeInterval, minPeakHeight, window_length=41, polyorder=12):
        idxs = self.getPeakIndexes(ylabel, window_length, polyorder)
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


    def hasPeak(self, timeInterval=1.5, minPeakHeight=25):
        return len(self.getSingularPeaks("mags",timeInterval,minPeakHeight)) > 0

    def hasMultiplePeaks(self, timeInterval=1.5, minPeakHeight=25):
        return len(self.getSingularPeaks("mags",timeInterval,minPeakHeight)) > 1


    def plotSingluarPeaksMag(self, timeInterval=1.5, minPeakHeight=25, window_length=41, polyorder=12):
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        ys = np.array(self.mags)
        ys = savgol_filter(ys, window_length, polyorder)
        indexes = self.getSingularPeaks("mags", timeInterval, minPeakHeight)
        pplot(xs,ys,indexes)
        plt.title("%s %s for %s" % (self.measType, "mags", self.filename))
        plt.show()

    def plotSingluarPeaks(self, timeInterval=1.5, minPeakHeight=25, window_length=41, polyorder=12):
        i = 1
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        for ylabel in self.measurements:
            plt.subplot(len(self.measurements),1,i)
            ys = np.array(self.__dict__[ylabel])
            ys = savgol_filter(ys, window_length, polyorder)
            indexes = self.getSingularPeaks(ylabel, timeInterval, minPeakHeight)
            pplot(xs, ys, indexes)
            plt.title("%s magnitude for %s from %s" % (self.measType, ylabel, self.filename))
            i += 1
        plt.show()

if __name__ == '__main__':
    files = None
    folder = "finaldata"
    all_files = sorted(os.listdir(folder))
    categorised = separate_files(all_files, group_by=[2])
    for dic in categorised:
        if dic["label"] == "Sitting slow":
            files = dic["files"]
    if files == None:
        print("no files picked up")
    for filename in files:
        print(filename)
        filepath = os.path.join(folder, filename)
        with open(filepath) as f:
            data = f.read().split("\n")
        accl = GyroOrAccel("Linear", data, filename)
        abso = GyroOrAccel("Absolute", data, filename)
        accl.plotSingluarPeaks()
        abso.plotSingluarPeaks()
        if accl.hasPeak():
            print("\t%s" % "Peak found!")
