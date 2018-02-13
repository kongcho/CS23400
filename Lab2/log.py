#!/usr/bin/env python
import ast
import pprint
import matplotlib.pyplot as plt
import numpy as np
import math

def get_speed_2d(times, xs, ys):
    vs = []
    for i in range(len(times) - 1):
        d = math.sqrt((xs[i+1]-xs[i])**2 + (ys[i+1]-ys[i])**2)
        t = times[i+1]-times[i]
        vs.append(d/t)
    return np.average(vs)

def get_speed_1d(times, xs):
    vs = []
    for i in range(len(times) - 1):
        d = abs(xs[i+1]-xs[i])
        t = times[i+1]-times[i]
        vs.append(d/t)
    return np.average(vs)

class Mac:
    vals = ["ds", "xs", "ys", "logds", "logxs", "logys"]

    def __init__(self, mac, logs):
        self.dic = {}
#        d0s = []
        xs = []
        ys = []
        ds = []
        rsses = []
        logds = []
        logxs = []
        logys = []
        for logg in logs:
            for i in range(len(logg.log["mac"])):
                if mac == logg.log["mac"][i]:
                    rsses.append(int(logg.log["rss"][i]))
 #                   d0s.append(log.d0)
                    ds.append(logg.ds[i])
                    xs.append(logg.xs[i])
                    ys.append(logg.ys[i])
                    if i == 0:
                        logds.append(0)
                        logxs.append(0)
                        logys.append(0)
                    else:
                        logds.append(math.log(logg.ds[i]))
                        logxs.append(math.log(logg.xs[i]))
                        logys.append(math.log(logg.ys[i]))
        self.mac = mac
#        self.dic["d0s"] = d0s
        self.dic["ds"] = ds
        self.dic["xs"] = xs
        self.dic["ys"] = ys
        self.dic["logds"] = logds
        self.dic["logxs"] = logxs
        self.dic["logys"] = logys
        self.dic["rsses"] = rsses

    def showPlot(self):
        i=1
        plt.figure(1).set_size_inches(24,48)
        for ylabel in vals:
            m = self.dic[ylabel]
            plt.subplot(len(vals),1,i)
            i += 1
            plt.scatter(self.dic["rsses"],m,c='r',label=ylabel)
            plt.xlabel('RSS')
            plt.title("magnitude for %s" % ylabel)
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

        self.spd = get_speed_2d(self.log["times"], self.log["loc_x"], self.log["loc_y"])
        self.ds = [self.spd * t for t in self.log["times"]]
        self.d0 = self.ds[0]

        self.spdx = get_speed_1d(self.log["times"], self.log["loc_x"])
        self.spdy = get_speed_1d(self.log["times"], self.log["loc_y"])
        self.xs = [self.spdx * t for t in self.log["times"]]
        self.ys = [self.spdy * t for t in self.log["times"]]


if __name__ == '__main__':
    pass
