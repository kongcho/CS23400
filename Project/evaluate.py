#!/usr/bin/env python3

import os
import json
import regex as re
import matplotlib.pyplot as plt
import numpy as np

from gyroOrAccl import GyroOrAccel

file_1 = "log_00_01_02_00_04.txt"
file_2 = "log_00_02_03_01_04.txt"
file_3 = "log_01_11_02_00_04.txt"
file_4 = "log_00_02_03_01_07.txt"

## For the purpose of group_by:
POSITIVE = 1
SCENARIO = 2
TRIAL = 3
DEVICE = 4
PERSON = 5

positives = ["Not fall", "Fall"]

scenarios = ["Sitting slow", "Sitting fast", "Cheer up only", "Cheer up and down",
    "Punch out only", "Punch out and in", "Squat sit", "Dab",
    "Walking down single step", "Walking down 5 steps", "Front fall no catch", "Front fall catch",
    "Side fall no catch", "Side fall catch", "Back fall no roll", "Back fall with roll",
    "Pushed fall front", "Pushed fall side", "Jump fall", "Front knee fall",
    "Dive roll", "Uncategorized fall"]

devices = ["Natalia's phone", "Cho Yin's phone"]

people = ["Natalia", "Cho Yin", "Lucy", "Poorvaja", 
    "Catherine", "Roberto", "Han Bin", "Andre", 
    "Clay", "Annalie", "Karlyn", "Najee",
    "Gamal", "Daniel", "Gaibo", "Aaron"]

def positive_to_string(pos_index):
    if pos_index in [0,1]:
        return positives[pos_index]
    else:
        raise ValueError("Positive value must be 0 or 1")

def scenario_to_string(scenario_index):
    if 0 <= scenario_index < 22:
        return scenarios[scenario_index] 
    else:
        raise ValueError("Invalid scenario value")

def device_to_string(device_index):
    if 0 <= device_index < 2:
        return devices[device_index]
    else:
        raise ValueError("Invalid device value")

def person_to_string(person_index):
    if 0 <= person_index < 16:
        return people[person_index]
    else:
        raise ValueError("Invalid person value")


def cat_dict_to_string_dict(cat_dict):
    ret_arr = []
    for cat in cat_dict:
        if cat == POSITIVE:
            ret_arr.append(positive_to_string(cat_dict[cat]))
        elif cat == SCENARIO:
            ret_arr.append(scenario_to_string(cat_dict[cat]))
        elif cat == DEVICE:
            ret_arr.append(device_to_string(cat_dict[cat]))
        elif cat == PERSON:
            ret_arr.append(person_to_string(cat_dict[cat]))
        elif cat == TRIAL:
            ## TODO
            pass
        else:
            raise ValueError
    return ret_arr

def cat_dict_to_string(cat_dict):
    string_dict = cat_dict_to_string_dict(cat_dict)
    return "; ".join(string_dict)

def categorize_file(filename, group_by=[POSITIVE]):
    regex = "log_(\d+)_(\d+)_(\d+)_(\d+)_(\d+).txt"
    m = re.match(regex, filename)
    positive = m.group(1)
    scenario = m.group(2)
    trial = m.group(3)
    device = m.group(4)
    person = m.group(5)
    cat_dict = {}
    for cat in group_by:
        cat_dict[cat] = int(m.group(cat))
    return cat_dict

## {"categories": {1: 0, 2: 1}, "files": []}
def separate_files(files, group_by=[POSITIVE]):
    ret = []
    for filename in files:
        cat_dict = categorize_file(filename, group_by=group_by)
        added = False
        for ret_dict in ret:
            if ret_dict["categories"] == cat_dict:
                ret_dict["files"].append(filename)
                added = True
                break
        if not added:
            label = cat_dict_to_string(cat_dict)
            new_dict = {"categories": cat_dict, "label": label, "files": [filename]}
            ret.append(new_dict)
    return ret

