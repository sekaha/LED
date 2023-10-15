from LED import *
from math import sin, cos, radians

set_orientation(1)

SCALE, WIDTH, HEIGHT, AMPLITUDE, PERIOD = 32, 24, 24, 3, 2
rot = [25, 25, 25]
CENTER_X, CENTER_Y = get_width_adjusted() // 2, get_height_adjusted() // 2
shift = 0

# 2d vector rotation
def rotate(x, y, angle):
    s = sin(radians(angle))
    c = cos(radians(angle))

    return x * c - y * s, y * c + x * s


while True:
    plot = []
    shift += 0.02

    rot[0] = get_mouse_x() * 4
    rot[1] = get_mouse_y() * 3

    for x in range(WIDTH):
        for y in range(HEIGHT):
            xx, yy = (2 * (x / WIDTH)) - 1, (2 * (y / HEIGHT)) - 1
            zz = (sin(x / PERIOD + shift) + cos(y / PERIOD + shift)) * AMPLITUDE
            # another function to try: zz = sin((xx*xx*9+yy*yy*9)+shift/12)*10
            plot.append((xx, yy, zz))
    refresh()

    for x, y, z in plot:
        col = color_hsv(127 + z * 5, 255, 255)
        x, y = rotate(x * SCALE, y * SCALE, rot[0])
        y, z = rotate(y, z, rot[1])
        draw_pixel(CENTER_X + x, CENTER_Y + y, col)
    draw()
