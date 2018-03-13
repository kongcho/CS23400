#!/usr/bin/env python3

import os
from parse import Log
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import numpy as np
import peakutils
from peakutils.plot import plot as pplot
from math import sqrt
import ast

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

    def getPeakIndexes(self, ys, window_length, polyorder, thres=0.8):
        ys = savgol_filter(ys, window_length, polyorder)
        indexes = peakutils.indexes(ys, thres)
        return indexes

    def findImpulse(self, window_length=41, polyorder=12, thres=0.8):
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        ylabel = "mags"
        ys = np.array(self.__dict__[ylabel])
        indexes = self.getPeakIndexes(ys, window_length, polyorder, thres)
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

    def getSingularPeaks(self, ys, timeInterval=1.5, minPeakHeight=25, window_length=41, polyorder=12, thres=0.8):
        idxs = self.getPeakIndexes(ys, window_length=window_length, polyorder=polyorder, thres=thres)

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

    def down_and_up(self, ylabel, peaks_pos, timeInterval=1.5, minNegPeakHeight=1, window_length=41, polyorder=12, thres=0.5):
        final_indexes = []
        ys_pos = np.array(self.__dict__[ylabel])
        ys_neg = np.negative(ys_pos)
        peaks_posi = self.getPeakIndexes(ys_pos, window_length=window_length, polyorder=polyorder, thres=thres)
        peaks_neg = self.getPeakIndexes(ys_neg, window_length=window_length, polyorder=polyorder, thres=thres)
        # print("posi")
        # print(peaks_posi)
        # print("neg")
        # print(peaks_neg)
        # print("pos")
        # print(peaks_pos)
        if len(peaks_neg) == 0:
            return []
        for peak_neg in peaks_neg:
            if ys_neg[peak_neg] < minNegPeakHeight:
                continue
            for i, peak_pos in enumerate(peaks_pos):
                diff = peak_pos - peak_neg
                if diff >= 0 and diff <= 3:
                    final_indexes.append(peak_pos)
        # print("pos")
        # print(peaks_pos)
        # print("neg")
        # print(peaks_neg)
        return final_indexes

    def is_fall(self, extra=[False, True], timeInterval=1.5, timeIntNeg=0.01, negPeakHeight=5, minPeakHeight=16, window_length=41, polyorder=12, thres=0.5):
        ys = self.__dict__["mags"]
        indexes = self.getPeakIndexes(ys, window_length=window_length, polyorder=polyorder, thres=0.8)
#        indexes = self.getSingularPeaks(ys, timeInterval, minPeakHeight, window_length, polyorder)
        if len(indexes) == 0:
            return indexes
        for index in indexes:
            if ys[index] < minPeakHeight:
                np.delete(indexes, [index])
        if extra[0]:
            for i, index in enumerate(indexes):
                if (self.__dict__["magxy"])[index] < abs((self.__dict__["zs"])[index]):
                    indexes = np.delete(indexes, [i])
                else:
                    continue
        if extra[1]:
            indexes = self.down_and_up("zs", indexes, timeIntNeg, negPeakHeight, window_length, polyorder, thres)
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

    def plotFinalAlgoPeaks(self, extra=[False, True], timeInterval=1.5, timeIntNeg=0.01, negPeakHeight=5, minPeakHeight=16, window_length=41, polyorder=12, thres=0.5):
        i = 1
        plt.figure(1).set_size_inches(24,48)
        xs = np.array(self.times)
        for ylabel in self.measurements:
            plt.subplot(len(self.measurements),1,i)
            ys = np.array(self.__dict__[ylabel])
            ys = savgol_filter(ys, 41, 12)
            indexes = self.is_fall(extra, timeInterval, timeIntNeg, negPeakHeight, minPeakHeight, window_length, polyorder, thres)
            pplot(xs, ys, indexes)
            plt.title("%s magnitude for %s from %s" % (self.measType, ylabel, self.filename))
            i += 1
        plt.show()
        plt.gcf().clear()

if __name__ == '__main__':
    # folder = "./finaldata/"
    # files = sorted(os.listdir(folder))
    # for filename in files:
    #     print(filename)
    #     filepath = os.path.join(folder, filename)
    #     with open(filepath) as f:
    #         data = f.read().split("\n")
    #     abso = GyroOrAccel("Absolute", data, filename)
    #     print(abso.is_fall([False, False], 1.5, 0.01, 5, 15, 41, 12, 0.5))
        # abso.plotFinalAlgoPeaks([False, False], 1.5, 0.01, 5, 15, 41, 12, 0.5)
    filename = "fall_detection_data_0.txt"
    with open(filename, "r") as f:
        data = f.read().split("\n")
    abso = GyroOrAccel("Absolute", data, filename)
    print(abso.is_fall([False, True], 0.05, 0.01, 25, 25, 41, 12, 0.8))
    abso.plotFinalAlgoPeaks([False, True], 0.05, 0.01, 25, 25, 41, 12, 0.8)
