import numpy as np
from src.golfBall import GolfBall
import warnings
warnings.filterwarnings("error")


# noinspection PyMethodMayBeStatic
# Air Density (kg/m^3)
rho = 1.225

# Air Viscosity (kg/(m*s))
nu = 1.81e-5
nu_k = 1.48e-5  # kinematic viscosity

# Grass Viscosity (estimation somewhere between air and water)
nu_g = 1.2e-4


def get_x_dot(x, no_frict):
    # no_frict indicates to ignore friction with the ground
    # Forces
    g = np.array([[0], [0], [-9.81]])  # gravity
    F = np.zeros((3, 1))  # total forces
    F_g = GolfBall.m * g  # force due to gravity
    F_m = np.zeros((3, 1))
    F_d = np.zeros((3, 1))
    speed = np.linalg.norm(x[3:6])
    spin = np.linalg.norm(x[6:9])*GolfBall.r/speed
    Re = speed*GolfBall.r*2/nu_k
    # Magnus and drag coefficients derived from References/proceedings-02-00238-v2.pdf
    S = 0.5*rho*np.pi*(GolfBall.r**3)*(-3.25*spin + 1.99)
    if Re < 87500:
        Cd = 1.29e-10*(Re**2) - 2.59e-5*Re + 1.50
    else:
        Cd = 1.91e-11*(Re**2) - 5.4e-6*Re + 0.56

    F_f = np.zeros((3, 1))  # force of friction
    T_f = np.zeros((3, 1))  # frictional torque
    T_d = np.zeros((3, 1))  # drag torque
    F_gd = np.zeros((3, 1))  # grass drag
    T_g = np.zeros((3, 1))  # grass frictional torque

    if x[2] < 0.05 and not no_frict:  # add friction when ball center is less than 5 cm off the ground
        # direction of frictional torque
        t_dir = unit(rotZ(-np.pi/2).dot(rotZ(np.pi/2).dot(x[6:9])*GolfBall.r + x[3:6])[0:2])
        # direction of velocity of bottom of ball
        v_dir = unit((rotZ(np.pi/2).dot(x[6:9])*GolfBall.r + x[3:6])[0:2])
        # Force of slipping friction with the ground
        F_f[0:2] = v_dir * GolfBall.u_k * GolfBall.m
        # frictional torque from slipping while rolling
        T_f[0:2] = t_dir*GolfBall.u_k*GolfBall.m*GolfBall.r  # T = F*r
        # Force of viscous drag with the grass blades
        F_gd[0:2] = x[3:5]*6*np.pi*GolfBall.r*nu_g
        # Viscous torque from grass
        T_d = GolfBall.S * 480 * nu_g * x[6:9]
    else:  # still in the air calculate air forces and torques
        # F_m = GolfBall.S * rho * np.cross(np.transpose(x[6:9]), np.transpose(x[3:6]))  # magnus force
        F_m = S*np.cross(np.transpose(x[6:9]), np.transpose(x[3:6]))
        F_m = np.reshape(F_m, (3, 1))
        # viscous torque - factor of 480 used to get correct decay rate
        T_d = S * 480 * nu * x[6:9]
        # Drag
        F_d = Cd * rho * x[3:6] * x[3:6] * GolfBall.A / 2  # drag force

    F = F_g - F_d + F_m - F_f - F_gd

    T = -T_f - T_d

    x_dot = np.zeros((9, 1))
    x_dot[0:3] = x[3:6]
    x_dot[3:6] = F / GolfBall.m
    x_dot[6:9] = T / GolfBall.I

    return x_dot


def get_x_0(vel, h_angle, club):
    x0 = np.zeros((9, 1), dtype='double')  # [pos, vel, ang vel]
    x0[2] = 0.1

    x0[3:6] = vel
    x0[6:9] = rotZ(-h_angle).dot(rotY(-h_angle)).dot(np.array([[club["spin"]], [0], [0]]))
    print(x0[6:9])

    return x0


def rotX(val):
    return np.array([[1, 0, 0], [0, np.cos(val), np.sin(val)], [0, np.sin(val), np.cos(val)]])


def rotY(val):
    return np.array([[np.cos(val), 0, np.sin(val)], [0, 1, 0], [-np.sin(val), 0, np.cos(val)]])


def rotZ(val):
    return np.array([[np.cos(val), -np.sin(val), 0], [np.sin(val), np.cos(val), 0], [0, 0, 1]])


def rk4(x0, step, no_frict):
    # no_frict indicates to ignore friction with the ground
    K1 = step * get_x_dot(x0, no_frict)
    K2 = step * get_x_dot(x0 + 0.5 * K1, no_frict)
    K3 = step * get_x_dot(x0 + 0.5 * K2, no_frict)
    K4 = step * get_x_dot(x0 + K3, no_frict)

    return x0 + K1 / 6 + K2 / 3 + K3 / 3 + K4 / 6


def regression(pos_list):
    # using v = (t*t')^-1 * t' * x
    # where:
    # - v is the velocity vector
    # - t is the vector of time values with '1' in the first column
    # - x is the vector of position values
    x = np.transpose(pos_list[0][0])
    t = np.array([pos_list[0][1:3]])
    pos_list = pos_list[1:]

    for row in pos_list:
        x = np.append(x, row[0][0:3].transpose(), axis=0)
        t = np.append(t, np.array([row[1:3]]), axis=0)

    v = np.linalg.pinv(np.transpose(t).dot(t)).dot(np.transpose(t)).dot(x)

    return v


def unit(x):
    return x / np.linalg.norm(x)


# x1 = np.array([[1], [2], [3]])
# x2 = np.array([[2.1], [4], [6]])
# x3 = np.array([[2.9], [6], [9]])
#
#
# x_list = [[x1, 1, 1], [x2, 1, 2], [x3, 1, 3]]
#
#
# print(regression(x_list))

