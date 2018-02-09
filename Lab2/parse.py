#!/usr/bin/env python
import os
import ast
from log import Log

def parseFile(filepath):
    with open(filepath) as f:
        rawdata = f.read()
    rawdata = ast.literal_eval(rawdata)
    log = Log(rawdata)
    return log

def parseFolder(folderpath):
    all_logs = []
    for file in os.listdir(folderpath):
        filepath = os.path.join(folderpath, file)
        all_logs.append(parseFile(filepath))
    return all_logs

