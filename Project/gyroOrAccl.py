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
    measTypes = ["Linear", "Absolute"]
    measurements = ["xs", "ys", "zs", "mags", "magxy"]

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
        self.magxy = []
        for point in data:
            self.times.append(point[1])
            dp = point[2]
            self.xs.append(dp[0])
            self.ys.append(dp[1])
            self.zs.append(dp[2])
            mag = sqrt(dp[0]**2 + dp[1]**2 + dp[2]**2)
            magxy = sqrt(dp[0]**2 + dp[1]**2)
            self.magxy.append(magxy)
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

    def getPeakIndexes(self, ys, window_length, polyorder):
        ys = savgol_filter(ys, window_length, polyorder)
        indexes = peakutils.indexes(ys, thres=0.8)
        return indexes

    def findImpulse(self, window_length=41, polyorder=12):
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        ylabel = "mags"
        ys = np.array(self.__dict__[ylabel])
        indexes = self.getPeakIndexes(ys, window_length, polyorder)
        pplot(xs,ys,indexes)
        plt.title("%s %s for %s" % (self.measType, ylabel, self.filename))
        plt.show()

    def removeClosePeaks(self, idxs, ys, minDipHeight):
        if len(idxs) in [0,1]:
            return idxs
        peaksWithDips = [idxs[0]]
        for i in range(1, len(idxs)):
            for j in range(idxs[i-1], idxs[i]):
                if ys[j] < minDipHeight:
                    peaksWithDips.append(idxs[i])
                    continue
        return peaksWithDips

    def hasPeak(self, timeInterval=1.5, minPeakHeight=25, window_length=41, polyorder=12):
        ys = self.__dict__["mags"]
        return len(self.getSingularPeaks(ys,timeInterval,minPeakHeight, window_length, polyorder)) > 0

    def hasMultiplePeaks(self, timeInterval=1.5, minPeakHeight=25, window_length=41, polyorder=12):
        ys = self.__dict__["mags"]
        return len(self.getSingularPeaks(ys,timeInterval,minPeakHeight, window_length, polyorder)) > 1

    def getSingularPeaks(self, ys, timeInterval=1.5, minPeakHeight=25, window_length=41, polyorder=12):
        idxs = self.getPeakIndexes(ys, window_length=window_length, polyorder=polyorder)

        ## only take the peaks above a certain height
        idxs = list(filter(lambda x: ys[x] > minPeakHeight, idxs))

        ## turn peaks that don't dip in between into one peak
        idxs = self.removeClosePeaks(idxs, ys, minPeakHeight)

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

    def down_and_up(self, ylabel, peaks_pos, timeInterval=1.5, minNegPeakHeight=1, window_length=41, polyorder=12):
        final_indexes = []
        ys_neg = np.negative(np.array(self.__dict__[ylabel]))
        peaks_neg = self.getSingularPeaks(ys_neg, timeInterval, minNegPeakHeight, window_length, polyorder)
        if len(peaks_neg) == 0:
            return []
        for peak_neg in peaks_neg:
            for peak_pos in peaks_pos:
                if peak_neg < peak_pos:
                    final_indexes.append(peak_pos)
        return final_indexes

    def is_fall(self, extra=[True, True], timeInterval=1.5, negPeakHeight=1, minPeakHeight=25, window_length=41, polyorder=12):
        ys = self.__dict__["mags"]
        indexes = self.getSingularPeaks(ys, timeInterval, minPeakHeight, window_length, polyorder)
        if len(indexes) == 0:
            return indexes
        if extra[0]:
            for i, index in enumerate(indexes):
                if (self.__dict__["magxy"])[index] < abs((self.__dict__["zs"])[index]):
                    indexes.pop(i)
                else:
                    continue
        if extra[1]:
            indexes = self.down_and_up("zs", indexes, timeInterval, negPeakHeight, window_length, polyorder)
        return indexes

    def plotSingluarPeaksMag(self, timeInterval=1.5, minPeakHeight=25, window_length=41, polyorder=12):
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        ys = np.array(self.mags)
        ys = savgol_filter(ys, window_length=window_length, polyorder=polyorder)
        ys = np.array(self.__dict__["mags"])
        indexes = self.getSingularPeaks(ys, timeInterval, minPeakHeight)
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
            ys = savgol_filter(ys, window_length=window_length, polyorder=polyorder)
            indexes = self.getSingularPeaks(ys, timeInterval, minPeakHeight)
            pplot(xs, ys, indexes)
            plt.title("%s magnitude for %s from %s" % (self.measType, ylabel, self.filename))
            i += 1
        plt.show()

if __name__ == '__main__':
    pass