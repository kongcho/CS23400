from datetime import datetime

class Log(object):
    mtypes = ["xAccls", "yAccls", "zAccls"]
    def __init__(self, rawdata):
        self.times = []
        self.xAccls = []
        self.yAccls = []
        self.zAccls = []
        for line in rawdata:
            if line == "":
                continue
            spl = line.split(" D: ")
            date = spl[0]
            dt = datetime.strptime(date, "%m-%d %H:%M:%S.%f")
            print(dt)
            self.times.append(dt)
            accl = map(lambda x: float(x), spl[1].split(","))
            for i in range(len(accl)):
                self.__dict__[self.mtypes[i]] = accl[i]
                print(accl[i])


if __name__ == '__main__':
    with open("logs/example_logs.txt") as f:
        data = f.read().split("\n")
    log = Log(data)