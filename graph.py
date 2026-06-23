import matplotlib.pyplot as plt
import numpy as np
import pickle

import pandas as pd

red_dark    = [97 /255, 0  /255, 6  /255]
red_light   = [220/255, 100/255, 100/255]
orange_dark = [214/255, 40 /255, 40 /255]
orange      = [255/255, 127/255, 17 /255]
peach       = [255/255, 176/255, 144/255]
yellow      = [252/255, 191/255, 73 /255]

green_dark  = [91 /255, 126/255, 60 /255]
green_light = [100/255, 200/255, 100/255]

teal_dark   = [40 /255, 90 /255, 72 /255]
teal_medium = [64 /255, 138/255, 113/255]
teal_light  = [176/255, 228/255, 204/255]

blue_dark   = [56 /255, 82 /255, 180/255]
blue_light  = [100/255, 100/255, 220/255]

purple      = [93 /255, 28 /255, 106/255]
pink        = [202/255, 89 /255, 149/255]

black       = [50 /255, 51 /255, 57 /255]
true_black  = [0.1,0.1,0.1]
gray        = [150/255, 150/255, 150/255]
white       = [1, 1, 1]

size = (14,12)

graphPath = r"Graph/"

all_timings = {'t1': [0.003, 0.0015, 0.0009, 0.0008, 0.001, 0.0008, 0.0008, 0.0009, 0.0009, 0.0009], 
't2': [0.0069, 0.0052, 0.0019, 0.0015, 0.0018, 0.0016, 0.0016, 0.0017, 0.0017, 0.0016], 
't3': [0.0556, 0.0405, 0.0369, 0.0365, 0.0366, 0.0362, 0.0366, 0.0363, 0.0373, 0.0368], 
't4': [0.0572, 0.0422, 0.038, 0.0376, 0.0377, 0.0373, 0.0377, 0.0375, 0.0383, 0.038], 
't5': [0.0828, 0.0428, 0.0385, 0.0382, 0.0383, 0.0379, 0.0382, 0.038, 0.0389, 0.0386]}


def graph_timings(all_timings):
    print("graph")
    alpha = 1
    zorder = 20
    linewidth = 2.5

    fig, ax = plt.subplots(figsize=size)
    ax.set_title("time")

    print(all_timings)

    all_timings_length = []

    for key in range(len(all_timings["t1"])):
        all_timings_length.append(key)


    print(all_timings.values())

    ax.stackplot(all_timings_length, 
    all_timings.values(), 
    labels = all_timings.keys(),
    linewidth = 1,
    alpha =0.8)

    ax.grid(which = "major", alpha = 0.5, linestyle = "--", linewidth = 0.8,color = gray, zorder = 0)

    #plt.tight_layout()
    plt.savefig("Graph/time.png")
    plt.close()


#graph_timings(all_timings)