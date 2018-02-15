#!/usr/bin/env python
import ast
import pprint
import matplotlib.pyplot as plt
import numpy as np
import math

def get_distance(x1, x0, y1, y0):
    return np.sqrt((x1 - x0)**2 + (y1 - y0)**2)

def process_times(t0, times):
    new_ts = []
    for i in range(len(times)):
        new_ts.append(times[i] - t0)
    return new_ts

def get_abs_d_1d(times, xs):
    min_i = 0
    length = len(times) - 1
    some_vs = []
    some_abs_ds = []
    all_abs_ds = []
    last_d = 0
    v0 = abs(xs[1] - xs[0])/(times[1] - times[0])
    for i in range(length):
        d = abs(xs[i+1] - xs[i])
        t = abs(times[i+1] - times[i])
        v = d/t
        if (i + 1) == length:
            vavg = np.average(some_vs)
            some_abs_ds = [last_d + vavg * t for t in process_times(times[min_i], times[min_i:])]
            all_abs_ds += some_abs_ds
        elif (v0 - 0.005) <= v <= (v0 + 0.005):
            some_vs.append(v)
        else:
            vavg = np.average(some_vs)
            diff_vs.append((i, vavg))
            some_abs_ds = [last_d + vavg * t for t in process_times(times[min_i], times[min_i:i])]
            all_abs_ds += some_abs_ds
            last_d = some_abs_ds[-1]
            v0 = v
            some_vs = [v0]
            min_i = i
    return all_abs_ds

def get_speed_2d(times, xs, ys):
    vs = []
    for i in range(len(times) - 1):
        d = get_distance(xs[i+1], xs[i], ys[i+1], ys[i])
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
    vals = ["ds", "xs", "ys"]

    def __init__(self, mac, logs):
        self.dic = {}
        xs = []
        ys = []
        rsses = []
        for logg in logs:
            for i in range(len(logg.xs)):
                if mac == logg.log["mac"][i]:
                    rsses.append(int(logg.log["rss"][i]))
                    xs.append(logg.xs[i])
                    ys.append(logg.ys[i])
        self.mac = mac
        self.dic["xs"] = np.asarray(xs)
        self.dic["ys"] = np.asarray(ys)
        self.dic["rsses"] = np.asarray(rsses)

    def showPlot(self):
        i=1
        plt.figure(1).set_size_inches(24,48)
        for ylabel in self.vals:
            m = self.dic[ylabel]
            plt.subplot(len(self.vals),1,i)
            i += 1
            plt.scatter(self.dic["rsses"],m,c='r',label=ylabel)
            plt.xlabel('RSS')
            plt.title("magnitude for %s" % ylabel)
            plt.grid(True)
            plt.yticks([])
        plt.tight_layout()
        plt.show()

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

        self.spdx = get_speed_1d(self.log["times"], self.log["loc_x"])
        self.spdy = get_speed_1d(self.log["times"], self.log["loc_y"])
        self.xs = [self.spdx * t for t in self.log["times"]]
        self.ys = [self.spdy * t for t in self.log["times"]]
