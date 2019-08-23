#!/usr/bin/env python3
"""
    Minimal usage example taken in https://github.com/qualisys/qualisys_python_sdk
    Connects to QTM and streams 3D data forever
    (start QTM first, load file, Play->Play with Real-Time output)
"""

import asyncio
from asyncio import async
import qtm #motion_capture
import xml.etree.ElementTree as ET
import rospy
from std_msgs.msg import Float32MultiArray

markersPub = rospy.Publisher('markers_pub', Float32MultiArray, queue_size=1)
rospy.init_node('motion_capture_realtime_acquire')


def on_packet(packet):
    """ Callback function that is called everytime a data packet arrives from QTM """
    print("Framenumber: {}".format(packet.framenumber))
    header, markers = packet.get_3d_markers()
    #we want the data in that order : wrist_Y, wrist_Z, hand_Z, elbow_Y
    my_array_of_data=[]
    my_array_of_data.append(markers[2].y) #wrist_Y
    my_array_of_data.append(markers[2].z) #wrist_Z
    my_array_of_data.append(markers[3].z) #hand_Z
    my_array_of_data.append(markers[1].y) #elbow_Y
    print("Component info: {}".format(header))
    publisher(my_array_of_data)
    for marker in markers:
        print("\t", marker)


def publisher(array_of_data):
    markersPub.publish(Float32MultiArray(data=array_of_data))
 
        
async def setup():
    """ Main function """
    connection = await qtm.connect("10.0.11.144") 
    if connection is None:
        return
        
    #To display the labels of all the markers you are using
    labels = []
    qxml = ET.fromstring(await connection.get_parameters(["3d"])) 
    for label in qxml[0].findall('Label'):
        labels.append(label[0].text)
    print(labels)
    
    await connection.stream_frames(components=["3d"], on_packet=on_packet)


if __name__ == "__main__":

    asyncio.ensure_future(setup()) 
    asyncio.get_event_loop().run_forever()
