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
    points = map(lambda x: comboMeas(x, ylabels), logs)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    labels = kmeans.labels_
    # print(ylabels)
    # print(labels)
    return labels

def checkGroundTruth(logs, labels):
    res = {}
    if (len(logs) != len(labels)):
        return 
    for i in range(len(logs)):
        if logs[i].type in res:
            res[logs[i].type] += labels[i]
        else:
            res[logs[i].type] = labels[i]
    return res

def perfectFit(logs,labels):
    groundTruth = checkGroundTruth(logs, labels)
    numZero = 0
    nonZeroCategory = ""
    for category in groundTruth:
        if groundTruth[category] == 0:
            numZero += 1
        else:
            nonZeroCategory = category
    numPositives = 0
    for log in logs:
        if log.type == nonZeroCategory:
            numPositives += 1
    if numZero == len(groundTruth) - 1 and numPositives == groundTruth[nonZeroCategory]:
        return nonZeroCategory
    return None

def checkCombos(logs):
    for i in range(1,len(measurements) + 1):
        for ylabels in combinations(np.array(measurements), i):
            labels = testMultipleVars(logs, ylabels)
            print(ylabels, labels)
            category = perfectFit(logs, labels)
            if category:
                print("THIS IS IT", category, ylabels)
                return category, ylabels

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

logs = parseFolder(folder)
# checkCombos(logs)

# for log in logs:
#     print("Actual: %s" % log.type)
#     prediction = predictNewPoint(log, folder)
#     print("Predcition: %s\n" % prediction)

# logs = parseFolder(folder)

labels = testMultipleVars(logs, ['xGyro', 'xAccl', 'zAccl'])
gt = checkGroundTruth(logs, labels)
print(labels)
print(gt)

logs = parseFolderSelected(folder, ["Driving","Walking","Standing"])
# checkCombos(logs)

labels = testMultipleVars(logs, ['yGyro', 'xMag', 'yAccl', 'yMag'])
gt = checkGroundTruth(logs, labels)
print(labels)
print(gt)

logs = parseFolderSelected(folder, ["Driving","Walking"])
# checkCombos(logs)

labels = testMultipleVars(logs, ['xGyro', 'yAccl'])
gt = checkGroundTruth(logs, labels)
print(labels)
print(gt)
