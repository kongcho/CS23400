from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels
from detector_wrapper import DetectorWrapper

try:
    detector = DetectorWrapper()

    front_wheels = Front_Wheels()
    back_wheels = Back_Wheels()

    while True:
        success, ret = detector.detect()
        detector.plot(ret)
        print(ret[1])

except KeyboardInterrupt:
    print("KeboardInterrupt Captured")
finally:
    detector.stop()
    back_wheels.stop()
    front_wheels.turn_straight()
