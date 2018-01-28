#!/usr/bin/env python
from sklearn.cluster import KMeans
import numpy as np
from log import Log
from parse import parseFolder, parseFolderSelected
from itertools import combinations

measurements = ["xGyro","yGyro","xAccl","xMag","zAccl","yAccl","zGyro","yMag","zMag"]

def testEachVar(logs):
    for ylabel in measurements:
        points = map(lambda x: x.getMeasurementInfo(ylabel), logs)
        kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
        labels = kmeans.labels_
        print(ylabel)
        print(labels)

def comboMeas(log, measArr):
    points = []
    for ylabel in measArr:
        points += log.getMeasurementInfo(ylabel)
    return points

ylabels = ["xGyro", "zAccl", "yGyro", "yAccl"]

def testMultipleVars(logs, ylabels):
    points = map(lambda x: comboMeas(x, ylabels), logs)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    labels = kmeans.labels_
    print(ylabels)
    print(labels)

def checkCombos():
    for i in range(1,len(measurements) + 1):
        for ylabels in combinations(np.array(measurements), i):
            testMultipleVars(logs, ylabels)

folder = "./data/"
logs = parseFolder(folder)
testMultipleVars(logs, ["xGyro", "zAccl", "yGyro", "yAccl"])


logs = parseFolderSelected(folder, ["Driving","Walking","Standing"])
testMultipleVars(logs, ['yGyro', 'xMag', 'yAccl', 'yMag'])

logs = parseFolderSelected(folder, ["Driving","Walking"])
testMultipleVars(logs, ['xGyro', 'yGyro', 'zAccl', 'yAccl', 'zGyro', 'zMag'])
