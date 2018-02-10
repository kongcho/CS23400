from parse import parseFolder
from log import Log, Mac

macs = ["8c:85:90:16:0a:a4", "ac:9e:17:7d:31:e8", "d8:c4:6a:50:e3:b1", "f8:cf:c5:97:e0:9e"]

def get_macs(folder):
    logs = parseFolder(folder)
    data = []
    for mac in macs:
        data.append(Mac(mac, logs))
    return data

get_macs("./data")
