#!/usr/bin/env python

from parse import parseFolder
from log import Log
from mac import Mac
import scipy.optimize
import matplotlib.pyplot as plt
import numpy as np

macs = ["8c:85:90:16:0a:a4", "ac:9e:17:7d:31:e8", "d8:c4:6a:50:e3:b1", "f8:cf:c5:97:e0:9e"]
# 8c:85:90:16:0a:a4 (location: x=6.8, y=6.8), ac:9e:17:7d:31:e8 (location: x=-0.87, y=9.45)
# P = C - glog(d)

def get_macs(folder):
    logs = parseFolder(folder)
    data = []
    for mac in macs:
        data.append(Mac(mac, logs))
    return data

def linear_func(x, m, c):
    return m*np.asarray(x) + c

def least_sq(mac):
    xs = mac.logxs
    ys = mac.rsses
    for i in range(1):
        plt.scatter(xs, ys, c='r')
    popt, pcov = scipy.optimize.curve_fit(linear_func, xs, ys)
#    plt.plot(xs, ys, 'b-')q
#    plt.plot(xs, linear_func(xs, popt[0].item(), popt[1].item()), 'r-')
    plt.show()
    return popt

if __name__ == '__main__':
    macs = get_macs("./data")
    for mac in macs:
        print(least_sq(mac))
