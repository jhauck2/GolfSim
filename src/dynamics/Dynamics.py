import numpy as np
from src.golfBall import GolfBall


# noinspection PyMethodMayBeStatic
# Air Density (kg/m^3)
rho = 1.225


def get_x_dot(self, x):
    # Forces
    g = np.array([[0], [0], [-9.81]])  # gravity
    F = np.zeros((3, 1))  # total forces
    F_g = GolfBall.m * g  # force due to gravity
    F_d = GolfBall.Cd * self.rho * x[3:6] * x[3:6] * GolfBall.A / 2  # drag force
    F_m = GolfBall.S * x[3:6].cross(x[6:9])
    F = F_g - F_d + F_m

    # Drag Torque - include S for dimensional consistency
    T_d = GolfBall.Cd * GolfBall.S * x[6:9] * x[6:9] * GolfBall.A / 2

    x_dot = np.zeros((9, 1))
    x_dot[0:3] = x[3:6]
    x_dot[3:6] = F / GolfBall.m
    x_dot[6:9] = -T_d / GolfBall.I

    return x_dot


def get_x_0(self, speed, v_angle, h_angle, f_angle, s_angle, club):
    x0 = np.zeros((9, 1))  # [pos, vel, ang vel]

    x0[3:6] = self.rotX(v_angle).dot(self.rotZ(h_angle)).dot(np.array([[0], [speed], [0]]))
    x0[6:9] = self.rotZ(h_angle).dot(self.rotY(f_angle - s_angle)).dot(np.array([[club["spin"]], [0], [0]]))

    return x0


def rotX(self, val):
    return np.array([[1, 0, 0], [0, np.cos(val), np.sin(val)], [0, np.sin(val), np.cos(val)]])


def rotY(self, val):
    return np.array([[np.cos(val), 0, np.sin(val)], [0, 1, 0], [-np.sin(val), 0, np.cos(val)]])


def rotZ(self, val):
    return np.array([[np.cos(val), -np.sin(val), 0], [np.sin(val), np.cos(val), 0], [0, 0, 1]])


def rk4(self, x0, step):
    K1 = step * self.get_x_dot(x0)
    K2 = step * self.get_x_dot(x0 + 0.5 * K1)
    K3 = step * self.get_x_dot(x0 + 0.5 * K2)
    K4 = step * self.get_x_dot(x0 + K3)

    return x0 + K1 / 6 + K2 / 3 + K3 / 3 + K4 / 6
