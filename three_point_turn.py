# Three point turn pseudo code
#!/usr/bin/python
# -*- coding: utf-8 -*-

from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
import time
import os
import logging
import sys
import drivetrain
from numpy import clip, interp

# set up ADC
i2c_helper = ABEHelpers()
bus = i2c_helper.get_smbus()
adc = ADCPi(bus, 0x68, 0x69, 12)


#define fixed values
red_min=3  #red is typically 3.5V
red=3.5
full_forward=0.5
slow_forward=0.1
full_reverse=-0.5
slow_reverse=-0.1

straight=0
full_left=-1
rear_line_sensor=2
front_line_sensor=2  #same sensor for now
max_rate=2

drive = drivetrain.DriveTrain(pwm_i2c=0x4 if i2c is None else i2c)


# needs a def run
def run():
#	initiate camera


	movesegment(T_first_segment_timeout, T_accelerating_first_segment, rear_line_sensor, full_forward, straight, slow_forward, straight)  #forward to turning point

	movesegment(T_left_turn_time, T_accelerating_second_segment, 0, Stopped, full_left, straight, slow_forward)  #first Left turn

	movesegment(T_third_segment_timeout, T_accelerating_third_segment, front_line_sensor, full_forward, straight, slow_forward,straight)  #forward to first side line

	movesegment(T_forth_segment_timeout, T_accelerating_forth_segment, rear_line_sensor, full_reverse, straight, slow_reverse, straight)  #reverse portion to second side line

	movesegment(T_fifth_segment_timeout, T_accelerating_fifth_segment, 0, full_forward, straight, slow_forward, straight)  #reverse portion to second side line

	movesegment(T_left_turn_time, T_accelerating_second_segment, 0, Stopped, full_left, straight, slow_forward)  #second Left turn
	movesegment(T_last_segment_timeout, T_accelerating_last_segment, front_line_sensor, full_forward, straight, slow_forward, straight)  #return to start
#	movesegment(T_last_segment_timeout, T_accelerating_last_segment, Camera, full_forward, straight, slow_forward, straight)  #return to start using camera

	movesegment(T_finish_timeout, T_accelerating_box_segment, rear_line_sensor, slow_forward, straight, Stopped, straight)  #Enter start box

	drive.set_neutral()

#End



def move_segment(total_timeout, accelerating_time, line_sensor, peak_throttle, peak_steering, end_throttle, end_steering):


#Note Line_sensor=0 if no line sensor exit required

# calculate timeout times
	end_timeout=time.time()+total_timeout
	acceleration_timeout=time.time()+accelerating_time

	while time.time()<end_timeout and line_sensor_value>red_min:


		if time.time()<acceleration_timeout:
#			throttle=peak_throttle   #easing will be needed to limit the maximum rate of change
			throttle=ease_throttle(throttle, peak_throttle, max_rate)
			steering=peak_steering
		else:	
			throttle = end_throttle   #easing needs adding 
			steering = end_steering
#		end If
		if line_Sensor!=0:   #if line sensor needs checking
			line_sensor_value=adc.read_voltage(line_sensor)

#		elif LineSensor = Camera then
#			Get BeaconAngle
#			steering proportional to BeaconAngle
#			line_sensor_value=adc.read_voltage(front_line_sensor)
		else:
			LineSensorValue=Red
#		end if
		drive.mix_channels_and_assign(throttle, steering)
#	Wend

	if throttle != end_throttle or steering != end_steering: #must have got better than usual acceleration. need to slow down before finishing
		throttle = end_throttle  #needs easing adding
		steering = end_steering #needs easing adding
		drive.mix_channels_and_assign(throttle, steering)
#	end If
#end sub

def ease_throttle(current_throttle, target, rate):
# if variable is above target
	if current_throttle>target:
		new_throttle=max(target,current_throttle-rate*(time.time()-last_throttle_update ))
# or variable is below target
	if current_throttle>=target:
		new_throttle=max(target,current_throttle+rate*(time.time()-last_throttle_update ))
	last_throttle_update=time.time() 
	return new_throttle

def ease_steering(current_steering, target, rate):
# if variable is above target
	if current_steering>target:
		new_steering=max(target,current_steering-rate*(time.time()-last_steering_update ))
# or variable is below target
	if current_steering>=target:
		new_steering=max(target,current_steering+rate*(time.time()-last_steering_update ))
	last_steering_update=time.time() 
	return new_steering
