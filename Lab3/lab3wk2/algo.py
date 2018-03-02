from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels
from detector_wrapper import DetectorWrapper
import time
import numpy as np

detector = DetectorWrapper()

front_wheels = Front_Wheels()
back_wheels = Back_Wheels()

# frame, mid_x , left_fit , right_fit , ploty , left_fitx , right_fitx

def get_curvature(fit, y_eval):
    a, b, c = fit
    curve_rad = ((1 + (2*a*y_eval + b)**2)**1.5) / np.absolute(2*a)

    print(curve_rad)
    return curve_rad

# turn left if detected lane center < middle etc
def middle_lane():
    print("START")
    init = time.time()
    drive = True
    front_wheels.turn_straight()
    back_wheels.speed = 50
    front_wheels.speed = 50
    while drive:
        success, ret = detector.detect()
        if time.time() - init > 5:
            back_wheels.stop()
            drive = False
        elif success == 0:
            back_wheels.stop()
            print("ERROR")
        else:
            lane_center = (ret[6] - ret[5]) / 2 + ret[5]
            dist_to_center = lane_center - mid_x
            print(dist_to_center)
            if dist_to_center < 0:
                # turn left
                back_wheels.speed = dist_to_center
                front_wheels.turn_rel(dist_to_center)
            else:
                # turn right
                back_wheels.speed = dist_to_center
                front_wheels.turn_rel(dist_to_center)
        print("END")
    return

# trying to see what kind of values u get
def get_vals():
#    back_wheels.stop()
    print("START")
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
                print(time.time())
                print("success: ")
#                print(success.shape) 
                print(success)
                print("ret: ")
#                print(ret.shape)
                print(ret)
#                print("left " + str(get_curvature(ret[2], ret[4])))
#                print("right " + str(get_curvature(ret[3], ret[4])))
                # detector.plot(ret[0])
            except Exception as e:
                print(e.message)
                back_wheels.stop()
                print("ERROR")
        print("END")
    return

if __name__ == "__main__":
#    middle_lane()

#    get_curvature()
    get_vals()
