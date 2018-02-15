from parse import parseFolder, parseFile
from log import Log, Mac, get_distance
import scipy.optimize
import numpy as np

macs = ["8c:85:90:16:0a:a4", "ac:9e:17:7d:31:e8", "d8:c4:6a:50:e3:b1", "f8:cf:c5:97:e0:9e"]
# 8c:85:90:16:0a:a4 (location: x=6.8, y=6.8)
# ac:9e:17:7d:31:e8 (location: x=-0.87, y=9.45)

# We didn't use this function because it combined all the traces
def get_macs(folder):
    """
    Get the Mac objects from a folder combining all traces
    inputs:
    folder (string): the name of the folder containing logs
    return:
    list of Mac objects based on the folder
    """
    logs = parseFolder(folder)
    data = []
    for mac in macs:
        data.append(Mac(mac, logs))
    return data

# This function separated the data for each trace
def get_macs_each(folder):
    """
    Get the Mac objects from a folder for each trace
    inputs:
    folder (string): the name of the folder containing logs
    return:
    list of Mac objects based on the folder
    """
    logs = parseFolder(folder)
    data = []
    for mac in macs:
        for log in logs:
            data.append(Mac(mac, [log]))
    return data

def train_folder(folder):
    """
    Uses each trace and trains data for each Mac address in the trace
      and outputs transmittor location, g, and c from the model
    input:
    folder (string): folder name
    return:
    results (stdout)
    """
    macs_data = get_macs_each(folder)
    for mac_name in macs:
        print("#### MAC: " + mac_name)
        curr_resx = []
        curr_resy = []
        errors = []
        for mac in macs_data:
            if mac.mac == mac_name:
                try:
                    res = least_sq_known(tx_unknown, (mac.dic["xs"], mac.dic["ys"]), mac.dic["rsses"])
                    curr_resx.append(res[0])
                    curr_resy.append(res[1])
                    if mac.mac == "8c:85:90:16:0a:a4":
                        err = (get_distance(res[0], 6.8, res[1], 6.8))
                        errors.append(err)
                    elif mac.mac == "ac:9e:17:7d:31:e8":
                        err = (get_distance(res[0], -0.87, res[1], 9.45))
                        errors.append(err)
                except:
                    print("Error: couldn't get results")
        resx = np.average(sorted(curr_resx)[2:-2])
        resy = np.median(sorted(curr_resy)[2:-2])
        print("\nRESULTS:\t" + str((resx, resy)))
        if mac_name == "8c:85:90:16:0a:a4":
            err = (get_distance(resx, 6.8, resy, 6.8))
            print("Error avg:\t" + str(np.average(errors)))
            print("Rrror Real:\t" + str(err))
        elif mac_name == "ac:9e:17:7d:31:e8":
            err = (get_distance(resx, -0.87, resy, 9.45))
            print("Avg error:\t" + str(np.average(errors)))
            print("Real error:\t" + str(err))
        print("--------------------------------------------------------- END\n")
    return

# Model for "8c:85:90:16:0a:a4" to see possible g, c values
def tx_a((rxx, rxy), g, c):
    return c - g * np.log10(get_distance(rxx, 6.8, rxy, 6.8))

# Model for "ac:9e:17:7d:31:e8" to see possible g, c values
def tx_b((rxx, rxy), g, c):
    return c - g * np.log10(get_distance(rxx, -0.87, rxy, 9.45))

# Model to pass through curve_fit function
# Treats transmittor locations as unknowns
def tx_unknown((rxx, rxy), txx, txy, g, c):
    return c - g * np.log10(get_distance(rxx, txx, rxy, txy))

# Model to train the data--bounds are based on likely x,y limits and parameters
#   that give the most accurate results
def least_sq_known(func, locs, rss):
    bs = ((-5, -5, -10, -100), (15, 15, 150, 100))
    popt, pcov = scipy.optimize.curve_fit(func, locs, rss, (3, 3, 30, -30), bounds=bs, method='trf')
    return popt

# Original model with no parameters
def least_sq(func, locs, rss):
    popt, pcov = scipy.optimize.curve_fit(func, locs, rss, method='lm')
    return popt

# Gets g, c values for known mac addresses to get a better sense
#   of possible values
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

if __name__ == '__main__':
    folder = "./data"
    train_folder(folder)
