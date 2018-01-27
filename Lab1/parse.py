#!/usr/bin/env python
import os
import ast
from log import Log

def parseFile(filepath):
    with open(filepath) as f:
        rawdata = f.read()
    rawdata = ast.literal_eval(rawdata)
    logs = []
    for rd in rawdata:
        log = Log(rd)
        #print(log.getAllMeasurements())
        log.showPlot()
        logs.append(log)

    return logs

def parseFolder(folderpath):
    for file in os.listdir(folderpath):
        filepath = os.path.join(folderpath, file)
        parseFile(filepath)

# ## TODO: There may be better ways to display this

if __name__ == '__main__':
    filepath = "./data/activity-dataset-Jumping.txt"
    parseFile(filepath)