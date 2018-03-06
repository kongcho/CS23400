from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels
from detector_wrapper import DetectorWrapper
import time
import numpy as np
from time import sleep

detector = DetectorWrapper()
front_wheels = Front_Wheels()
back_wheels = Back_Wheels()

def get_curvature(fit, y):
    a, b, c = fit
    curve_rad = ((1 + (2*a*y + b)**2)**1.5) / np.absolute(2*a)
    return curve_rad

# getting the frame sizes of the images
def get_vals():
    init = time.time()
    drive = True
    front_wheels.turn_straight()
    back_wheels.speed = 50
    front_wheels.speed = 50
    while drive:
        if time.time() - init > 5:
            back_wheels.stop()
            drive = False
        else:
            try:
                back_wheels.forward()
                success, ret = detector.detect()
                # see what is frame size to see frame midpoint
                print(ret[0].shape)
            except Exception as e:
                back_wheels.stop()
                print(e)
    return

# turns by different angles (soft/hard) based on whether the midpoint is far enough from frame midpoint
def turn(wheels, scales, direction, diff, sleep_time):
    left_soft, left_hard, left_threshold, right_soft, right_hard, right_threshold = scales
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
    wheels.turn_rel(scale * direction)
    sleep(sleep_time)
    return

def nextDir(frame_midpoint, curr_ret, thresholds):
    left_side_thres, right_side_thres = thresholds
    frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = curr_ret
    curve_left = get_curvature(left_fit, left_fitx[-1])
    curve_right = get_curvature(right_fit, right_fit[-1])
    print(frame_midpoint * (1 - left_side_thres), mid_x, frame_midpoint * (1 + right_side_thres), curve_left, curve_right)
    if mid_x < frame_midpoint * (1 - left_side_thres):
        return RIGHT, frame_midpoint * (1 - left_side_thres) - mid_x
    elif mid_x > frame_midpoint * (1 + right_side_thres):
        return LEFT, mid_x - frame_midpoint * (1 + right_side_thres)
    return STRAIGHT, 0

def steer(frame_midpoint, speed_0, scales, thresholds, maxtime, sleep_time=0.005, log=False, filename="out.txt"):
    init = time.time()
    front_wheels.turn_straight()
    back_wheels.speed = speed_0

    if log == True:
        all_arrs = []

    while True:
        if time.time() - init > maxtime:
            back_wheels.stop()
            print("FINISH TIME")
            break
        else:
            try:
                success, ret = detector.detect()
                detector.plot(ret)
                if success:
                    move, diff = nextDir(frame_midpoint, ret, thresholds)
                    print(move, diff)
                    turn(front_wheels, scales, move, diff, sleep_time)
                else:
                    back_wheels.stop()
                    print("CANT DETECT LANE")
            except Exception as e:
                back_wheels.stop()
                print("TRY FAILED: " + str(e))

        if log == True:
            frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = ret
            curve_left = get_curvature(left_fit, left_fitx[-1])
            curve_right = get_curvature(right_fit, right_fit[-1])
            curr_arr = [time.time(), mid_x, left_fit, right_fit, curve_left, curve_right, ploty, left_fitx, right_fitx]
            all_arrs.append(curr_arr)

    if log == True:
        all_arrs = np.array(all_arrs)
        np.savetxt(filename, all_arrs, delimiter=',')
    return

# steer based on changing midpoint from last time
def steer_mid(frame_midpoint, speed_0, scales, thresholds, maxtime, sleep_time=0.005, log=False, filename="out.txt"):
    init = time.time()
    front_wheels.turn_straight()
    back_wheels.speed = speed_0
    midpoint = frame_midpoint

    if log == True:
        all_arrs = []

    while True:
        if time.time() - init > maxtime:
            back_wheels.stop()
            print("FINISH TIME")
            break
        else:
            try:
                success, ret = detector.detect()
                detector.plot(ret)
                if success:
                    move, diff = nextDir(midpoint, ret, thresholds)
                    print(move, diff)
                    turn(front_wheels, scales, move, diff, sleep_time)
                    midpoint = ret[1]
                else:
                    back_wheels.stop()
                    print("CANT DETECT LANE")
            except Exception as e:
                back_wheels.stop()
                print("TRY FAILED: " + str(e))

        if log == True:
            frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = ret
            curve_left = get_curvature(left_fit, left_fitx[-1])
            curve_right = get_curvature(right_fit, right_fit[-1])
            curr_arr = [time.time(), mid_x, left_fit, right_fit, curve_left, curve_right, ploty, left_fitx, right_fitx]
            all_arrs.append(curr_arr)

    if log == True:
        all_arrs = np.array(all_arrs)
        np.savetxt(filename, all_arrs, delimiter=',')
    return

# steer based on future midpoint (average)
def steer_future(frame_midpoint, speed_0, scales, thresholds, maxtime, sleep_time=0.005, log=False, filename="out.txt"):
    init = time.time()
    front_wheels.turn_straight()
    back_wheels.speed = speed_0
    midpoint = frame_midpoint

    if log == True:
        all_arrs = []

    while True:
        if time.time() - init > maxtime:
            back_wheels.stop()
            print("FINISH TIME")
            break
        else:
            try:
                success, ret = detector.detect()
                detector.plot(ret)
                if success:
                    lefts = ret[5][130:140]
                    rights = ret[6][130:140]
                    avg = np.average(np.divide(np.subtract(lefts, rights), 2)) + np.average(lefts)
                    ret[1] = avg
                    move, diff = nextDir(midpoint, ret, thresholds)
                    print(move, diff)
                    turn(front_wheels, scales, move, diff, sleep_time)
                    midpoint = ret[1]
                else:
                    back_wheels.stop()
                    print("CANT DETECT LANE")
            except Exception as e:
                back_wheels.stop()
                print("TRY FAILED: " + str(e))

        if log == True:
            frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = ret
            curve_left = get_curvature(left_fit, left_fitx[-1])
            curve_right = get_curvature(right_fit, right_fit[-1])
            curr_arr = [time.time(), mid_x, left_fit, right_fit, curve_left, curve_right, ploty, left_fitx, right_fitx]
            all_arrs.append(curr_arr)

    if log == True:
        all_arrs = np.array(all_arrs)
        np.savetxt(filename, all_arrs, delimiter=',')
    return


STRAIGHT = 0
LEFT = 1
RIGHT = -1

if __name__ == "__main__":
    # scales is the turning angle calculated based on how far the lane midpoint is from the frame midpoint 
    # we incorportae different threshholds between left and right turn
    
    # scales parameters:
    #     left turn soft angle
    #     left hard angle
    #     left diff threshold
    #     right turn soft angle
    #     right turn hard angle
    #     right turn diff threshold
    scales = (4.7, 11.61, 90, 4.7, 8.93, 90)

    # thresholds parameters:
    #     left side threshhold
    #     right side threshold
    thresholds = (0.17, 0.17)

    # steer parameters:
    #     frame_midpoint
    #     speed_0
    #     scales
    #     thresholds

    steer(260, 30, scales, thresholds)      # frame_midpoint = 250 for right turn
    # steer_mid(260, 30, scales, thresholds)
    # steer_future(260, 30, scales, thresholds)

