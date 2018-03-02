from mypicar.front_wheels import Front_Wheels
from mypicar.back_wheels import Back_Wheels

import time

front_wheels = Front_Wheels()
back_wheels = Back_Wheels()

try:
	# set front_wheels back to straight
	front_wheels.turn_straight()
	# first part
	# set the speed to 50
	back_wheels.speed= 50
	front_wheels.turn_left()
	back_wheels.forward()
	time.sleep(4)
	back_wheels.stop()
	# seconde part
	# set the speed to 50
	back_wheels.speed= 50
	front_wheels.turn_right()
	back_wheels.backward()
	time.sleep(4)
	back_wheels.stop()
	# third part
	back_wheels.forward()
	for i in range(70, 90, 1):
		back_wheels.speed = (90-i) *4
		front_wheels.turn(i)
		time.sleep(3./20)
	back_wheels.stop()
except:
	print "encountered error or interrupted, motor stop, turn straight"
	back_wheels.stop()
