#!/usr/bin/env python3
# coding: utf-8

from time import sleep

from ev3dev.ev3 import *	
import os
import numpy as np
import sklearn
import pickle

left_motor = LargeMotor(OUTPUT_B);  assert left_motor.connected
right_motor = LargeMotor(OUTPUT_C); assert right_motor.connected
# Change color sensor mode
col.mode = 'COL-REFLECT'
btn = Button()
ts = TouchSensor();    	assert ts.connected
col= ColorSensor(); 	assert col.connected
power = 30
target = 55
kp = float(0.65) # gain moteur %
kd = 1           # dérive
ki = float(0.30) # gaint moteur int
direction = -1
minRef = 41
maxRef = 63


# Line follower 
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
	sensor1=0
	sensor2=0
	mid_sensor = 0
	left_motor_count = 0
	right_motor_count = 0

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

		sensor1 += col.value()
		mid_sensor += col.value()
		sensor2 += col.value()
		left_motor_count += left_motor.speed
		right_motor_count += right_motor.speed

		sleep(0.1)

	left_motor.stop()
	right_motor.stop()

	# Unification des donnée 
	sensor1 = sensor1 / 533
	mid_sensor = mid_sensor / 533
	sensor2 = sensor2 / 533
	left_motor_count = left_motor_count / 533
	right_motor_count = right_motor_count / 533

	X_new = [[sensor1, sensor2, mid_sensor, left_motor_count, right_motor_count]]

	# Load .sav, .pkl
	loaded_model = pickle.load(open('./formes_model/trained_model.sav', 'rb'))
	loaded_scaler = pickle.load(open('./formes_model/mlp_scaler.pkl', 'rb'))

	# Apply scaler
	X_new = loaded_scaler.transform(X_new)

	# Classify new data
	y_new = loaded_model.predict(X_new)
	print(str(y_new[0]))
	Sound.speak(str(y_new[0]))


run(power, target, kp, kd, ki, direction, minRef, maxRef)