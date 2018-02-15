from parse import parseFolder, parseFile
from log import Log, Mac, get_distance
import scipy.optimize
import matplotlib.pyplot as plt
import numpy as np
import math
import os

macs = ["8c:85:90:16:0a:a4", "ac:9e:17:7d:31:e8", "d8:c4:6a:50:e3:b1", "f8:cf:c5:97:e0:9e"]
# 8c:85:90:16:0a:a4 (location: x=6.8, y=6.8)
# ac:9e:17:7d:31:e8 (location: x=-0.87, y=9.45)
# P = C - glog(d)

def get_macs(folder):
    logs = parseFolder(folder)
    data = []
    for mac in macs:
        data.append(Mac(mac, logs))
    return data

def get_macs_each(folder):
    logs = parseFolder(folder)
    data = []
    for mac in macs:
        for log in logs:
            data.append(Mac(mac, [log]))
    return data

def train_folder(folder):
    macs_data = get_macs_each(folder)
    for mac_name in macs:
        print("#### " + mac_name)
        curr_resx = []
        curr_resy = []
        errorx = []
        errory = []
        errors = []
        for mac in macs_data:
            if mac.mac == mac_name:
                mac.showPlot()
                try:
                    res = (least_sq(tx_unknown, (mac.dic["xs"], mac.dic["ys"]), mac.dic["rsses"]))
                    curr_resx.append(res[0])
                    curr_resy.append(res[1])
                    print((res[0]), (res[1]))
                    if mac.mac == "8c:85:90:16:0a:a4":
                        err = (get_distance(res[0], 6.8, res[1], 6.8))
                        errors.append(err)
                        print("error:\t" + str((res[0]-6.8, res[1]-6.8, err)))
                    elif mac.mac == "ac:9e:17:7d:31:e8":
                        err = (get_distance(res[0], -0.87, res[1], 9.45))
                        print("error:\t" + str((res[0]+0.87, res[1]-9.45, err)))
                        errors.append(err)
                except:
                    print("error")
                print("# end")
        resx = np.average(curr_resx)
        resy = np.average(curr_resy)
        print("\nRES:\t" + str((resx, resy)))
        if mac_name == "8c:85:90:16:0a:a4":
            err = (get_distance(resx, 6.8, resy, 6.8))
            print("ERRS:\t" + str((np.average(errors), err)))
        elif mac_name == "ac:9e:17:7d:31:e8":
            err = (get_distance(resx, -0.87, resy, 9.45))
            print("ERRS:\t" + str((np.average(errors), err)))
        print("------------------------------------------------------ END\n")
    return

def tx_known((rxx, rxy, aorb), g, c):
    if aorb == 0:
        return c - g * np.log10(get_distance(rxx, 6.8, rxy, 6.8))
    elif aorb == 1:
        return c - g * np.log10(get_distance(rxx, -0.87, rxy, 9.45))

def tx_a((rxx, rxy), g, c):
    return c - g * np.log10(get_distance(rxx, 6.8, rxy, 6.8))

def tx_b((rxx, rxy), g, c):
    return c - g * np.log10(get_distance(rxx, -0.87, rxy, 9.45))

def tx_unknown((rxx, rxy), txx, txy, g, c):
    return c - g * np.log10(get_distance(rxx, txx, rxy, txy))

def least_sq(func, locs, rss):
    popt, pcov = scipy.optimize.curve_fit(func, locs, rss, (5, 5, -50, 1), method='lm')
    return popt

def res_for_ab(folder):
    macs = get_macs(folder)
    for mac in macs:
        print(mac.mac)
        if mac.mac == "8c:85:90:16:0a:a4":
            print(mac.mac)
            print(least_sq(tx_a, (mac.dic["xs"], mac.dic["ys"]), mac.dic["rsses"]))
        elif mac.mac == "ac:9e:17:7d:31:e8":
            print(mac.mac)
            print(least_sq(tx_b, (mac.dic["xs"], mac.dic["ys"]), mac.dic["rsses"]))

def res_unknown(folder):
    macs = get_macs(folder)
    for mac in macs:
        print(mac.mac)
        try:
            res = least_sq(tx_unknown, (mac.dic["xs"], mac.dic["ys"]), mac.dic["rsses"])
            print(res)
        except:
            print("error")
        if mac.mac == "8c:85:90:16:0a:a4":
            res_a = least_sq(tx_a, (mac.dic["xs"], mac.dic["ys"]), mac.dic["rsses"])
        elif mac.mac == "ac:9e:17:7d:31:e8":
            res_b = least_sq(tx_b, (mac.dic["xs"], mac.dic["ys"]), mac.dic["rsses"])

if __name__ == '__main__':
    train_folder("./data")
