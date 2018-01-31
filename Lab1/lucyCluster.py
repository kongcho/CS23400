#!/usr/bin/env python
from sklearn.cluster import KMeans
from log import Log
from parse import *
from itertools import combinations
import numpy as np
import os

measurements = ["xGyro","yGyro","xAccl","xMag","zAccl","yAccl","zGyro","yMag","zMag"]
categories = ["Walking", "Jumping", "Driving", "Standing"]

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
                print(category, ylabels)
                return category, ylabels
    return "Standing", ['yGyro', 'xMag', 'yAccl', 'yMag']

def getPrediction(log, folder, categories, ylabels):
    logs = parseFolderSelected(folder, categories)
    points = map(lambda x: comboMeas(x, ylabels), logs)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    point = comboMeas(log, ylabels)
    prediction = kmeans.predict([point])
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
        return "Driving"
    if prediction == 0:
        return "Walking"

def parseFolderSelectedFast(folderpath, types):
    logs = {}
    for file in os.listdir(folderpath):
        curr_types = []
        for t in types:
            if t in file:
                filepath = os.path.join(folderpath, file)
                curr_types += parseFile(filepath)
                logs[t] = curr_types
    return logs

def getRightLogs(all_points, types):
    logs = []
    for key in all_points:
        if key in types:
            logs += all_points[key]
    return logs

def comboMeasFast(log, measArr):
    points = []
    for ylabel in measArr:
        points += [log.getMeasurementInfo(ylabel)]
    return points

def getPredictionFast(point, all_points, all_ylabels, ylabels):
    indexes = []
    for y in ylabels:
        for i, ylabel in enumerate(all_ylabels):
            if y == ylabel:
                indexes.append(i)
    new_points = []
    for i in all_points:
        temp = []
        for x in indexes:
            temp += i[x]
        new_points.append(temp)
    new_point = []
    for x in indexes:
        new_point += point[x]
    kmeans = KMeans(n_clusters=2, random_state=0).fit(new_points)
    prediction = kmeans.predict([new_point])
    return prediction[0]

def predictNewPointFast(log, points, ylabels, all_points):
    types = ["Walking", "Jumping", "Driving", "Standing"]
    point = comboMeasFast(log, ylabels)
    prediction = getPredictionFast(point, points, ylabels, \
                                   ['xAccl', 'yAccl', 'zAccl', 'xGyro'])
    if prediction == 1:
        return "Jumping"
    types.remove("Jumping")
    points = getRightLogs(all_points, types)
    prediction = getPredictionFast(point, points, ylabels, \
                                   ['yGyro', 'xMag', 'yAccl', 'yMag'])
    if prediction == 0:
        return "Standing"
    types.remove("Standing")
    points = getRightLogs(all_points, types)
    prediction = getPredictionFast(point, points, ylabels, \
                                   ['xGyro', 'yGyro', 'zAccl', 'yAccl', 'zGyro', 'zMag'])
    if prediction == 1:
        return "Driving"
    if prediction == 0:
        return "Walking"

def predictFast(test_folder, folder):
    wrongs = 0
    types = ["Walking", "Jumping", "Driving", "Standing"]
    ylabels =  ["xGyro","yGyro","xAccl","xMag","zAccl","yAccl","zGyro","yMag","zMag"]
    all_logs = parseFolderSelectedFast(folder, types)
    all_points = {}
    for key in all_logs:
        all_points[key] = map(lambda x: comboMeasFast(x, ylabels), all_logs[key])
    points = getRightLogs(all_points, types)
    test_logs = parseFolder(test_folder)
    for log in test_logs:
        result = predictNewPointFast(log, points, ylabels, all_points)
        print("Actual: %s" % log.type)
        if log.type != result:
            wrongs += 1
            print "WRONG!!: ",
        print("Prediction: %s\n" % result)
    print("wrongs: " + str(wrongs))

def test_vars(folder):
    logs = parseFolder(folder)

    labels = testMultipleVars(logs, ["xGyro", "yGyro", "yAccl"])
    gt = checkGroundTruth(logs, labels)
    print(labels)
    print(gt)

    logs = parseFolderSelected(folder, ["Driving","Walking","Standing"])
    labels = testMultipleVars(logs, ['yGyro', 'xMag', 'yAccl', 'yMag'])
    gt = checkGroundTruth(logs, labels)
    print(labels)
    print(gt)

    logs = parseFolderSelected(folder, ["Driving","Walking"])
    labels = testMultipleVars(logs, ['xGyro', 'yGyro', 'zAccl', 'yAccl', 'zGyro', 'zMag'])
    gt = checkGroundTruth(logs, labels)
    print(labels)
    print(gt)


def getFastResults():
    test_folder = "./data"
    folder = "./data"
    predictFast(test_folder, folder)

def getOldResults():
    folder = "./data"
    logs = parseFolder(folder)
    for log in logs:
        print("Actual: %s" % log.type)
        prediction = predictNewPoint(log, "./data")
        print("Prediction: %s\n" % prediction)

def getTestResults():
    folder = "./test"
    logs = parseTestFolder(folder)
    for log in logs:
        print("Actual: %s" % log.type)
        prediction = predictNewPoint(log, "./data")
        print("Prediction: %s\n" % prediction)

# getTestResults()
# getOldResults()
getFastResults()
# checkCombos(log)
