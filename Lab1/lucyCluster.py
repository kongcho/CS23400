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
        kmeans = KMeans(n_clusters=2, random_state=0 ,max_iter=20).fit(points)
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
#    print(ylabels)
#    print(labels)
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
        print(nonZeroCategory)
        return nonZeroCategory
    return None

def checkCombos(logs):
    for i in range(1, len(measurements) + 1):
        for ylabels in combinations(np.array(measurements), i):
            labels = testMultipleVars(logs, ylabels)
            print(ylabels, labels)
            category = perfectFit(logs, labels)
            if category:
                print(category, ylabels)
                return category, ylabels
    return "Standing", ['yGyro', 'xMag', 'yAccl', 'yMag']

def getPrediction(log, folder, categories, ylabels):
    logs = parseFolderSelected(folder,categories)
    points = map(lambda x: comboMeas(x, ylabels), logs)
    print("here1")
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    point = comboMeas(log, ylabels)
    print("here2")
    prediction = kmeans.predict([point])
    print("here3")
    return prediction[0]

def predictNewPoint(point, folder):
    categories = ["Walking", "Jumping", "Driving", "Standing"]
    prediction = getPrediction(point, folder, categories, \
        ["xGyro", "zAccl", "yGyro", "yAccl"])
    if prediction == 1:
        return "Jumping"
    categories.remove("Jumping")
    prediction = getPrediction(point, folder, categories, \
        ['yGyro', 'xMag', 'yAccl', 'yMag'])
    if prediction == 0:
        return "Standing"
    categories.remove("Standing")
    prediction = getPrediction(point, folder, categories, \
        ['xGyro', 'yGyro', 'zAccl', 'yAccl', 'zGyro', 'zMag'])
    if prediction == 1:
        return "Walking"
    if prediction == 0:
        return "Driving"


folder = "./data/"
categories = ["Walking", "Jumping", "Driving", "Standing"]

logs = parseFolder(folder)
for log in logs:
    print("Actual: %s" % log.type)
    prediction = predictNewPoint(log, folder)
    print("Prediction: %s\n" % prediction)


# logs = parseFolder(folder)
# checkCombos(logs)

# print(len(logs))
# print(logs[0].type)
# labels = testMultipleVars(logs, ["xGyro", "yGyro", "yAccl", "zAccl"])
# gt = checkGroundTruth(logs, labels)
# print("1")
# print(labels)
# print("2")
# print(gt)

# logs = parseFolderSelected(folder, ["Driving","Walking","Standing"])
# labels = testMultipleVars(logs, ['yGyro', 'xMag', 'yAccl', 'yMag'])
# gt = checkGroundTruth(logs, labels)
# print("3")
# print(labels)
# print("4")
# print(gt)

# logs = parseFolderSelected(folder, ["Driving","Walking"])
# labels = testMultipleVars(logs, ['xGyro', 'yGyro', 'zAccl', 'yAccl', 'zGyro', 'zMag'])
# gt = checkGroundTruth(logs, labels)
# print("5")
# print(labels)
# print("6")
# print(gt)


