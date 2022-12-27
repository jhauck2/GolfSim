from src.subject import Subject
import cv2
from src.dynamics import rotX, rotZ, rk4, regression, get_x_0
import numpy as np
from src.clubs import Clubs
from src.golfBall import GolfBall
import time
from math import atan2, acos, cos, sin
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from mpl_toolkits import mplot3d


class State(Subject):
    def __init__(self, name, parent_state_machine=None):
        super().__init__()
        self.name = name
        self.state_machine = parent_state_machine
        self.is_active = False

    def update(self, delta):
        pass

    def enter(self, msg=None):
        self.notify("entered")
        self.is_active = True

    def exit(self, msg=None):
        self.notify("exited")
        self.is_active = False
        
        
class Standby(State):

    def enter(self, msg=None):
        super().enter()
        img = cv2.imread('Resources/OpenCVLogo.png')
        cv2.imshow('Title', img)
        print("Place ball on mat and pres 'a' to arm")
        print("Or press 's' to simulate shot")

    def update(self, delta=None):
        # Wait for player to place ball and arm cameras
        key = cv2.waitKey(1) & 0xFF
        if key == ord("a"):
            print("Arming...")
            self.state_machine.transition_to("Arm")
        if key == ord("s"):
            pos_list = [[np.array([[0], [0], [0]]), 1, 0.0],
                        [rotX(14.1*np.pi/180).dot(rotZ(3.0*np.pi/180)).dot(np.array([[0], [62.34/60], [0.0]])), 1, 1.0/60]]
            msg = {"pos_list": pos_list, "club": Clubs.Driver}
            self.state_machine.transition_to("Simulate", msg)


class Arm(State):
    def __init__(self, name):
        super().__init__(name)
        self.num_tries = 100
        self.tol = 0.03  # Tolerance in meters

    def enter(self, msg=None):
        super().enter(msg)
        self.num_tries = 100

    def update(self, delta=None):
        global cam1, cam2
        cam1.read()
        cam2.read()

        pos1 = cam1.get_ball()
        pos2 = cam2.get_ball()

        if self.num_tries <= 0:
            print("Ball could not be located within tolerance")
            self.state_machine.transition_to("Standby")
            return

        if pos1 is None or pos2 is None:
            self.num_tries -= 1
            return

        diff = np.abs(np.linalg.norm((pos2 - pos1)[0:3]))

        if diff <= self.tol:
            print("Ball has been located")

            global ball_pos
            ball_pos = (pos1 + pos2) / 2
            self.state_machine.transition_to("Ready")
        else:
            self.num_tries -= 1


class Ready(State):
    def __init__(self, name):
        super().__init__(name)
        self.dist_to_net = 2.4
        self.pos_list = []

    def update(self, delta=None):
        # Wait for ball to move
        global cam1, cam2
        # set previous images and clear current images
        cam1.prev_img = cam1.img
        cam2.prev_img = cam2.img
        cam1.img = None
        cam2.img = None

        cam1.read()
        pos1, time1 = cam1.get_ball()
        diff1 = np.abs(np.linalg.norm((pos1 - ball_pos)[0:3]))

        cam2.read()
        pos2, time2 = cam2.get_ball()
        diff2 = np.abs(np.linalg.norm((pos2 - ball_pos)[0:3]))

        if diff1 > self.dist_to_net or diff2 > self.dist_to_net:
            self.state_machine.transition_to("Simulate", {"pos_list": self.pos_list})
            return

        if diff1 > 0.1:
            self.pos_list.append([pos1, 1, time1])

        if diff2 > 0.1:
            self.pos_list.append([pos2, 1, time2])