def sep_files_by_fall(folder, extra=[True, True], timeInterval=1.5, timeIntNeg=0.01, negPeakHeight=5, minPeakHeight=16, window_length=41, polyorder=12, thres=0.5, group_by=[POSITIVE]):
    mult_falls = []
    one_fall = []
    no_falls = []
    for file in os.listdir(folder):
        filepath = os.path.join(folder, file)
        with open(filepath) as f:
            data = f.read().split("\n")
        abso = GyroOrAccel("Absolute", data, file)
        fall_res = abso.is_fall(extra, timeInterval, timeIntNeg, negPeakHeight, minPeakHeight, window_length, polyorder, thres)
        if len(fall_res) == 0:
            no_falls.append(file)
        elif len(fall_res) == 1:
            one_fall.append(file)
        else:
            mult_falls.append(file)
    return {"one detected": one_fall,
            "multiple detected": mult_falls,
            "none detected": no_falls}

def sep_files_by_type_and_fall(folder, extra=[True, True], timeInterval=1.5, timeIntNeg=0.01, negPeakHeight=5, minPeakHeight=3, window_length=41, polyorder=12, thres=0.5, group_by=[POSITIVE]):
    num_peaks_dict = sep_files_by_fall(folder, extra=extra, timeInterval=timeInterval, timeIntNeg=timeIntNeg, negPeakHeight=negPeakHeight,
     minPeakHeight=minPeakHeight, window_length=window_length, polyorder=polyorder, thres=thres, group_by=group_by)
    ret_dict = {}
    for num_key in num_peaks_dict:
        files = num_peaks_dict[num_key]
        separated = separate_files(files, group_by=group_by)
        ret_dict[num_key] = separated
    return ret_dict

def get_recall(folder, timeInterval=1.5, minPeakHeight=3):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=[POSITIVE])
    total_falls = 0 
    for item in detection_dict["one detected"]:
        if item["label"] == "Fall":
            true_positives = item["num"]
    for key in detection_dict:
        for item in detection_dict[key]:
            if item["label"] == "Fall":
                total_falls += item["num"]
    return float(true_positives)/total_falls

def get_precision(folder, timeInterval=1.5, minPeakHeight=25):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=[POSITIVE])
    total_trials = detection_dict["one detected"][0]["num"] + detection_dict["one detected"][1]["num"] \
        + detection_dict["none detected"][0]["num"] + detection_dict["none detected"][1]["num"] \
        + detection_dict["one detected"][0]["num"] + detection_dict["one detected"][1]["num"]
    for item in detection_dict["one detected"]:
        if item["label"] == "Fall":
            true_positives = item["num"]
    return float(true_positives)/total_detections

def get_truths(folder, timeInterval=1.5, minPeakHeight=3):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=[POSITIVE])
    total_detections = detection_dict["one detected"][0]["num"] + detection_dict["one detected"][1]["num"]
    for item in detection_dict["one detected"]:
        if item["label"] == "Fall":
            true_positives = item["num"]
    return float(true_positives)/total_detections

def get_num_detected_each_cat(folder, extra=[True, True], timeInterval=1.5, timeIntNeg=0.01, negPeakHeight=5, minPeakHeight=3, window_length=41, polyorder=12, thres=0.5, group_by=[POSITIVE]):
    separated = sep_files_by_type_and_fall(folder, extra=extra, timeInterval=timeInterval, timeIntNeg=timeIntNeg, negPeakHeight=negPeakHeight,\
     minPeakHeight=minPeakHeight, window_length=window_length, polyorder=polyorder, thres=thres, group_by=group_by)
    ret_dict = {}
    for num_key in separated:
        ret_dict[num_key] = []
        for item in separated[num_key]:
            item_dict = {"label": item["label"], "num": len(item["files"])}
            ret_dict[num_key].append(item_dict)
    return ret_dict

