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
	left_sensor=0
	right_sensor=0
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

		#save data for predict 
		left_sensor += 0
		mid_sensor += col.value()
		right_sensor += 0
		left_motor_count += left_motor.speed
		right_motor_count += right_motor.speed
		
	left_motor.stop()
	right_motor.stop()

# Unification des donnée 
	left_sensor = left_sensor / 1883
	mid_sensor = mid_sensor / 1883
	right_sensor = right_sensor / 1883
	left_motor_count = left_motor_count / 1883
	right_motor_count = right_motor_count / 1883

	X_new = [[left_sensor, right_sensor, mid_sensor, left_motor_count, right_motor_count]]

	# Load model and scaler
	loaded_model = pickle.load(open('./formes_model/trained_model.sav', 'rb'))
	loaded_scaler = pickle.load(open('./formes_model/mlp_scaler.pkl', 'rb'))
	
	print(loaded_scaler)
	# Apply scaler
	X_new = loaded_scaler.transform(X_new)

	# Classify new data
	y_new = loaded_model.predict(X_new)
	screen = Screen()
	sound = Sound()

	if y_new[0] == 0:
		screen.clear()

		# Screen.draw returns a PIL.ImageDraw handle
		screen.draw.line((30, 50, 80, 100))
		screen.draw.line((80, 100, 148, 50))
		screen.draw.arc((30, 30, 90, 70), 180, 0)
		screen.draw.arc((90, 30, 148, 70), 180, 0)
		screen.update()
		Sound.speak("Heart")
	elif y_new[0] == 1:
		screen.clear()
		lines = [(80,20),(20,100),(158,100)]
		screen.draw.polygon(lines)
		screen.update()
		Sound.speak("Triangle")


run(power, target, kp, kd, ki, direction, minRef, maxRef)