class Simulate(State):
    def __init__(self, name):
        super().__init__(name)
        self.x = np.zeros((9, 1))  # state vector of [pos, vel, angular vel]
        self.v_angle = 0.0  # vertical launch angle in radians
        self.h_angle = 0.0  # horizontal launch angle in radians
        self.step = 1.0/60  # simulation resolution (60 fps)
        self.tot_time = 0.0  # total simulation time
        self.tot_steps = 0  # total simulation steps
        self.plt_x = np.array([])
        self.plt_y = np.array([])
        self.plt_z = np.array([])
        self.fig = plt.figure(figsize=(14, 9))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlim([-60, 60])
        self.ax.set_ylim([0, 300])
        self.ax.set_zlim([0, 60])
        self.ax.set_box_aspect(aspect=(2, 5, 1))
        self.ax.plot([0, 0], [0, 300], [0, 0], '-r')  # Center line
        self.line, = self.ax.plot(self.plt_x, self.plt_y, self.plt_z)
        self.cur_time = 0

    def enter(self, msg=None):
        self.x = np.zeros((9, 1))  # state vector of [pos, vel, angular vel]
        self.v_angle = 0.0  # vertical launch angle in radians
        self.h_angle = 0.0  # horizontal launch angle in radians
        self.step = 1.0 / 60  # simulation resolution (60 fps)
        self.tot_time = 0.0  # total simulation time
        self.cur_time = time.time()
        self.tot_steps = 0  # total simulation steps
        pos_list = msg["pos_list"]
        club = msg["club"]
        reg = regression(pos_list)
        v = np.transpose(np.array([reg[1]]))
        print(v)
        self.v_angle = atan2(v[2], v[1])
        self.h_angle = atan2(v[0], v[1])
        self.x = get_x_0(v, self.h_angle, club)
        self.plt_x = np.array([])
        self.plt_y = np.array([])
        self.plt_z = np.array([])
        plt.ion()
        plt.show()
        super().enter()

    def update(self, delta=None):
        # draw current ball position from self.x
        # time_dif = time.time() - self.cur_time
        # if time_dif < self.step:
        #     return
        #
        # self.cur_time += time_dif

        if self.tot_steps % 4 == 0:
            Artist.remove(self.ax.lines[1])
            self.ax.plot(self.plt_x, self.plt_y, self.plt_z, color='blue')
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        # update ball position
        speed = abs(np.linalg.norm(self.x[3:6]))
        rot_speed = abs(np.linalg.norm(self.x[6:9]))
        self.plt_x = np.append(self.plt_x, self.x[0])
        self.plt_y = np.append(self.plt_y, self.x[1])
        self.plt_z = np.append(self.plt_z, self.x[2])
        if self.tot_steps % 60 == 0:
            print("Time: " + str(self.tot_time) + "   Height: " + str(self.x[2]) + "   Distance: " + str(self.x[1]) +
                  "   Speed: " + str(speed) + "   Angular Speed: " + str(rot_speed))

        self.tot_time += self.step
        self.tot_steps += 1

        # check for "bounce"
        if self.x[2] < GolfBall.r:  # ball is underground
            self.x[2] = GolfBall.r
            if self.x[5] < -0.25 and self.tot_time > 1:  # ball is traveling downward fast enough to bounce
                print("bounce")
                print("Time: " + str(self.tot_time) + "   Height: " + str(self.x[2]) + "   Distance: " + str(
                    self.x[1]) + "   Speed: " + str(speed) + "   Angular Speed: " + str(rot_speed))
                # coefficient of restitution
                e = 0.2
                # if self.x[5] <= -20:
                #     e = 0.51 - 0.0375*np.abs(self.x[5]) + 0.000903*self.x[5]**2

                self.x[5] = self.x[5]*-e
                self.x[3:5] = self.x[3:5]*2*e

            else:
                self.x[5] = 0.0
        # run integrator
        ignore_friction = True
        if self.tot_time > 0.5:
            ignore_friction = False
        self.x = rk4(self.x, self.step, ignore_friction)
        if all(np.abs(self.x[3:5]) < 0.05) and self.x[2] < 0.05:
            print("Time: " + str(self.tot_time) + "   Height: " + str(self.x[2]) + "   Distance: " + str(self.x[1]) +
                  "   Speed: " + str(speed) + "   Angular Speed: " + str(rot_speed))

            self.state_machine.transition_to("Standby")