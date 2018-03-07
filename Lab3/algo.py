from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels
from detector_wrapper import DetectorWrapper
import time
import numpy as np
from time import sleep

detector = DetectorWrapper()
front_wheels = Front_Wheels()
back_wheels = Back_Wheels()

# the angle of the turn is different for left and right turn,
#   and also if the lane midpoint is very far from the fixed midpoint
# if the lane midpoint is too far from the fixed midpoint, the car
#   will turn at a bigger angle
def turn(wheels, scales, direction, diff, sleep_time):
    right_soft, right_hard, right_threshold, left_soft, left_hard, left_threshold = scales
    if direction == RIGHT:
        if diff > right_threshold:
            scale = right_hard
        else:
            scale = right_soft
    elif direction == LEFT:
        if diff > left_threshold:
            scale = left_hard
        else:
            scale = right_hard
    else:
        scale = 0
    wheels.turn_rel(scale * direction)
    sleep(sleep_time)
    return

# determines next move of the car based on the lane midpoint and fixed frame midpoint.
# The thresholds are different between left and right side.
# The car turns left if the lane midpoint is left of the frame midpoint, and turns right if
#   the midpoint is on the right of the frame midpoint
def nextDir(frame_midpoint, curr_ret, thresholds):
    left_side_thres, right_side_thres = thresholds
    frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = curr_ret
    if mid_x < frame_midpoint * (1 - left_side_thres):
        return LEFT, frame_midpoint * (1 - left_side_thres) - mid_x
    elif mid_x > frame_midpoint * (1 + right_side_thres):
        return RIGHT, mid_x - frame_midpoint * (1 + right_side_thres)
    return STRAIGHT, 0

# runs nextDir and inputs the next direction into turn
def steer(frame_midpoint, speed_0, scales, thresholds, max_time, sleep_time=0.005, log=False, filename="out.txt"):
    init = time.time()
    front_wheels.turn_straight()
    back_wheels.speed = speed_0

    if log == True:
        all_arrs = []

    while True:
        if time.time() - init > max_time:
            back_wheels.stop()
            print("Error: time is finished")
            break
        else:
            try:
                success, ret = detector.detect()
                detector.plot(ret)
                if success:
                    move, diff = nextDir(frame_midpoint, ret, thresholds)
                    turn(front_wheels, scales, move, diff, sleep_time)
                else:
                    back_wheels.stop()
                    print("Stopped detecting lane")
            except Exception as e:
                back_wheels.stop()
                print("Can't detect: " + str(e))

        if log == True:
            frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = ret
            curr_arr = [time.time(), mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx]
            all_arrs.append(curr_arr)

    if log == True:
        all_arrs = np.array(all_arrs)
        np.savetxt(filename, all_arrs, delimiter=',')
    return

STRAIGHT = 0
RIGHT = 1
LEFT = -1

if __name__ == "__main__":
    # scales is the turning angle calculated based on how far the lane midpoint is from the frame midpoint 
    # we incorporate different threshholds between left and right turn

    # scales parameters:
    #     right turn soft angle
    #     right hard angle
    #     right diff threshold
    #     left turn soft angle
    #     left turn hard angle
    #     left turn diff threshold
    scales = (4.7, 11.61, 90, 2.7, 8.93, 90)

    # thresholds parameters:
    #     left side threshhold
    #     right side threshold
    thresholds = (0.10, 0.15)

    # steer parameters:
    #     frame_midpoint
    #     speed_0
    #     scales
    #     thresholds
    #     max_time
    #     sleep_time
    steer(330, 30, scales, thresholds, 360, 0.005)