def print_num_detected_each_cat(folder, extra=[True, True], timeInterval=1.5, timeIntNeg=0.01, negPeakHeight=5, minPeakHeight=16, window_length=41, polyorder=12, thres=0.5, group_by=[POSITIVE]):
    separated = sep_files_by_type_and_fall(folder, extra, timeInterval, timeIntNeg, negPeakHeight, minPeakHeight, window_length, polyorder, thres)
    false_pos = 0
    false_neg = 0
    truth_pos = 0
    truth_neg = 0
    for num_key in separated:
        # print(num_key)
        for item in separated[num_key]:
            label = item["label"]
            total = len(item["files"])
            if num_key == "none detected":
                if label == "Not fall":
                    truth_neg += total
                elif label == "Fall":
                    false_neg += total
            elif num_key == "one detected" or num_key == "multiple detected":
                if label == "Not fall":
                    false_pos += total
                elif label == "Fall":
                    truth_pos += total
            # print("\t%s: %d" % (label, total))
    sum = false_pos + false_neg + truth_pos + truth_neg
    print("false_pos: %s, false neg: %s, true pos: %s, true neg: %s" % (false_pos, false_neg, truth_pos, truth_neg))
    print("accuracy: %s, pres: %s, recall: %s" % (((truth_pos + truth_neg)/sum), (truth_pos/(truth_pos + false_pos)), (truth_pos/(truth_pos + false_neg))))
    return separated

def get_recall_and_precision(folder, timeInterval=1.5, minPeakHeight=3, group_by=[POSITIVE], phrase="", extra=[True, True]):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=group_by, extra=extra)
    # print(json.dumps(detection_dict, indent=4))
    total_falls = 0
    true_positives = 0
    for item in detection_dict["one detected"]:
        if "Fall" in item["label"] and phrase in item["label"]:
            true_positives = item["num"]
    if true_positives == 0:
        return -1., -1.
    for key in detection_dict:
        for item in detection_dict[key]:
            if "Fall" in item["label"] and phrase in item["label"]:
                total_falls += item["num"]
    recall = float(true_positives)/total_falls
    total_detections = detection_dict["one detected"][0]["num"] + detection_dict["one detected"][1]["num"]
    for item in detection_dict["one detected"]:
        if "Fall" in item["label"] and phrase in item["label"]:
            true_positives = item["num"]
    precision = float(true_positives)/total_detections
    return recall, precision

def get_accuracy(folder, timeInterval=1.5, minPeakHeight=3, group_by=[POSITIVE], phrase="", extra=[True, True]):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=group_by, extra=extra)
    # print(json.dumps(detection_dict, indent=4))
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    print(phrase)
    for item in detection_dict["one detected"]:
        if phrase in item["label"]:
            if "Fall" in item["label"]:
                true_positives = item["num"]
            elif "Not fall" in item["label"]:
                false_positives = item["num"]
    for item in detection_dict["none detected"]:
        if phrase in item["label"]:
            if "Not fall" in item["label"]:
                true_negatives = item["num"] 
            elif "Fall" in item["label"]:
                false_negatives = item["num"]
    total = true_negatives + true_positives + false_negatives + false_positives
    print(true_negatives, true_negatives, total)
    try:
        accuracy = float(true_negatives + true_positives) / total
    except:
        accuracy = -1.
    try:
        precision = float(true_positives) / (true_positives + false_positives)
    except:
        precision = -1.
    try:
        recall = float(true_positives) / (true_positives + false_negatives)
    except:
        recall = -1.
    return accuracy, precision, recall

def get_truth_by_category(folder, categories, cat_type, first_fall_cat, minPeakHeight=3, extra=[False, True]):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=1.5, minPeakHeight=minPeakHeight, group_by=[POSITIVE, cat_type], extra=extra)
    pos_dict = {}
    neg_dict = {}
    for cat_idx in range(len(categories)):
        cat = categories[cat_idx]
        if cat_idx < first_fall_cat:
            true_key = "none detected"
            false_key = "one detected"
        else:
            true_key = "one detected"
            false_key = "none detected"
        true_list = detection_dict[true_key]
        false_list = detection_dict[false_key]
        correct_num = 0
        incorrect_num = 0
        for item in true_list:
            if cat in item["label"]:
                correct_num = item["num"]
                break
        for item in false_list:
            if cat in item["label"]:
                incorrect_num = item["num"]
                break
        accuracy = float(correct_num) / (correct_num + incorrect_num)
        if cat_idx < first_fall_cat:
            neg_dict[cat] = accuracy
        else:
            pos_dict[cat] = accuracy
    return neg_dict, pos_dict

