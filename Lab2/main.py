from parse import parseFolder
from log import Log, Mac

macs = ["8c:85:90:16:0a:a4", "ac:9e:17:7d:31:e8", "d8:c4:6a:50:e3:b1", "f8:cf:c5:97:e0:9e"]
# 8c:85:90:16:0a:a4 (location: x=6.8, y=6.8), ac:9e:17:7d:31:e8 (location: x=-0.87, y=9.45)

def get_macs(folder):
    logs = parseFolder(folder)
    data = []
    for mac in macs:
        data.append(Mac(mac, logs))
    return data

if __name__ == '__main__':
    get_macs("./data")
