#!/usr/bin/env python
import os
import ast
from log import Log

def parseFile(filepath):
    """
    pares a log file to return a Log object
    inputs:
    filepath (string): path to the log file
    return:
    Log object of parsed data
    """
    with open(filepath) as f:
        rawdata = f.read()
    rawdata = ast.literal_eval(rawdata)
    log = Log(rawdata)
    return log

def parseFolder(folderpath):
    """
    parese all of the files in a folder
    inputs:
    folderpath (string): path to the log folder
    return:
    list of Log objects
    """
    all_logs = []
    for file in os.listdir(folderpath):
        filepath = os.path.join(folderpath, file)
        all_logs.append(parseFile(filepath))
    return all_logs

