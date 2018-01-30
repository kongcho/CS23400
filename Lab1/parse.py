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
        # log.showPlot()
        logs.append(log)
    return logs

def parseTestFolder(folderpath):
    logs = []
    for file in os.listdir(folderpath):
        filepath = os.path.join(folderpath, file)
        with open(filepath) as f:
            rawdata = ast.literal_eval(f.read())
            logs.append(Log(rawdata))
    return logs

def parseFolder(folderpath):
    logs = []
    for file in os.listdir(folderpath):
        filepath = os.path.join(folderpath, file)
        logs += parseTestFile(filepath)
    return logs

def parseFolderSelected(folderpath, types):
    logs = []
    for file in os.listdir(folderpath):
        for t in types: 
            if t in file:
                filepath = os.path.join(folderpath, file)
                logs += parseFile(filepath)
                continue
    return logs

## TODO: There may be better ways to display this

if __name__ == '__main__':
    filepath = "./data/activity-dataset-Jumping.txt"
    parseFile(filepath)
