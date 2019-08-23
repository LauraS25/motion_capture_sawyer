# motion_capture_sawyer
These codes allow to receive the positions coming from the Qualysis motion capture program and to publish these values in order to send them to the Sawyer robot imitating certain movements of our arm. 

The work of https://github.com/qualisys/qualisys_python_sdk helped me a lot to have a code able to receive the positions from the motion capture system in realtime.


## Requirements
-python3 
-qtm librairy
-asyncio library 

To install qtm :
sudo apt-get install python3-pip 
python3 -m pip install qtm

## Model I used on QTM
4 markers :
- shoulder
- elbow
- on the top of the wrist
- at the end of the middle finger 
