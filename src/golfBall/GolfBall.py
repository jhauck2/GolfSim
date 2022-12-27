from numpy import pi

# drag coefficient https://www.scirp.org/journal/paperinformation.aspx?paperid=85529
Cd = 0.2
# Ball mass (kg)
m = 0.04592623
# Ball radius (m)
r = 21.335e-3
# cross-sectional area (m^2)
A = pi*r**2
# Ball moment of inertia
I = 0.4 * m * r ** 2
# Magnus coefficient (kg)
S = 8 / 3 * pi * r ** 3
# Friction Coefficient with ground
u_k = 0.4
# Using convention: direction right handed golfer is facing = +x, ball flight direction = +y, up = +z
# Define the lower and upper boundaries of the ball color in HSV space
ball_lower = (0, 90, 187)
ball_upper = (21, 255, 255)
