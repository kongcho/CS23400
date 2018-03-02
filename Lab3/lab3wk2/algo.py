from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels
from detector_wrapper import DetectorWrapper
import time
import numpy as np

detector = DetectorWrapper()
front_wheels = Front_Wheels()
back_wheels = Back_Wheels()

# frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx

def get_curvature(fit, y):
    a, b, c = fit
    curve_rad = ((1 + (2*a*y + b)**2)**1.5) / np.absolute(2*a)
    return curve_rad

# trying to see what kind of values u get
def get_vals():
    print("START")
    init = time.time()
    drive = True
    front_wheels.turn_straight()
    back_wheels.speed = 50
    front_wheels.speed = 50
    while drive:
        if time.time() - init > 5:
            back_wheels.stop()
            print("END of time")
            drive = False
        else:
            try:
                back_wheels.forward()
                success, ret = detector.detect()
                print(ret[0].shape)
                print(ret[4].shape)
                print(ret[5].shape)
                print(ret[6].shape)
                print(ret[:4])
            except Exception as e:
                back_wheels.stop()
                print(e)
                print("ERROR")
        print("END")
    return

def turn(wheels, scale, direction):
    wheels.turn_rel(scale * direction)
    sleep(.01)
    return

STRAIGHT = 0
LEFT = -1
RIGHT = 1

def nextDir(frame_midpoint, curr_ret):
    THRESHOLD = 0.2
    frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = ret
    # curve_left = get_curvature(left_fit, left_fitx[-1])
    # curve_right = get_curvature(right_fit, right_fit[-1])
    if mid_x < frame_midpoint * (1 - THRESHOLD):
        return RIGHT
    elif mid_x > frame_midpoint * (1 + THRESHOLD):
        return LEFT
    return STRAIGHT


def steer(frame_midpoint, speed_0, scale, log=False, filename="out.txt"):
    init = time.time()
    front_wheels.turn_straight()
    #TO CHANGE
    back_wheels.speed = speed_0
    front_wheels.speed = speed_0

    if log == True:
        print("START")
        all_arrs = []

    while True:
        # TO CHANGE MAX TIME
        if time.time() - init > 5:
            back_wheels.stop()
            print("FINISH TIME")
            break
        else:
            try:
                success, ret = detector.detect()
                if success:
                    move = nextDir(frame_midpoint, ret)
                    if move == LEFT:
                        turn(front_wheels, scale, LEFT)
                    elif move == RIGHT:
                        turn(front_wheels, scale, RIGHT)
                    else:
                        back_wheels.forward()
            except Exception as e:
                back_wheels.stop()
                print("ERROR")
                print(str(e))

        if log == True:

            frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = ret
            curve_left = get_curvature(left_fit, left_fitx[-1])
            curve_right = get_curvature(right_fit, right_fit[-1])
            curr_arr = [time.time(), mid_x, left_fit, right_fit, curve_left, curve_right, ploty, left_fitx, right_fitx]
            all_arrs.append(curr_arr)
            print(curr_arr[:6])

    if log == True:
        all_arrs = np.array(all_arrs)
        np.savetxt(filename, all_arrs, delimiter=',')


def log_vals(filename):
    print("START")
    init = time.time()
    drive = True
    is_first = True
    all_arrs = []
    front_wheels.turn_straight()
    #TO CHANGE
    back_wheels.speed = 50
    front_wheels.speed = 50
    while drive:
        # TO CHANGE MAX TIME
        if time.time() - init > 5:
            back_wheels.stop()
            print("FINISH TIME")
            drive = False
        else:
            try:
                # INSTRUCTIONS
                back_wheels.forward()

                # TURN LEFT
#                back_wheels.forward()
#                back_wheels.speed = 50
#                front_wheels.turn_rel(-50)
#                time.sleep(0.01)

                # BETTER LEFT
#                for i in range(70, 90, 1):
#                    back_wheels.speed = (90 - i) * 4
#                    front_wheels.turn(i)
#                    time.sleep(3. / 20)

                # OTHER
                success, ret = detector.detect()
                if success:
                    frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = ret
                    curve_left = get_curvature(left_fit, left_fitx[-1])
                    curve_right = get_curvature(right_fit, right_fit[-1])
                    curr_arr = [time.time(), mid_x, left_fit, right_fit, curve_left, curve_right, ploty, left_fitx, right_fitx]
                    all_arrs.append(curr_arr)
                    print(curr_arr[:6])

                    # midpoint based on initial mid-point
                    if is_first:
                        midpoint = mid_x
                        is_first = False
                        continue

#                    # CHANGE BASED ON MIDDLE

#                    # turn left
#                    if mid_x < midpoint:
#                        for i in range(70, 80, 1):
#                            back_wheels.speed = (90 - i) * 4
#                            front_wheels.turn(-i)
#                            time.sleep(0.01)
#                    # turn right
#                    else:
#                        for i in range(70, 80, 1):
#                            back_wheels.speed = (90 - i) * 4
#                            front_wheels.turn(i)
#                            time.sleep(0.01)

#                    # CHANGE BASED ON AVERAGES
#                    lefts = left_fitx[130:140]
#                    rights = right_fitx[130:140]
#                    avg = np.average(np.divide(np.subtract(lefts, rights), 2)) + np.average(lefts)

                else:
                    print("FAILED SUCCESS")
            except Exception as e:
                back_wheels.stop()
                print("ERROR")
                print(str(e))
    all_arrs = np.array(all_arrs)
    np.savetxt(filename, all_arrs, delimiter=',')
    return

if __name__ == "__main__":
    steer(1.,1.,1.)
