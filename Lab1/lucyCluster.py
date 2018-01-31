#!/usr/bin/env python
from sklearn.cluster import KMeans
import numpy as np
from log import Log
from parse import parseFolder, parseFolderSelected
from itertools import combinations
from nfft import nfft

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
    points = map(lambda x: x.getMultipleMeasurements(ylabels), logs)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    labels = kmeans.labels_
    # print(ylabels)
    # print(labels)
    return labels

def checkGroundTruth(logs, labels, expected):
    if sum(labels) > len(labels) // 2:
        for i in range(len(labels)):
            labels[i] = 1 - labels[i]
    res = {}
    if (len(logs) != len(labels)):
        return 
    for i in range(len(logs)):
        unexpected = 1
        if logs[i].type == expected and labels[i] == 1:
            unexpected = 0
        if logs[i].type != expected and labels[i] == 0:
            unexpected = 0
        if logs[i].type in res:
            res[logs[i].type] += unexpected
        else:
            res[logs[i].type] = unexpected
    return res

def perfectFit(logs, labels, expected):
    groundTruth = checkGroundTruth(logs, labels, expected)
    for g in groundTruth:
        if groundTruth[g] != 0:
            return False
    return True

def checkCombos(logs, categories):
    for expected in categories:
        for i in range(1,len(measurements) + 1):
            for ylabels in combinations(np.array(measurements), i):
                labels = testMultipleVars(logs, ylabels)
                print(ylabels, labels)
                if perfectFit(logs, labels, expected):
                    print("THIS IS IT", expected, ylabels)
                    return expected, ylabels

def getPrediction(log, folder, categories, ylabels):
    logs = parseFolderSelected(folder,categories)
    points = map(lambda x: comboMeas(x, ylabels), logs)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    point = comboMeas(log, ylabels)
    prediction = kmeans.predict([point])
    return prediction[0]

def predictNewPoint(point, folder):
    categories = ["Walking", "Jumping", "Driving", "Standing"]
    prediction = getPrediction(point, folder, categories, \
        ['xGyro', 'xAccl', 'zAccl'])
    if prediction == 1:
        return "Jumping"
    categories.remove("Jumping")
    prediction = getPrediction(point, folder, categories, \
        ['yGyro', 'xMag', 'yAccl', 'yMag'])
    if prediction == 0:
        return "Standing"
    categories.remove("Standing")
    prediction = getPrediction(point, folder, categories, \
        ['xGyro', 'yAccl'])
    if prediction == 1:
        return "Walking"
    if prediction == 0:
        return "Driving"   


folder = "./data/"
categories = ["Walking", "Jumping", "Driving", "Standing"]

# logs = parseFolder(folder)
# checkCombos(logs)

# for log in logs:
#     print("Actual: %s" % log.type)
#     prediction = predictNewPoint(log, folder)
#     print("Predcition: %s\n" % prediction)

# logs = parseFolder(folder)

# labels = testMultipleVars(logs, ['xGyro', 'xAccl', 'zAccl'])
# gt = checkGroundTruth(logs, labels)
# print(labels)
# print(gt)

categories = ["Driving","Walking","Standing"]
logs = parseFolderSelected(folder, categories)
# checkCombos(logs)

labels = testMultipleVars(logs, ['yGyro', 'xMag', 'yAccl', 'yMag'])
gt = checkGroundTruth(logs, labels, "Standing")
print(labels)
print(gt)

# categories = ["Driving","Walking"]
# logs = parseFolderSelected(folder, categories)
# checkCombos(logs, categories)

# labels = testMultipleVars(logs, ['xGyro', 'yAccl'])
# gt = checkGroundTruth(logs, labels)
# print(labels)
# print(gt)
