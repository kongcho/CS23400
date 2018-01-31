#!/usr/bin/env python
from sklearn.cluster import KMeans
import numpy as np
from log import Log
from parse import parseFolder, parseFolderSelected
from itertools import combinations
from nfft import nfft

# measurements = ["xGyro","yGyro","xAccl","xMag","zAccl","yAccl","zGyro","yMag","zMag"]
measurements = ["xAccl", "yAccl", "zAccl"]
def testEachVar(logs, thres):
    for ylabel in measurements:
        points = map(lambda x: x.getMeasurementInfo(ylabel, thres), logs)
        kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
        labels = kmeans.labels_
        print(ylabel)
        print(labels)

ylabels = ["xGyro", "zAccl", "yGyro", "yAccl"]

def testMultipleVars(logs, ylabels, thres):
    points = map(lambda x: x.getMultipleMeasurements(ylabels, thres), logs)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    labels = kmeans.labels_
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

def checkCombos(logs, categories, thres):
    bestNum = 1000
    bestGt = None
    bestExpected = None
    for expected in categories:
        # print(expected)
        for i in range(1,len(measurements) + 1):
            for ylabels in combinations(np.array(measurements), i):
                labels = testMultipleVars(logs, ylabels, thres)
                gt = checkGroundTruth(logs, labels, expected)
                offBy = 0
                for t in gt:
                    offBy += gt[t]
                if offBy < bestNum:
                    bestNum = offBy
                    bestGt = ylabels
                    bestExpected = expected
                # print(ylabels, offBy, gt)
                if perfectFit(logs, labels, expected):
                    print("THIS IS IT", expected, ylabels)
                    return expected, offBy, ylabels
    print("RESULT", bestExpected, bestNum, bestGt)
    return bestExpected, bestNum, bestGt

def getPrediction(log, folder, categories, ylabels, thres):
    logs = parseFolderSelected(folder,categories)
    points = map(lambda x: x.getMultipleMeasurements(ylabels, thres), logs)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    point = log.getMultipleMeasurements(ylabels, thres)
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

def getBestThreshold(logs, categories):
    numWrong = 1000
    bestThres = -1
    for i in range(10):
        thres = i/10.
        print(thres)
        bestExpected, bestNum, bestGt = checkCombos(logs, categories, thres)
        if bestNum < numWrong:
            numWrong = bestNum
            bestThres = thres
    print(bestThres)
    return bestThres


folder = "./data/"
categories = ["Walking", "Jumping", "Driving", "Standing"]

logs = parseFolder(folder)
checkCombos(logs, categories, 0.0)
# getBestThreshold(logs, categories)

# for log in logs:
#     print("Actual: %s" % log.type)
#     prediction = predictNewPoint(log, folder)
#     print("Predcition: %s\n" % prediction)

# logs = parseFolder(folder)

# labels = testMultipleVars(logs, ['xGyro', 'xAccl', 'zAccl'])
# gt = checkGroundTruth(logs, labels)
# print(labels)
# print(gt)

categories.remove("Jumping")
logs = parseFolderSelected(folder, categories)
checkCombos(logs, categories, 0.2)

# getBestThreshold(logs, categories)
#### yAccl and zAccl seem to consistantly yield the best results
#### the optimal threshold is around thres=0.2

# labels = testMultipleVars(logs, ['yGyro', 'xMag', 'yAccl', 'yMag'])
# gt = checkGroundTruth(logs, labels, "Standing")
# print(labels)
# print(gt)

categories.remove("Driving")
logs = parseFolderSelected(folder, categories)
checkCombos(logs, categories, 0.5)

# getBestThreshold(logs, categories)
## best threshold thres=0.5, only yAccl

# logs = parseFolderSelected(folder, categories)
# for i in range(10):
#     checkCombos(logs, categories, i/10.)

# labels = testMultipleVars(logs, ['xGyro', 'yAccl'])
# gt = checkGroundTruth(logs, labels)
# print(labels)
# print(gt)
