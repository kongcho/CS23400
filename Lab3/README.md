﻿# Lab3: Self Driving Car
## Team 2: Natalia Kisanga, Cho Yin Kong, Lucy Newman


## Summary
In this lab, we built an algorithm for a self-driving car that detects and moves along a lane. We first wrote a basic algorithm comparing the midpoint of the lane to the midpoint of the frame in deciding the angle to turn the car’s wheels. Through testing our code on the cars during lab, we were able to find the optimal parameters for scaling the turn angle and threshold values to make the car smoothly follow the lane.


## Algorithm


Our algorithm uses the `steer` function which takes in various parameters we gathered through testing the car on the lane. We continually run the given lane detection algorithm and compare the midpoint of the detected lane to the midpoint of the frame in order to determine which direction the car should turn. The return of lane detection is passed to `nextDir`, whose return indicates whether the detected midpoint was to the left of the midpoint or to the right, and by how much. The results of `nextDir` are then passed to `turn`, which determines whether and by how much the car should turn, and tells the wheels to do so. The car continues to run until it stops detecting any lane.


To adjust for sensitivity and different curvatures from different directions of turning, we made variables for right difference threshold and left difference threshold. If the detected lane’s midpoint is to the left of the window, it returns a left turn, and if it is to the right of the window, it returns a right turn. The wheels turn with `wheels.turn_rel(angle * direction)`, and `direction` is `-1` for a left turn and `1` for a right turn. Otherwise, if the lane midpoint is within the window, it continues going straight. We also have another threshold for how far the lane's midpoint is to the frame midpoint. If it is too far, we use a hard angle turn so the car turns more. Otherwise, we use the soft angle and turn less. 


## Parameters


Scales parameters:
1. Right turn soft angle: how much to scale the soft right turn angle by
2. Right turn hard angle: how much to scale the hard right turn angle by
3. Right turn difference threshold: threshold of the difference between midpoints for differentiating between right soft and hard turn 
4. Left turn soft angle: how much to scale the soft left turn angle by
5. Left turn hard angle: how much to scale the hard left turn angle by
6. Left turn difference threshold: threshold of the difference between midpoints for differentiating between left soft and hard turn 


Threshold parameters:
1. Left side threshold: soft threshold for the left side of the window before turning
2. Right side threshold: soft threshold for the right side of the window before turning


Steer parameters:
1. Frame midpoint: midpoint of the camera frame
2. Speed: speed of the car, is constant
2. Scales: scales parameters (listed above)
3. Thresholds: threshold parameters (listed above)
4. Max time: how long until the car stops moving
5. Sleep time: how long to sleep after each turn command


## Running the code


Run `algo.py` from the `~/team2/lab3` directory on our bot.
