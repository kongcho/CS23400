#!/usr/bin/env python
import ast
import pprint
import matplotlib.pyplot as plt
import numpy as np
import math

def get_distance(x1, x0, y1, y0):
    """
    Get Euclidean distance between two points
    input:
    x0 (float): first x coordinate
    x1 (float): second x coordinate
    y0 (float): first y coordinate
    y1 (float): second y coordinate
    return (float):
    the Euclidean distance
    """
    return np.sqrt((x1 - x0)**2 + (y1 - y0)**2)

def process_times(t0, times):
    new_ts = []
    for i in range(len(times)):
        new_ts.append(times[i] - t0)
    return new_ts

# We ended up not using this method to get absolute distance
#   because it was less accurate than average speed * time
def get_abs_d_1d(times, xs):
    """
    get absolute distance in one dimension by computing average speed
      for each path section and multiplying the change in time, and adding
      the distance so far
    inputs:
    times (float): time since the log began
    xs (float): x values
    return (float): absolute distance
    """
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
            some_abs_ds = [last_d + vavg * t for t in process_times(times[min_i], times[min_i:i])]
            all_abs_ds += some_abs_ds
            last_d = some_abs_ds[-1]
            v0 = v
            some_vs = [v0]
            min_i = i
    return all_abs_ds

def get_speed_1d(times, xs):
    """
    get speed in one dimension
    inputs:
    times (float): time since the log began
    xs (float): position values
    return (float): average speed
    """
    vs = []
    for i in range(len(times) - 1):
        d = abs(xs[i+1]-xs[i])
        t = times[i+1]-times[i]
        vs.append(d/t)
    return np.average(vs)

class Mac:
    """
    contains information for one trace and a given mac address
    """
    vals = ["ds", "xs", "ys"]

    def __init__(self, mac, logs):
        """
        Mac constructor
        input:
        mac (string): the mac address
        logs (list of log objects): logs for this mac address
        result:
        self.dic: dictionary of arrays from the log values
            aggregated from the input logs
        """
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
    """
    contains information from a log constructed from raw data
    """
    measurements = ["loc_x", "loc_y", "rss", "mac"]

    def __init__(self, rawdata):
        """
        Constructor for log object
        input:
        rawdata (json): the raw data collected from the log
        result:
        self.log (dictionary of arrays)
            times (list of floats): seconds since beginning the log 
            measurements (list of floats): value logged 
            - loc_x, loc_y, rss, mac
        self.spdx (float): speed calculation for x
        self.spdy (float): speed calculation for y
        self.xs (float): x distance so far at each time step
        self.ys (float): y distance so far at each time step
        """
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

        # We currently use the average speed for every consecutive points
        #   because it ended up being the most accurate
        self.spdx = get_speed_1d(self.log["times"], self.log["loc_x"])
        self.spdy = get_speed_1d(self.log["times"], self.log["loc_y"])
        self.xs = [self.spdx * t for t in self.log["times"]]
        self.ys = [self.spdy * t for t in self.log["times"]]
