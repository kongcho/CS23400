from os import listdir
from os.path import isfile, join
import os
import re

def tryint(s):
    try:
        return int(s)
    except:
        return s
def alphanum_key(s):
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    l.sort(key=alphanum_key)
    return l

# renames a given folder to our naming standard
# log_fall-or-not_scenario_trial_device_person.txt
def rename(filepath, person):
    all_files = [filepath + f for f in listdir(filepath) if isfile(join(filepath, f))]
    sorted_files = sort_nicely(all_files)
    count = 0
    scenario = 10
    for filename in all_files:
        if count == 3:
            count = 0
            scenario += 1
        os.rename(filename, filepath + "log_1_" + str(scenario) + "_" + str(count) + "_1" + "_" + str(person) + ".txt")
        count += 1

if __name__ == "__main__":
    rename("./FallNajee/",11)
