#!/usr/bin/env python

import rospy
import numpy as np

from std_msgs.msg import Float64
from std_msgs.msg import String
from std_msgs.msg import Float64MultiArray
from control_msgs.msg import JointControllerState
#from gazebo_msgs.msg import GetJointProperties

import matplotlib.pyplot as plt
import time
import os

#####################

#joint 2
pub2= rospy.Publisher('/robot/right_joint_position_controller/joints/right_j5_controller/command', Float64, queue_size=100)

limit_pos_j5=2.9761 #xacro file
limit_vel_j5=3.485 #xacro file

position_des2=list()
position_act2=list()


#joint 1
pub1= rospy.Publisher('/robot/right_joint_position_controller/joints/right_j4_controller/command', Float64, queue_size=100)

limit_vel_j4=3.485 #xacro file
limit_pos_j4=2.9761 #xacro file

position_des1=list()
position_act1=list()

#####################

# Access data from Excel
import xlrd
os.chdir('/home/laura/Projects/LauraS/catkin_ws')
book=xlrd.open_workbook('Measurement4_final.xlsx')
sheets=book.sheet_names()
cur_sheet=book.sheet_by_name(sheets[0])

rospy.init_node('sawyer_motion_control', anonymous=True)
rate = rospy.Rate(50)

#wrist
list_of_wrist_position=list()
list_of_elbow_position=list()
av_first_last_val_w=list()
av_first_last_val_w.append(0.0)
av_first_last_val_w.append(0.0)
av_first_last_val_w.append(0.0)

#elbow
list_of_elbow_position=list()
av_first_last_val_e=list()
av_first_last_val_e.append(0.0)
av_first_last_val_e.append(0.0)
av_first_last_val_e.append(0.0)

def sawyer_motion_control_final():
	print 'start'

	rospy.Subscriber("/robot/right_joint_position_controller/joints/right_j4_controller/command", Float64, callback1)
	rospy.Subscriber("/robot/right_joint_position_controller/joints/right_j5_controller/command", Float64, callback2)

	#need by able to find to correct columns in the row 11
	total_col=cur_sheet.ncols
	total_row=cur_sheet.nrows
	for col in range (0,total_col-1):
		val=cur_sheet.cell_value(10,col)
		if val == 'r_wrist_m Z' :
			col_wrist_Z = col
		if val == 'r_elbow Y':
			col_elbow=col
		if val == 'r_hand Z':
			col_hand=col
		if val == 'r_wrist_m Y' :
			col_wrist_Y = col
		if val == 'Frame' :
			col_frame = col
	#print 'col_wrist_Z',col_wrist_Z
	#print 'col_elbow',col_elbow
	#print 'col_hand',col_hand
	#print 'col_wrist_Y',col_wrist_Y
	#print 'col_frame',col_frame
	row=12
	pos_cmd_lr=4.15722656e-03
	pos_cmd_ud=9.50683594e-03

	while not rospy.is_shutdown() and row < total_row:
		wrist_value_excel_Y = cur_sheet.cell(row,col_wrist_Y).value
		wrist_value_excel_Z = cur_sheet.cell(row,col_wrist_Z).value
		hand_value_excel = cur_sheet.cell(row,col_hand).value
		elbow_value_excel = cur_sheet.cell(row,col_elbow).value
		frame_value = cur_sheet.cell(row,col_frame).value
		print frame_value

		wrist_value = -(hand_value_excel-wrist_value_excel_Z)*limit_pos_j5/50 
		#print 'wrist_value_excel_Y',wrist_value_excel_Y
		#print 'elbow_value_excel',elbow_value_excel
		elbow_value = (wrist_value_excel_Y-elbow_value_excel)*limit_pos_j4/195
		#print 'elbow_value',elbow_value
				
		list_of_wrist_position.append(wrist_value)
		list_of_elbow_position.append(elbow_value)
	
		if len(list_of_wrist_position)==5:
			av_first_last_val_w.append(av_2values(list_of_wrist_position))
			#print 'av_first_last_val_w',av_first_last_val_w
			pos_cmd_ud=av_list(list_of_wrist_position)
			
			if abs(abs(av_first_last_val_w[-1])-abs(av_first_last_val_w[0]))>0.02:
			#need it to avoid shaking while doing nothing 
				#print 'pos_cmd_ud',pos_cmd_ud
				#if abs(pos_cmd_ud)> 0.77 : #0.77=10*limit_joint4/38.3 
				position_des2.append(pos_cmd_ud)
				pub2.publish(pos_cmd_ud)
			del list_of_wrist_position[0]
			del av_first_last_val_w[0]

		if len(list_of_elbow_position)==5:
			av_first_last_val_e.append(av_2values(list_of_elbow_position))
			pos_cmd_lr=av_list(list_of_elbow_position)

			if abs(abs(av_first_last_val_e[-1])-abs(av_first_last_val_e[0]))>0.02:
			#need it to avoid shaking while doing nothing 
				#print('pos_cmd_lr',pos_cmd_lr)
				position_des1.append(pos_cmd_lr)
				pub1.publish(pos_cmd_lr)
			del list_of_elbow_position[0]
			del av_first_last_val_e[0]


		row=row+1
		rate.sleep()
	rospy.spin()
	# spin() simply keeps python from exiting until this node is stopped

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
	#need : find a solution to put the robot in an initial position 
	pub2.publish(0.0) #doesn't work 
	pub1.publish(0.0)	
	#rospy.Rate(10).sleep()
	sawyer_motion_control_final()
	print 'time elapsed', time.time()-start
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

