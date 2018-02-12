#!/usr/bin/env python
import ast
import pprint
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt

def get_speed(times, xs, ys):
    vs = []
    for i in range(len(times) - 1):
        d = sqrt((xs[i+1]-xs[i])**2 + (ys[i+1]-ys[i])**2)
        t = times[i+1]-times[i]
        vs.append(d/t)
    return np.average(vs)

class Mac:
    def __init__(self, mac, logs):
        self.dic = {}
#        d0s = []
        ds = []
        rsses = []
        logds = []
        for log in logs:
            for i in range(len(log.log["mac"])):
                if mac == log.log["mac"][i]:
 #                   d0s.append(log.d0)
                    ds.append(log.ds[i])
                    logds.append(math.log(log.ds[i]))
                    rsses.append(log.log["rss"][i])
        self.mac = mac
#        self.dic["d0s"] = d0s
        self.dic["logds"] = logds
        self.dic["ds"] = ds
        self.dic["rsses"] = rsses

class Log:
    measurements = ["loc_x", "loc_y", "rss", "mac"]

    def __init__(self, rawdata):
        self.log = {}

        times = []
        time0 = rawdata[0]['time']
        for dictionary in rawdata:
            times.append(dictionary['time'] - time0)
        self.log["times"] = times

        for ylabel in self.measurements:
            m = []
            for dictionary in rawdata:
                m.append(dictionary[ylabel])
            self.log[ylabel] = m

        self.spd = get_speed(self.log["times"], self.log["loc_x"], self.log["loc_y"])

        self.ds = [self.spd * t for t in self.log["times"]]

        self.d0 = self.ds[0]

    def showPlot(self):
        i=1
        plt.figure(1).set_size_inches(24,48)
        for ylabel in self.measurements:
            m = self.__dict__[ylabel]
            plt.subplot(len(self.measurements),2,i)
            i += 1
            plt.plot(self.__dict__["times"],m,label=ylabel)
            plt.xlabel('Time (s)')
            plt.title("magnitude for %s %s" % (self.type, ylabel))
            plt.grid(True)
            plt.yticks([])
        plt.tight_layout()
        plt.show()

    def getMeasurementInfo(self, ylabel):
        ## TODO: you may want to add to/modify this
        return []

    def getAllMeasurements(self):
        ## TODO: you may want to modify this
        ret = []
        for ylabel in self.measurements:
            ret += self.getMeasurementInfo(ylabel)
        return ret

if __name__ == '__main__':
    pass
