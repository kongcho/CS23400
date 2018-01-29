#!/usr/bin/env python
import ast
import pprint
import operator
import matplotlib.pyplot as plt
import numpy as np
from pylab import fft
from nfft import ndft

types = ["Driving", "Jumping", "Standing", "Walking"]
files = ["./data/activity-dataset-" + activity + ".txt" for activity in types]

class Log:
    measurements = ["xGyro","yGyro","xAccl","xMag","zAccl","yAccl","zGyro","yMag","zMag"]

    def __init__(self, rawdata):
        # if isinstance(rawdata, basestring):
        #     rawdata = ast.literal_eval(rawdata)

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


    def getFreq(self, ylabel):
        if ylabel not in self.measurements:
            return
        xs = self.times
        ys = self.__dict__[ylabel]
        x = np.array(xs)
        y = np.array(ys)
        yf = fft(y)

        ## TODO: This may not be what we want.
        return yf

    def getFreqNew(self, ylabel):
        if ylabel not in self.measurements:
            return
        xs = self.times
        ys = self.__dict__[ylabel]
        length = len(xs)//2
        if length % 2 != 0:
            length = length - 1
        amps = ndft(xs[:length], ys[:length])
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

    def findPeaks(self, ylabel):
        # returns a list of the indices of peaks
        xs = self.times
        ys = self.__dict__[ylabel]

        peaks = []

        # this doesn't really work as a peak finder 
        # need to find a better version since find_peaks_cwt is really slow
        for x in range (1, len(ys)-1):
            if (ys[x] > ys[x-1]) and (ys[x] > ys[x-1]):
                peaks.append(x)

        # this calculation takes way too long: 
        # peaks = signal.find_peaks_cwt(ys, np.arange(1, len(ys)))
        # xs = xs[1:]
        # peaks = signal.find_peaks_cwt(ys, xs)

        return peaks;

    def getNumPeaks(self, ylabel):
        # returns the number of peaks
        return len(self.findPeaks(ylabel))

    def getPeriods(self, ylabel):
        # calculate mean period by measuring distance between peaks

        xs = self.times
        peaks = self.findPeaks(ylabel)
        periods = [xs[j]-xs[i] for i, j in zip(peaks[:-1], peaks[1:])]
        return periods

    def getPeriod(self, ylabel):
        #calculate mean period using getPeriods

        periods = self.getPeriods(ylabel)
        return np.mean(periods)

    def getPeriod1(self, ylabel):
        # finds the likely period of a given measurement
        # only works if we correctly apply FFT

        # the period of a signal is 1/frequency 
        # frequency estimated by the longest wavelength of FFT

        xf, yf = self.getFreq(ylabel)

        # why would this happen?
        if np.argmax(abs(yf)) == 0:
            period = 0
        else:
            period = 1/np.argmax(abs(yf))
        return period

    def getAmplitude(self, ylabel):
        # TODO: finds average amplitude of measurement
        return 0

    def getPeriodVariance(self, ylabel):
        # likelihood that the period guess was correct
        return 0

    def getMeasurementInfo(self, ylabel):
        ## TODO: you may want to add to/modify this
        ys = self.__dict__[ylabel]
        ymax = max(ys)
        ymin = min(ys)
        yft = self.getFreqNew(ylabel)
        ftMaxIndex = np.argmax(yft)
        period = self.times[ftMaxIndex]
        if period > 15:
            period = 0.
        ftMaxVal = np.max(yft)
        return [ymax,
                ymin
#                ftMaxVal,
#                np.mean(ys),
#                np.std(ys),
#                self.getNumPeaks(ylabel),
#                self.getPeriod(ylabel),
#                self.getPeriod1(ylabel), # included both period measuments for comparison
#                self.getAmplitude(ylabel),
#                self.getPeriodVariance(ylabel)
        ]

    def getAllMeasurements(self):
        ## TODO: you may want to modify this
        ret = []
        for ylabel in self.measurements:
            ret += self.getMeasurementInfo(ylabel)
        return ret

if __name__ == '__main__':
    with open("logs/activity-team2-Driving-1.txt") as f:
        rawdata = f.read()

    log = Log(rawdata)
    for ylabel in log.measurements:
        print(ylabel)
        print(log.getMeasurementInfo(ylabel))
