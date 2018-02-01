#!/usr/bin/env python
from sklearn.cluster import KMeans
import numpy as np
from log import Log
from parse import parseFolder, parseTestFolder, parseFolderSelected, parseFolderSelectedFast
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
        print(expected)
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
                print(ylabels, offBy, gt)
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

def predictNewPoint(point, folder, ms1, ms2, ms3):
    categories = ["Walking", "Jumping", "Driving", "Standing"]
    prediction = getPrediction(point, folder, categories, ms1, 0.)
    if prediction == 1:
        return "Jumping"
    categories.remove("Jumping")
    prediction = getPrediction(point, folder, categories, ms2, 0.2)
    if prediction == 0:
        return "Standing"
    categories.remove("Standing")
    prediction = getPrediction(point, folder, categories, ms3, 0.5)
    if prediction == 1:
        return "Walking"
    if prediction == 0:
        return "Driving"

def getRightLogs(all_points, types):
    logs = []
    for key in all_points:
        if key in types:
            logs += all_points[key]
    return logs

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



def predictNewPointFast(log, points, ylabels, all_points, ts, ms1, ms2, ms3):
    types = Log.types[:]
    point = log.getMultMeasFast(ylabels, ts[0])
    prediction = getPredictionFast(point, points, ylabels, ms1)
    if prediction == 1:
        return "Jumping"
    types.remove("Jumping")
    points = getRightLogs(all_points, types)
    point = log.getMultMeasFast(ylabels, ts[1])
    prediction = getPredictionFast(point, points, ylabels, ms2)
    if prediction == 1:
        return "Driving"
    types.remove("Driving")
    points = getRightLogs(all_points, types)
    point = log.getMultMeasFast(ylabels, ts[2])
    prediction = getPredictionFast(point, points, ylabels, ms3)
    if prediction == 1:
        return "Standing"
    if prediction == 0:
        return "Walking"   

def predictFast(test_folder, folder, thres, ms1, ms2, ms3):
    wrongs = 0
    types = Log.types
    ylabels = ["xAccl", "yAccl", "zAccl"]
    all_logs = parseFolderSelectedFast(folder, types)
    all_points = {}
    for key in all_logs:
        all_points[key] = map(lambda x: x.getMultMeasFast(ylabels, thres), all_logs[key])
    points = getRightLogs(all_points, types)
    test_logs = parseTestFolder(test_folder)
    for log in test_logs:
        result = predictNewPointFast(log, points, ylabels, all_points, [0.,0.2,0.5], ms1, ms2, ms3)
        print("Actual: %s" % log.type)
        if log.type != result:
            wrongs += 1
            print "WRONG!!: ",
        print("Prediction: %s\n" % result)
    total = len(test_logs)
    percent = (total - wrongs) * 100.0 / total 
    print("wrongs: %d out of %d: %f percent" % (wrongs, total, percent))


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

def showGt(logs, ylabels, expected, thres):
    print("***")
    print("expected: %s" % expected)
    print("printing false negatives and false positives")
    labels = testMultipleVars(logs, ylabels, thres)
    gt = checkGroundTruth(logs, labels, expected)
    print(gt)
    print("***")

def checkAllPoints(folder, ms1, ms2, ms3):
    logs = parseFolder(folder)
    numWrong = 0.
    for log in logs:
        print("Actual: %s" % log.type)
        prediction = predictNewPoint(log, folder, ms1, ms2, ms3)
        if prediction == log.type:
            msg = "Right!"            
        else:
            msg = "--Wrong!!"
            numWrong += 1
        print("%s Predcition: %s\n" % (msg, prediction))
    percent = numWrong / len(logs)
    print("%d correct (%f%)" % (numWrong, percent))
    return numWrong

def getFastResults(ms1, ms2, ms3):
    test_folder = "./test"
    folder = "./data"
    predictFast(test_folder, folder, 0.3, ms1, ms2, ms3)

getFastResults(["xAccl", "zAccl"], ["yAccl", "zAccl"], ["yAccl"])

# folder = "./data/"
# categories = ["Walking", "Jumping", "Driving", "Standing"]
# logs = parseFolder(folder)
# ylabels = ["xAccl", "zAccl"]
# showGt(logs, ylabels, "Jumping", 0.)

# checkAllPoints(folder, ["xAccl", "zAccl"], ["yAccl"], ["yAccl"])

# predictNewPoint(log, folder, ['xGyro', 'xAccl', 'zAccl'], \
#     ['yGyro', 'xMag', 'yAccl', 'yMag'], \
#     ['xGyro', 'yAccl'])

# categories.remove("Jumping")
# logs = parseFolderSelected(folder, categories)
# ylabels = ["yAccl"]
# showGt(logs, ylabels, "Driving", 0.2)
# getBestThreshold(logs, categories)
#### yAccl and zAccl seem to consistantly yield the best results
#### the optimal threshold is around thres=0.2


# categories.remove("Driving")
# logs = parseFolderSelected(folder, categories)
# showGt(logs, ylabels, "Standing", 0.5)

# getBestThreshold(logs, categories)
## best threshold thres=0.5, only yAccl

# logs = parseFolderSelected(folder, categories)
# for i in range(10):
#     checkCombos(logs, categories, i/10.)