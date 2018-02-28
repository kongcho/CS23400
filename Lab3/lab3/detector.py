from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels
from detector_wrapper import DetectorWrapper

# --------- Basic Implementation --------------

# use mid-point of lane, curvature of lane, and car speed to 
# design an algorithm to control turning angle of the front wheels

# ----------------------------------------------


# returns steering angle necessary to stay in lane
def drive(ret):
    dir = direction(ret)
    if

# returns the direction the lane is turning
# calculate the curvature of a lane line, is to fit a 2nd degree polynomial to that line
def direction(ret):

    # ret returns mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx 
    # left_fit returns 3 values, 3 parameters of parabola of left lane
    # f(y) = Ay^2 + By + C
    # A gives us the curvature of the lane line, 
    # B gives us the heading or direction that the line is pointing
    # C gives us the position of the line based on how far away it is from the very left of the image

    left_fit = ret[1]
    right_ft = ret[2]

    if ret[0] == 1:
        return "straight"
    else if ret[0] == 2:
        return "left"
    else 
        return  "right"


def detect():
    try:
        detector = DetectorWrapper()

        front_wheels = Front_Wheels()
        back_wheels = Back_Wheels()

        while True:
            success, ret = detector.detect()
            detector.plot(ret)
            print(ret[1])

            # ret returns mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx 

            # mid_x is the mid point of the lane at the bottom border of a frame
            # left_fit & right_fit are the fitted parameters for the parabola curve returned from numpy.polyfit
            # left_fitx and right_fitx save the x position(horizontal, increase from left to right)

            angle = drive(ret)
            turn_rel(angle)

    except KeyboardInterrupt:
        print("KeboardInterrupt Captured")
    finally:
        detector.stop()
        back_wheels.stop()
        front_wheels.turn_straight()


if __name__ == '__main__':
    detect()