def optimize_recall_and_precision(folder):
    best_recall = 0
    best_precision = 0
    best_minPeakHeight = 0
    best_overall_precision = 0
    best_ovearll_precision_minPeakHeight = 0
    best_overall_recall = 0
    best_overall_recall_minPeakHeight = 0
    for minPeakHeight in range(50):
        print("minHeight: %d" % (minPeakHeight))
        print("best_minPeakHeight: %d, best recall: %f, best precision: %f" % (best_minPeakHeight, best_recall, best_precision))
        print("best_overall_recall: %f (%d), best_overall_precision: %f (%d)" % (best_overall_recall, best_overall_recall_minPeakHeight, best_overall_precision, best_ovearll_precision_minPeakHeight))
        recall, precision = get_recall_and_precision(folder, timeInterval=1.5, minPeakHeight=minPeakHeight)
        print("recall: %f, precision: %f" % (recall, precision))
        if recall + precision > best_recall + best_precision:
            best_recall = recall
            best_precision = precision
            best_minPeakHeight = minPeakHeight
        if recall > best_overall_recall:
            best_overall_recall = recall
            best_overall_recall_minPeakHeight = minPeakHeight
        if precision > best_overall_precision:
            best_overall_precision = precision
            best_ovearll_precision_minPeakHeight = minPeakHeight
    return best_minPeakHeight, best_recall, best_precision

def get_accuracy_dict(folder, categories, cat_type, minPeakHeight=3, extra=[False, True]):
    acc_dict = {}
    prec_dict = {}
    rec_dict = {}
    for cat in categories:
        accuracy, precision, recall = get_accuracy(folder, phrase=cat, minPeakHeight=minPeakHeight, group_by=[POSITIVE, cat_type], extra=extra)
        acc_dict[cat] = accuracy
        prec_dict[cat] = precision
        rec_dict[cat] = recall
    return acc_dict, prec_dict, rec_dict


def plot_results():
    folder = "finaldata"
    categorize_file(file_1)
    minPeakHeight = 16
    extra = [False, True]
    neg_dict, pos_dict = get_truth_by_category(folder, scenarios, SCENARIO, 10, extra=extra)

    for D in [neg_dict, pos_dict]:
        plt.bar(range(len(D)), list(D.values()), align='center')
        locs, labels = plt.xticks(range(len(D)), list(D.keys()))
        plt.setp(labels, rotation=30)
        if D == neg_dict:
            title = "Proportion of actions with no false positive"
        else:
            title = "Proportion of actions with accurate detection"
        plt.title(title)
        plt.show()


def print_results(folder, timeInterval=1.5, minPeakHeight=25, group_by=[POSITIVE, SCENARIO]):
    print(get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=[POSITIVE]))
    print("\n")
    print(json.dumps(get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=group_by), indent=4))

if __name__ == '__main__':
    # plot_results()
    folder = "finaldata"
    categories = people
    cat_type = PERSON
    acc_dict, prec_dict, rec_dict = get_accuracy_dict(folder, categories, cat_type, minPeakHeight=3, extra=[False, True])
    print(acc_dict)
    print(prec_dict)
    print(rec_dict)

    # folder = "finaldata"
    categories = devices
    cat_type = DEVICE
    acc_dict, prec_dict, rec_dict = get_accuracy_dict(folder, categories, cat_type, minPeakHeight=3, extra=[False, True])
    print(acc_dict)
    print(prec_dict)
    print(rec_dict)