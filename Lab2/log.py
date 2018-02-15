#!/usr/bin/env python
import ast
import pprint
import matplotlib.pyplot as plt
import numpy as np
import math

def get_distance(x1, x0, y1, y0):
    return np.sqrt((x1 - x0)**2 + (y1 - y0)**2)

def get_abs_d_2d(times, xs, ys):
    min_i = 0
    length = len(times) - 1
    some_vs = []
    some_abs_ds = []
    all_abs_ds = []
    diff_vs = []
    v0 = get_distance(xs[1], xs[0], ys[1], ys[0])/(times[1] - times[0])
    for i in range(length):
        d = get_distance(xs[i+1], xs[i], ys[i+1], ys[i])
        t = abs(times[i+1] - times[i])
        v = d/t
        if i+1 == length:
            vavg = np.average(some_vs)
            # print(v0)
            # print(vavg)
            # print(v)
            diff_vs.append((i, vavg))
            some_abs_ds = [vavg * t for t in times[min_i:]]
            all_abs_ds += some_abs_ds
            continue
        if (v0 - 0.005) <= v <= (v0 + 0.005):
            some_vs.append(v)
        else:
            vavg = np.average(some_vs)
            # print(v0)
            # print(vavg)
            # print(v)
            diff_vs.append((i, vavg))
            some_abs_ds = [vavg * t for t in times[min_i:i]]
            all_abs_ds += some_abs_ds
            v0 = v
            some_vs = [v0]
            min_i = i
    print(diff_vs)
    return all_abs_ds

def get_abs_d_1d(times, xs):
    min_i = 0
    length = len(times) - 1
    some_vs = []
    some_abs_ds = []
    all_abs_ds = []
    diff_vs = []
    v0 = abs(xs[1] - xs[0])/(times[1] - times[0])
    for i in range(length):
        d = abs(xs[i+1] - xs[i])
        t = abs(times[i+1] - times[i])
        v = d/t
        if (i + 1) == length:
            vavg = np.average(some_vs)
            # print(i)
            # print(v0)
            # print(vavg)
            # print(v)
            diff_vs.append((i, vavg))
            some_abs_ds = [vavg * t for t in times[min_i:]]
            all_abs_ds += some_abs_ds
        elif (v0 - 0.005) <= v <= (v0 + 0.005):
            some_vs.append(v)
        else:
            vavg = np.average(some_vs)
            # print(i)
            # print(v0)
            # print(vavg)
            # print(v)
            diff_vs.append((i, vavg))
            some_abs_ds = [vavg * t for t in times[min_i:i]]
            all_abs_ds += some_abs_ds
            v0 = v
            some_vs = [v0]
            min_i = i
    print(diff_vs)
    return all_abs_ds

def get_speed_2d(times, xs, ys):
    vs = []
    for i in range(len(times) - 1):
        d = get_distance(xs[i+1], xs[i], ys[i+1], ys[i])
        t = times[i+1]-times[i]
        vs.append(d/t)
    return np.average(vs) # vs[10]

def get_speed_1d(times, xs):
    vs = []
    for i in range(len(times) - 1):
        d = abs(xs[i+1]-xs[i])
        t = times[i+1]-times[i]
        vs.append(d/t)
    return np.average(vs) #vs[15]

class Mac:
    vals = ["ds", "xs", "ys"]

    def __init__(self, mac, logs):
        self.dic = {}
        xs = []
        ys = []
        ds = []
        rsses = []
        for logg in logs:
            for i in range(len(logg.log["mac"])):
                if mac == logg.log["mac"][i]:
                    rsses.append(int(logg.log["rss"][i]))
                    ds.append(logg.ds[i])
                    xs.append(logg.xs[i])
                    ys.append(logg.ys[i])
        self.mac = mac
        self.dic["ds"] = np.asarray(ds)
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
        self.spdx = get_speed_1d(self.log["times"], self.log["loc_x"])
        self.spdy = get_speed_1d(self.log["times"], self.log["loc_y"])
        # self.spdx = abs(self.log["loc_x"][-1] - self.log["loc_x"][0])/abs(self.log["times"][-1] - self.log["times"][0])
        # self.spdy = abs(self.log["loc_y"][-1] - self.log["loc_y"][0])/abs(self.log["times"][-1] - self.log["times"][0])
        self.ds = [self.spd * t for t in self.log["times"]]
        self.xs = [self.spdx * t for t in self.log["times"]]
        self.ys = [self.spdy * t for t in self.log["times"]]
        # print(self.ds[0:10] + self.ds[-5:-1])
        # print(self.xs[0:15] + self.ds[-5:-1])
        # print(self.ys[0:10] + self.ds[-5:-1])
        # self.ds = get_abs_d_2d(self.log["times"], self.log["loc_x"], self.log["loc_y"])
        # self.xs = get_abs_d_1d(self.log["times"], self.log["loc_x"])
        # self.ys = get_abs_d_1d(self.log["times"], self.log["loc_y"])
        # print(self.ds[0:10] + self.ds[-5:-1])
        # print(self.xs[0:15] + self.ds[-5:-1])
        # print(self.ys[0:10] + self.ds[-5:-1])
        # self.xs = [0.0 * t for t in self.log["times"][:3818]] + \
        #           [0.275123503584 * t for t in self.log["times"][3818:11964]] + \
        #           [0.508998360497 * t for t in self.log["times"][8624:]]
        # print("### END")

if __name__ == '__main__':
    pass
