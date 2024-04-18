import numpy as np
from math import radians
from LED import *


set_orientation(1)
set_window_scale(16)

W, H = get_width_adjusted(), get_height_adjusted()

# generating the range of x values and y values
xvals, yvals = np.arange(W), np.arange(H)
# palette = [(5, 5, 24), (107, 31, 255), (204, 40, 195), (255, 255, 200)]

scale, zoom = 1, 1.2
dest_x, dest_y = 529119.95, 370.30776251
shift_factor = 2**21

# a very large number, right before floating point representation breaks
max_zoom = 2**54
t = 0
while True:
    # zoom in and out
    if (scale > max_zoom) or (scale < 1):
        zoom = 1 / zoom
    scale *= zoom
    t += 1
    palette = [
        oklch_to_oklab(0.3 + i * 0.25, 0.1 + i * 0.15, radians(t + 360 - i * 75))
        for i in range(4)
    ]

    # Zoom to a specific location
    x_shift, y_shift = dest_x * (scale / shift_factor), dest_y * (scale / shift_factor)

    # create the complex plane we work from, adjusted for shift and scale
    x, y = np.meshgrid(
        (xvals + x_shift - W / 2) / scale, (yvals + y_shift - H / 2) / scale
    )

    # mandelbrot set formula
    z = c = x + y * 1j

    iters = np.zeros(z.shape)
    mask = np.ones(z.shape)
    detail = 48 + int(min(1, scale / 1000000) * 2000)

    # count number of iterations for coloring
    for _ in range(detail):
        # the mask controls the darkness of the edge, having it low results in sharper edges, but loss of detail
        mask *= np.abs(z) <= 255
        iters += mask
        z = (z**2 + c) * mask

    # draw each pixel
    for y, row in enumerate(iters):
        for x, pixel in enumerate(row):
            c = color_oklab(*merge_palette(palette, pixel / detail))
            draw_pixel(x, y, c)

    draw()
