#!/usr/bin/env python3

import os
import json
import regex as re
import matplotlib.pyplot as plt

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

def sep_files_by_peak(folder, timeInterval=1.5, minPeakHeight=25):
    no_peaks = []
    one_peak = []
    mult_peaks = []
    for file in os.listdir(folder):
        filepath = os.path.join(folder, file)
        with open(filepath) as f:
            data = f.read().split("\n")
        abso = GyroOrAccel("Linear", data, file)
        if abso.hasMultiplePeaks(timeInterval=timeInterval, minPeakHeight=minPeakHeight):
            mult_peaks.append(file)
        elif abso.hasPeak(timeInterval=timeInterval, minPeakHeight=minPeakHeight):
            one_peak.append(file)
        else:
            no_peaks.append(file)
    return {"no peaks": no_peaks,
        "one peak": one_peak,
        "multiple peaks": mult_peaks}

def sep_files_by_type_and_peak(folder, timeInterval=1.5, minPeakHeight=25, group_by=[POSITIVE]):
    num_peaks_dict = sep_files_by_peak(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight)
    ret_dict = {}
    for num_key in num_peaks_dict:
        files = num_peaks_dict[num_key]
        separated = separate_files(files, group_by=group_by)
        ret_dict[num_key] = separated
    return ret_dict

def get_num_detected_each_cat(folder, timeInterval=1.5, minPeakHeight=25, group_by=[POSITIVE]):
    separated = sep_files_by_type_and_peak(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=group_by)
    ret_dict = {}
    for num_key in separated:
        ret_dict[num_key] = []
        for item in separated[num_key]:
            item_dict = {"label": item["label"], "num": len(item["files"])}
            ret_dict[num_key].append(item_dict)
    return ret_dict

def get_recall(folder, timeInterval=1.5, minPeakHeight=25):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=[POSITIVE])
    total_falls = 0 
    for item in detection_dict["one peak"]:
        if item["label"] == "Fall":
            true_positives = item["num"]
    for key in detection_dict:
        for item in detection_dict[key]:
            if item["label"] == "Fall":
                total_falls += item["num"]
    return float(true_positives)/total_falls

def get_precision(folder, timeInterval=1.5, minPeakHeight=25):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=[POSITIVE])
    total_trials = detection_dict["one peak"][0]["num"] + detection_dict["one peak"][1]["num"] \
        + detection_dict["no peaks"][0]["num"] + detection_dict["no peaks"][1]["num"] \
        + detection_dict["one peak"][0]["num"] + detection_dict["one peak"][1]["num"]
    for item in detection_dict["one peak"]:
        if item["label"] == "Fall":
            true_positives = item["num"]
    return float(true_positives)/total_detections

def get_truths(folder, timeInterval=1.5, minPeakHeight=25):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=[POSITIVE])
    total_detections = detection_dict["one peak"][0]["num"] + detection_dict["one peak"][1]["num"]
    for item in detection_dict["one peak"]:
        if item["label"] == "Fall":
            true_positives = item["num"]
    return float(true_positives)/total_detections


def get_recall_and_precision(folder, timeInterval=1.5, minPeakHeight=25, group_by=[POSITIVE], phrase=""):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=group_by)
    # print(json.dumps(detection_dict, indent=4))
    total_falls = 0 
    true_positives = None
    for item in detection_dict["one peak"]:
        if "Fall" in item["label"] and phrase in item["label"]:
            true_positives = item["num"]
    if true_positives is None:
        return -1., -1.
    for key in detection_dict:
        for item in detection_dict[key]:
            if "Fall" in item["label"] and phrase in item["label"]:
                total_falls += item["num"]
    recall = float(true_positives)/total_falls
    total_detections = detection_dict["one peak"][0]["num"] + detection_dict["one peak"][1]["num"]
    for item in detection_dict["one peak"]:
        if "Fall" in item["label"] and phrase in item["label"]:
            true_positives = item["num"]
    precision = float(true_positives)/total_detections
    return recall, precision

def get_truth_by_category(categories, first_fall_cat):
    detection_dict = get_num_detected_each_cat(folder, timeInterval=1.5, minPeakHeight=minPeakHeight, group_by=[POSITIVE, SCENARIO])
    pos_dict = {}
    neg_dict = {}
    for cat_idx in range(len(categories)):
        cat = categories[cat_idx]
        if cat_idx < first_fall_cat:
            true_key = "no peaks"
            false_key = "one peak"
        else:
            true_key = "one peak"
            false_key = "no peaks"
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

def print_results(folder, timeInterval=1.5, minPeakHeight=25, group_by=[POSITIVE, SCENARIO]):
    print(get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=[POSITIVE]))
    print("\n")
    print(json.dumps(get_num_detected_each_cat(folder, timeInterval=timeInterval, minPeakHeight=minPeakHeight, group_by=group_by), indent=4))

if __name__ == '__main__':
    folder = "finaldata"
    categorize_file(file_1)
    files = [file_1, file_2, file_3, file_4]
    # print(separate_files(files, group_by=[POSITIVE, SCENARIO]))
    minPeakHeight = 16
    neg_dict, pos_dict = get_truth_by_category(scenarios, 10)
    # print(json.dumps(D, indent=4))

    for D in [neg_dict, pos_dict]:
        plt.bar(range(len(D)), list(D.values()), align='center')
        plt.xticks(range(len(D)), list(D.keys()))
        plt.show()

    # for scenario in scenarios:
    #     # print("minPeakHeight: %d" % minPeakHeight)
    #     # print_results(folder, timeInterval=1.5, minPeakHeight=minPeakHeight, group_by=[POSITIVE, DEVICE])
    #     recall, precision = get_recall_and_precision(folder, timeInterval=1.5, group_by=[POSITIVE, SCENARIO], minPeakHeight=minPeakHeight, phrase=scenario)
    #     print("%s accuracy\n\trecall: %f, precision: %f" % (scenario, recall, precision))

    # print(get_num_detected_each_cat("finaldata"))
    # print(get_precision("finaldata"))
    # print(get_recall("finaldata"))
    # print(optimize_recall_and_precision(folder))