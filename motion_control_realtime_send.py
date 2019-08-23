#!/usr/bin/env python3

import rospy
import numpy as np

from std_msgs.msg import Float64
from std_msgs.msg import Float32MultiArray
from control_msgs.msg import JointControllerState

import matplotlib.pyplot as plt
import time
import os

rospy.init_node('listener', anonymous=True)

#####################
''' Here we are modifying the angles of two joints : joint 5 and joint 4. Please make sure that a modification of thoses angles can't hurt the robot.
Please change the values of limit_pos_j5 and limit_pos_j4 if you are using different joints (values can be found in the robot description)
'''

#joint 2
pub2= rospy.Publisher('/robot/right_joint_position_controller/joints/right_j5_controller/command', Float64, queue_size=100)

limit_pos_j5=2.9761 #xacro file

position_des2=list()
position_act2=list()


#joint 1
pub1= rospy.Publisher('/robot/right_joint_position_controller/joints/right_j4_controller/command', Float64, queue_size=100)

limit_pos_j4=2.9761 #xacro file

position_des1=list()
position_act1=list()

#####################


#wrist
list_of_wrist_position=list()
list_of_elbow_position=list()
av_first_last_val_w=list()
av_first_last_val_w.append(0.0)
av_first_last_val_w.append(0.0)
av_first_last_val_w.append(0.0)

wrist_list_Y=list()
wrist_list_Y.append(0.0)
wrist_list_Z=list()
wrist_list_Z.append(0.0)
hand_list_Z=list()
hand_list_Z.append(0.0)
elbow_list_Y=list()
elbow_list_Y.append(0.0)

#elbow
list_of_elbow_position=list()
av_first_last_val_e=list()
av_first_last_val_e.append(0.0)
av_first_last_val_e.append(0.0)
av_first_last_val_e.append(0.0)


def sawyer_motion_control_final():
	print('start')
	rospy.Subscriber("markers_pub", Float32MultiArray, callback)
	rospy.Subscriber("/robot/right_joint_position_controller/joints/right_j4_controller/command", Float64, callback1)
	rospy.Subscriber("/robot/right_joint_position_controller/joints/right_j5_controller/command", Float64, callback2)
	rospy.spin()
	# spin() simply keeps python from exiting until this node is stopped

def callback(data):
	''' data represents an array of float giving the coordinates of each markers in that order: shoulder, elbow, wrist and hand. We only need elbow (Y), wrist (Y and Z) and hand (Z) '''	
	rospy.loginfo(rospy.get_caller_id() + " I heard for %s", data.data)
	wrist_list_Y.append(data.data[0])
	wrist_list_Z.append(data.data[1])
	hand_list_Z.append(data.data[2])
	elbow_list_Y.append(data.data[3])

	pos_cmd_lr=4.15722656e-03
	pos_cmd_ud=9.50683594e-03

	wrist_value = -(hand_list_Z[-1]-wrist_list_Z[-1])*limit_pos_j5/60 #60 seem to be the maximum value i can have 
	elbow_value = (wrist_list_Y[-1]-elbow_list_Y[-1])*limit_pos_j4/200 #200 seem to be the maximum value i can have 
				
	list_of_wrist_position.append(wrist_value)
	list_of_elbow_position.append(elbow_value)
	
	if len(list_of_wrist_position)==5:
		av_first_last_val_w.append(av_2values(list_of_wrist_position))
		#print 'av_first_last_val_w',av_first_last_val_w
		pos_cmd_ud=av_list(list_of_wrist_position)
			
		if abs(abs(av_first_last_val_w[-1])-abs(av_first_last_val_w[0]))>0.02:
		#need it to avoid shaking while doing nothing 
			position_des2.append(pos_cmd_ud)
			pub2.publish(pos_cmd_ud)
		del list_of_wrist_position[0]
		del av_first_last_val_w[0]

	if len(list_of_elbow_position)==5:
		av_first_last_val_e.append(av_2values(list_of_elbow_position))
		pos_cmd_lr=av_list(list_of_elbow_position)

		if abs(abs(av_first_last_val_e[-1])-abs(av_first_last_val_e[0]))>0.02:
		#need it to avoid shaking while doing nothing 
			position_des1.append(pos_cmd_lr)
			pub1.publish(pos_cmd_lr)
		del list_of_elbow_position[0]
		del av_first_last_val_e[0]

# callback 1 and 2 give access to the actual position of the robot (of the two joints considered)
def callback1(data):
	position_act1.append(data.data)

def callback2(data):
	position_act2.append(data.data)

def av_list(list_of_val):
	n=len(list_of_val)
	somme=0	
	for i in range (0,n-1):
		somme=somme+list_of_val[i]
	return somme/n
		
def av_2values(list_of_val):
	return (list_of_val[0]+list_of_val[-1])/2
	

if __name__ == '__main__':
	start=time.time()
	sawyer_motion_control_final()
	print('time elapsed', time.time()-start)
	plt.figure()
	#plt.subplot(2, 1, 1)
	plt.title('joint position up/down - joint 5') #up/down
	plt.plot(position_des2, 'b', label='desired position up/down')
	plt.plot(position_act2, 'r', label='actual position up/down')
	#plt.subplot(2, 1, 2)
	plt.figure()
	plt.title('joint position right/left - joint 4')
	plt.plot(position_des1, 'b', label='desired position right/left')
	plt.plot(position_act1, 'r', label='actual position right/left')
	plt.show()

