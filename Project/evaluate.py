#!/usr/bin/env python3

import os
import regex as re
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

def positive_to_string(pos):
    if pos == 1:
        return "Fall"
    elif pos == 0:
        return "Not fall"
    else:
        raise ValueError("Positive value must be 0 or 1")

def scenario_to_string(scenario):
    if scenario == 0:
        return "Sitting slow"
    elif scenario == 1:
        return "Sitting fast"
    elif scenario == 2:
        return "Cheer up only"
    elif scenario == 3:
        return "Cheer up and down"
    elif scenario == 4:
        return "Punch out only"
    elif scenario == 5:
        return "Punch out and in"
    elif scenario == 6:
        return "Squat sit"
    elif scenario == 7:
        return "Dab"
    elif scenario == 8:
        return "Walking down single step"
    elif scenario == 9:
        return "Walking down 5 steps"
    elif scenario == 10:
        return "Front fall, no catch"
    elif scenario == 11:
        return "Front fall, catch"
    elif scenario == 12:
        return "Side fall, no catch"
    elif scenario == 13:
        return "Side fall, catch"
    elif scenario == 14:
        return "Back fall, no roll"
    elif scenario == 15:
        return "Back fall, with roll"
    elif scenario == 16:
        return "Pushed fall front"
    elif scenario == 17:
        return "Pushed fall side"
    elif scenario == 18:
        return "Jump fall"
    elif scenario == 19:
        return "Front knee fall"
    elif scenario == 20:
        return "Dive roll"
    elif scenario == 21:
        return "Uncategorized fall"
    else:
        raise ValueError("Invalid scenario value")

def device_to_string(device):
    if device == 0:
        return "Natalia's phone"
    elif device == 1:
        return "Cho Yin's phone"
    else:
        raise ValueError("Invalid device value")

def person_to_string(person):
    if person == 0:
        return "Natalia"
    elif person == 1:
        return "Cho Yin"
    elif person == 2:
        return "Lucy"
    elif person == 3:
        return "Poorvaja"
    elif person == 4:
        return "Catherine"
    elif person == 5:
        return "Roberto"
    elif person == 6:
        return "Han Bin"
    elif person == 7:
        return "Andre"
    elif person == 8:
        return "Clay"
    elif person == 9:
        return "Annalie"
    elif person == 10:
        return "Karlyn"
    elif person == 11:
        return "Najee"
    elif person == 12:
        return "Gamal"
    elif person == 13:
        return "Daniel"
    elif person == 14:
        return "Gaibo"
    elif person == 15:
        return "Aaron"
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

def sep_files_by_peak(folder):
    no_peaks = []
    one_peak = []
    mult_peaks = []
    for file in os.listdir(folder):
        filepath = os.path.join(folder, file)
        with open(filepath) as f:
            data = f.read().split("\n")
        abso = GyroOrAccel("Absolute", data, file)
        if abso.hasMultiplePeaks():
            mult_peaks.append(file)
        elif abso.hasPeak():
            one_peak.append(file)
        else:
            no_peaks.append(file)
    return {"no peaks": no_peaks,
        "one peak": one_peak,
        "multiple peaks": mult_peaks}

def sep_files_by_type_and_peak(folder, group_by=[POSITIVE]):
    num_peaks_dict = sep_files_by_peak(folder)
    ret_dict = {}
    for num_key in num_peaks_dict:
        files = num_peaks_dict[num_key]
        separated = separate_files(files, group_by=group_by)
        ret_dict[num_key] = separated
    return ret_dict

def print_num_detected_each_cat(folder, group_by=[POSITIVE]):
    separated = sep_files_by_type_and_peak(folder, group_by=group_by)
    for num_key in separated:
        print(num_key)
        for item in separated[num_key]:
            print("\t%s: %d" % (item["label"], len(item["files"])))


if __name__ == '__main__':
    categorize_file(file_1)
    files = [file_1, file_2, file_3, file_4]
    # print(separate_files(files, group_by=[POSITIVE, SCENARIO]))
    print_num_detected_each_cat("finaldata", group_by=[POSITIVE, SCENARIO])