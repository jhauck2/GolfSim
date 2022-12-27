import numpy as np
import cv2
import time
from src.golfBall import GolfBall
from src.clubs import Clubs
from src.camera import Camera
from src.dynamics import regression, get_x_0, rk4, rotZ, unit, rotX
from src.stateMachine import StateMachine
from src.nestedState import NestedState
from src.state import State, Standby, Arm, Ready, Simulate
from src.Database import Database

# **********************************************************************************************************************
# ************************************************* Initialize Cameras *************************************************
# **********************************************************************************************************************

# Cameras
cam1 = Camera()
cam2 = Camera()

# Allow cameras to warm up
time.sleep(2.0)

cam1.initialize()
cam2.initialize()


# **********************************************************************************************************************
# ************************************************ Create State Machine ************************************************
# **********************************************************************************************************************

# # Initialize states
class Calibrate(State):
    pass


calibrate = Calibrate("Calibrate")

standby = Standby("Standby")
ball_pos = None

arm = Arm("Arm")

ready = Ready("Ready")

simulate = Simulate("Simulate")

state_machine = StateMachine("Standby", [calibrate, standby, arm, ready, simulate])

# **********************************************************************************************************************
# ************************************************* Run State Machine **************************************************
# **********************************************************************************************************************
while True:
    state_machine.update()
