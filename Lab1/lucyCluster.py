#!/usr/bin/env python
from sklearn.cluster import KMeans
import numpy as np
from log import Log
from parse import parseFolder, parseFolderSelected
from itertools import combinations
import datetime

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
                print(category, ylabels)
                return category, ylabels
    return "Standing", ['yGyro', 'xMag', 'yAccl', 'yMag']

def getPrediction(log, folder, categories, ylabels):
    print("1 " + str(datetime.datetime.now()))
    logs = parseFolderSelected(folder,categories)
    print("2 " + str(datetime.datetime.now()))
    points = map(lambda x: comboMeas(x, ylabels), logs)
    print("3 " + str(datetime.datetime.now()))
    kmeans = KMeans(n_clusters=2, random_state=0).fit(points)
    print("4 " + str(datetime.datetime.now()))
    point = comboMeas(log, ylabels)
    print("5 " + str(datetime.datetime.now()))
    prediction = kmeans.predict([point])
    print("6 " + str(datetime.datetime.now()))
    return prediction[0]

def getPredictionFast(all_points, i, log, ylabels):
    all_ylabels =  ["xGyro","yGyro","xAccl","xMag","zAccl","yAccl","zGyro","yMag","zMag"]
    indexes = []
    print("1 " + str(datetime.datetime.now()))
    for y in ylabels:
        for i, ylabel in enumerate(all_ylabels):
            if y == ylabel:
                indexes.append(i)
    print("2 " + str(datetime.datetime.now()))
    new_points = map(lambda arr: [arr[x] for x in indexes], all_points)
    print("3 " + str(datetime.datetime.now()))
#    print(new_points)
    new_point = [all_points[i][x] for x in indexes]
    print("4 " + str(datetime.datetime.now()))
#    print(new_point)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(new_points)
    print("5 " + str(datetime.datetime.now()))
    #point = comboMeas(log, ylabels)
    prediction = kmeans.predict([new_point])
    print("6 " + str(datetime.datetime.now()))
#    print(prediction)
    return prediction[0]

def parseFolderSelectedFast(folderpath, types):
    logs = []
    for file in os.listdir(folderpath):
        for t in types:
            if t in file:
                filepath = os.path.join(folderpath, file)
                logs += parseFile(filepath)
                continue
    return logs

def removeCat(removing, categories, all_points):
    pass

def predictNewPointFast(folder):
    categories = ["Walking", "Jumping", "Driving", "Standing"]
    ylabels =  ["xGyro","yGyro","xAccl","xMag","zAccl","yAccl","zGyro","yMag","zMag"]
    logs = parseFolderSelected(folder, categories)
    all_points = map(lambda x: comboMeas(x, ylabels), logs)
    for i, log in enumerate(logs):
        print("Actual: %s" % log.type)
        prediction = getPredictionFast(all_points, i, log, \
                                       ["xGyro", "zAccl", "yGyro", "yAccl"])
        if prediction == 1:
            result = "Jumping"
        categories.remove("Jumping")
        prediction = getPredictionFast(all_points, i, log, \
                                       ['yGyro', 'xMag', 'yAccl', 'yMag'])
        if prediction == 0:
            result = "Standing"
        categories.remove("Standing")
        prediction = getPredictionFast(all_points, i, log, \
                                       ['xGyro', 'yGyro', 'zAccl', 'yAccl', 'zGyro', 'zMag'])
        if prediction == 1:
            result = "Walking"
        if prediction == 0:
            result = "Driving"
        print("Prediction: %s\n" % result)

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


folder = "./data/"
categories = ["Walking", "Jumping", "Driving", "Standing"]

def new_func(folder):
    predictNewPointFast(folder)

def old_func(folder):
    logs = parseFolder(folder)
    for log in logs:
        print("Actual: %s" % log.type)
        prediction = predictNewPoint(log, folder)
        print("Prediction: %s\n" % prediction)

#old_func(folder)
#checkCombos(log)

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

test_vars(folder)
