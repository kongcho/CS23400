from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels
from detector_wrapper import DetectorWrapper


def drive(ret):
    frame = ret[0] 
    mid_x = ret[1]
    left_fit = ret[2]
    right_fit = ret[3]
    ploty = ret[4]
    left_fitx = ret[5]
    right_fitx = ret[6]


def detect():
    try:
        detector = DetectorWrapper()

        front_wheels = Front_Wheels()
        back_wheels = Back_Wheels()

        while True:
            success, ret = detector.detect()
            detector.plot(ret)
            print(ret[1])

            #ret is a tuple which contains frame, mid_x, 
            #left_fit, right_fit, ploty , left_fitx , right_fitx

            #frame is the current frame captured from the camera (returned from cap.read in OpenCV)
            #mid_x is the mid point of the lane at the bottom border of a frame
            #left_fit and right_fit are the fitted parameters for the parabola curve returned from
            #numpy.polyfit
            #left_fitx and right_fitx save the x position(horizontal, increase from left to right)
            drive(ret)

    except KeyboardInterrupt:
        print("KeboardInterrupt Captured")
    finally:
        detector.stop()
        back_wheels.stop()
        front_wheels.turn_straight()


if __name__ == '__main__':
    detect()



