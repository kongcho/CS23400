#!/usr/bin/env python
import ast
import pprint
import matplotlib.pyplot as plt
import numpy as np
import peakutils
import operator
import scipy as sp
from pylab import fft
from nfft import ndft

class Log:
    measurements = ["xGyro","yGyro","xAccl","xMag","zAccl","yAccl","zGyro","yMag","zMag"]

    def __init__(self, rawdata):
        if isinstance(rawdata, basestring):
            rawdata = ast.literal_eval(rawdata)

        self.type = rawdata['type']

        times = []
        time0 = rawdata['seq'][0]['time']
        for y in rawdata['seq']:
            times.append((y['time'] - time0))
        self.times = times

        for ylabel in self.measurements:
            m = []
            for z in rawdata['seq']:
                m.append(z['data'][ylabel])
            self.__dict__[ylabel] = m

    def __str__(self):
        ret = ""
        ret += "Type: %s\n" % (self.type)
        t = self.times
        if len(t) < 4:
            return
        ret += "Times:\n\t[%s,%s,%s,...,%s]\n" % (t[0],t[1],t[2],t[-1])
        for y in self.measurements:
            m = self.__dict__[y]
            ret += "%s:\n\t[%s,%s,%s,...,%s]\n" % (y,m[0],m[1],m[2],m[-1])
        return ret


    def getFreq(self, ys):
        if ylabel not in self.measurements:
            return
        ys = self.__dict__[ylabel]
        yf = fft(np.array(ys[:(len(ys)//2)]))

        ## TODO: This may not be what we want.
        return yf

    def getFreqNew(self, ys, times):
        length = len(times)//2
        if length % 2 != 0:
            length = length - 1
        amps = ndft(times[:length], ys[:length])
        return amps

    def showPlot(self):
        i=1
        plt.figure(1).set_size_inches(24,48)
        for ylabel in self.measurements:
            m = self.__dict__[ylabel]
            plt.subplot(len(self.measurements),2,i)
            i += 1
            plt.plot(self.times,m,label=ylabel)
            plt.xlabel('Time (s)')
            plt.title("magnitude for %s %s" % (self.type, ylabel))
            plt.grid(True)
            plt.yticks([])

            plt.subplot(len(self.measurements),2,i)
            i += 1

            xf, yf = self.getFreq(ylabel)

            plt.plot(xf, np.abs(yf))
            plt.grid()
            plt.title("freq analyisis for %s %s" % (self.type, ylabel))
            plt.yticks([])
            plt.xlabel('Time (s)')
        plt.tight_layout()
        plt.show()

    def getPeriod(self, ys, times):
        ## TODO: find the likely period of a given measurement
        yft = self.getFreqNew(ys, times)
#        ftMaxIndex = np.argmax(yft)
#        period = self.times[ftMaxIndex]
#        if period > 15:
#            period = 0.0
        ftMaxVal = np.max(yft)
        return ftMaxVal

    def getNumPeaks(self, ylabel):
        cb = np.array(self.__dict__[ylabel])
#        filtered = sp.signal.lfilter([1.0/10]*len(cb), 1, cb)
#        filtered = sp.signal.savgol_filter(cb, 201, 3)
        threshold = 0.5
        indexes = peakutils.indexes(cb, thres=threshold)
#        print(len(indexes))
        return len(indexes)

    def getAmplitude(self, ylabel):
        ## TODO: find average amplitude of measurement
        ys = self.__dict__[ylabel]
        return np.average(ys)

    def getPeriodVariance(self, ylabel):
        ## TODO: likelihood that the period guess was correct
        return 0

    def getMeasurementInfo(self, ylabel):
        ## TODO: you may want to add to/modify this
        xs = self.times
        ys = self.__dict__[ylabel]
        ymax = max(ys)
        ymin = min(ys)
        return [ymax
                , ymin
                , self.getNumPeaks(ylabel)
#                , np.std(np.std(ys))
#                , np.max(sp.signal.find_peaks_cwt(ys, range(0, 150, 20)))
#                , np.std(np.gradient(ys))
#                , self.getFreqs(ys)
#                , np.std(np.std(ys))
#                , np.std(ys)
                , self.getAmplitude(ylabel)
#                , self.getPeriod(sp.signal.lfilter([1.0/10]*len(ys), 1, ys), xs)
        ]

    def getAllMeasurements(self):
        ## TODO: you may want to modify this
        ret = []
        for ylabel in self.measurements:
            ret += self.getMeasurementInfo(ylabel)
        return ret

if __name__ == '__main__':
    pass
    with open("logs/activity-team2-Driving-1.txt") as f:
        rawdata = f.read()

    log = Log(rawdata)
    for ylabel in log.measurements:
        print(ylabel)
        print(log.getMeasurementInfo(ylabel))
