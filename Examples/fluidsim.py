from LED import *
import numpy as np
from scipy import signal

W, H = get_width_adjusted(), get_height_adjusted()

density = np.random.uniform(0,1,(W,H))

def diffuse(k):
    global density
    current_density = density
    dis = 0.95

    for i in range(5):
        kernel = [[0,dis,0],[dis,0,dis],[0,dis,0]]
        density_av = signal.convolve(density, kernel, mode='same')/4
        density = (current_density+density_av*k)/(1+k)

while True:
    draw_canvas(0,0,colorize(density, BLUE))
 
    if get_mouse_left():
        density[int(get_mouse_x())][int(get_mouse_y())] = 2

    diffuse(1)
    draw()