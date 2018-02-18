#!/usr/bin/env python3

from datetime import datetime
import os
import regex as re

class Log(object):
    mtypes = ["xAccls", "yAccls", "zAccls"]
    def __init__(self, rawdata):
        regex = "(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+).*(Gyroscope|Acceleration|Accelerometer).*?([-\.\dE]+,[-\.\dE]+,[-\.\dE]+)"
        self.times = []
        self.seconds = []
        self.data = []
        first = True
        self.numErrs = 0
        for line in rawdata:
            try:
                m = re.match(regex, line)
                if not m:
                    print("no match found \n\t%s" % line)
                date = m.group(1)
                dt = datetime.strptime(date, "%m-%d %H:%M:%S.%f")
                secs = datetime_to_float(dt)
                if first:
                    self.t0 = secs
                    first = False
                    s = 0.
                else:
                    s = secs - self.t0
                    gap = s - self.seconds[-1]
                    if gap > 1:
                        print("big time gap %f" % gap)
                self.seconds.append(s)
                self.times.append(dt)                
                motionType = m.group(2)
                if motionType == "Acceleration":
                    motionType = "Accelerometer"
                data = m.group(3)
                measurements = list(map(lambda x: float(x), data.split(",")))
                dataPoint = [motionType, s, measurements]
                self.data.append(dataPoint)
            except Exception as e:
                print(str(e))
                self.numErrs += 1
                pass
        print(self.numErrs)

def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return total_seconds


if __name__ == '__main__':
    folder = "data"
    for file in os.listdir("data"):
        filepath = os.path.join(folder, file)
        with open(filepath) as f:
            data = f.read().split("\n")
        log = Log(data)
        break