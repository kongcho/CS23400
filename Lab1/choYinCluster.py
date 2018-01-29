#!/usr/bin/env python
import ast
import matplotlib.pyplot as plt
import scipy.cluster.vq as vq
import numpy as np
from nfft import ndft

activities = ["Driving", "Jumping", "Standing", "Walking"]
files = ["./data/activity-dataset-" + activity + ".txt" for activity in activities]
data_types = ["xGyro", "yGyro", "xAccl", "xMag", "zAccl", "yAccl", "zGyro", "yMag", "zMag"]

def process_times(old_times):
    times = []
    time0 = old_times[0]
    for time in old_times:
        times.append(time - time0)
    return old_times

def get_test_datas(filename):
    data_type = "zGyro"
    no_of_data = 2

    short_dicts = []
    with open(filename, 'r') as f:
        all_data = ast.literal_eval(f.read())
        short_dicts = all_data[:no_of_data]
    test_data = []
    data = []
    times = []
    for i in range(no_of_data):
        curr_dicts = short_dicts[i]["seq"]
        times = []
        t0 = curr_dicts[0]["time"]
        for j in range(len(curr_dicts)):
            times.append(curr_dicts[j]["time"] - t0)
            data.append(curr_dicts[j]["data"][data_type])
        test_data.append([times, data])
    return test_data

def get_test_data(filename):
    data_type = "zGyro"
    index_of_data = 4

    short_dicts = []
    with open(filename, 'r') as f:
        all_data = ast.literal_eval(f.read())
        short_dicts = all_data[index_of_data]
    test_data = []
    data = []
    times = []
    curr_dicts = short_dicts["seq"]
    times = []
    t0 = curr_dicts[0]["time"]
    for j in range(len(curr_dicts)):
        times.append(curr_dicts[j]["time"] - t0)
        data.append(curr_dicts[j]["data"][data_type])
    test_data.append([times, data])
    return test_data

def write_test_data(filenames):
    all_data = []
    with open("test_data.txt", 'w') as f:
        for filename in filenames:
            all_data += get_test_datas(filename)
        f.write(str(all_data))
    return all_data

def one_zGyro_data(filename):
    with open(filename, 'r') as f:
        all_data = ast.literal_eval(f.read())
    return all_data

def get_dft(all_arrays):
    # The number of frequencies at which to evaluate the result
    no_freqs = 4
    freqs = []
    for i, arrays in enumerate(all_arrays):
        length = len(arrays[0])//2
        if length % 2 != 0:
            length = length - 1
        amps = ndft(arrays[0][:length], arrays[1][:length])
        freqs.append([arrays[1][:length], amps])
    return freqs

def plot_everything(all_arrays):
    fig, ax = plt.subplots(1, 1)
    for i, arrays in enumerate(all_arrays):
        ax.scatter(arrays[0], arrays[1], s=5, label = i)
    plt.legend(loc='upper right')
    plt.show()

def get_kmeans(arrays):
    arrxy = np.array(zip(arrays[0], arrays[1]))
    centroids, label = vq.kmeans2(arrxy, 4)

    colors = ([([0.4,1,0.4],[1,0.4,0.4],[0.1,0.8,1],[0.5,0.8,1])[i] for i in label])
    plt.scatter(arrxy[:,0], arrxy[:,1], c=colors)
    plt.scatter(centroids[:,0],centroids[:,1], marker='o', s = 300, linewidths=1, c='none')
    plt.scatter(centroids[:,0],centroids[:,1], marker='x', s = 300, linewidths=1)
    plt.show()

if __name__ == '__main__':
    # write_test_data(files)
    plot_everything(get_dft(one_zGyro_data("test_data.txt")))
    # test = [[1, 1, 1.2, 3, 5, 6, 7, 9, 8], [5, 6, 3, 2, 4, 5, 8, 10, 2]]
    # get_kmeans(test)
    pass
