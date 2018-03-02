from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels
from detector_wrapper import DetectorWrapper

# --------- Basic Implementation --------------

# use mid-point of lane, curvature of lane, and car speed to 
# design an algorithm to control turning angle of the front wheels

# ----------------------------------------------

# set these values after testing?

window_mid = 250    # midpoint of the window
window_offset = 5   # level of sensitivity to midpoint of window
time_offset = 1     # time offset for steering
speed = 30          # baseline speed level


def drive(ret):

    mid_x = ret[1]  # midpoint of the lane at the bottom border of a frame

    # if midpoint of lane is to the right of the frame
    if (mid_x > window_mid + window_offset):
        front_wheels.turn_right()

    # if midpoint of lane is to the left of the frame
    if (mid_x < window_mid - window_offset):
        front_wheels.turn_left()

    # if midpoint of lane is relatively in the center
    else:
        front_wheels.turn_straight()

    time.sleep(time_offset)


# returns steering angle necessary to stay in lane
def turn_dir(ret):

    # calculate the curvature of a lane line, is to fit a 2nd degree polynomial to that line

    # left_fit returns 3 values, 3 parameters of parabola of left lane
    # f(y) = Ay^2 + By + C
    # A gives us the curvature of the lane line, 
    # B gives us the heading or direction that the line is pointing
    # C gives us the position of the line based on how far away it is from the very left of the image


    left_fit = ret[2] # parameters for left lane
    left_a = left_fit[0]
    left_b = left_fit[1]
    left_c = left_fit[2]


    right_ft = ret[3] # parameters for right lane
    right_a = right_fit[0]
    right_b = right_fit[1]
    right_c = right_fit[2]

    # how to calculate curvature of lane??
    curvature = (left_a + right_b)/2

    # how is direction of wheel turn related to lane curvature?
    # 0 < rel_angle < 30
    direction = curvature/10

    return direction



def detect():
    try:
        detector = DetectorWrapper()

        front_wheels = Front_Wheels()
        back_wheels = Back_Wheels()

        #start driving
        front_wheels.turn_straight()
        back_wheels.speed = speed
        back_wheels.forward()

        while True:
            success, ret = detector.detect()
            detector.plot(ret)
            print(ret[1])

            # ret returns frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx 

            # mid_x is the mid point of the lane at the bottom border of a frame
            # left_fit & right_fit are the fitted parameters for the parabola curve returned from numpy.polyfit
            # left_fitx and right_fitx save the x position(horizontal, increase from left to right)

            # turns front wheels left, right, or straight
            drive(ret)

            # other option: turn wheels using angle calculation from curvature of lane

            #angle = direction(ret)
            #turn_rel(angle)

    except KeyboardInterrupt:
        print("KeboardInterrupt Captured")
    finally:
        detector.stop()
        back_wheels.stop()
        front_wheels.turn_straight()


if __name__ == '__main__':
    detect()



