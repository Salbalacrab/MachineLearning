#!/usr/bin/env python3
# coding: utf-8

from time import sleep

from ev3dev.auto import *
import os

left_motor = LargeMotor(OUTPUT_B);  assert left_motor.connected
right_motor = LargeMotor(OUTPUT_C); assert right_motor.connected
ts = TouchSensor();    	assert ts.connected
col= ColorSensor(); 	assert col.connected
col.mode = 'COL-REFLECT'
btn = Button()

power = 30
target = 55
kp = float(0.65) 
kd = 1           
ki = float(0.30) 
direction = -1
minRef = 41
maxRef = 63


def steering(course, power):
	power_left = power_right = power
	s = (50 - abs(float(course))) / 50

	if course >= 0:
		power_right *= s
		power_left = power
		if course > 100:
			power_right = - power
			power_left = power
	else:
		power_left *= s
		power_right = power			
		if course < -100:
			power_left = - power
			power_right = power			

	return (int(power_left), int(power_right))

def run(power, target, kp, kd, ki, direction, minRef, maxRef):
    
	lastError = error = integral = 0
	left_motor.run_direct()
	right_motor.run_direct()
	while not ts.value() :
		refRead = col.value()
		error = target - (100 * ( refRead - minRef ) / ( maxRef - minRef ))
		derivative = error - lastError
		lastError = error
		integral = float(0.5) * integral + error
		course = (kp * error + kd * derivative +ki * integral) * direction
		for (motor, pow) in zip((left_motor, right_motor), steering(course, power)):
			motor.duty_cycle_sp = pow
		sleep(0.01) # Aprox 100 Hz
		# Write sensor data to text file
		f.write(str(col.value()) + "," + str(col.value()) + "," + str(left_motor.speed) + "," + str(right_motor.speed) + "\n")



f= open("/home/robot/ai-for-ev3-master/data/digits/1_.txt", "w+") 

run(power, target, kp, kd, ki, direction, minRef, maxRef)
left_motor.stop()
right_motor.stop()