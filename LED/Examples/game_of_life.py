from LED import *
import numpy as np

W = get_width_adjusted()
H = get_height_adjusted()

world = np.random.randint(0, 2, size=(W, H), dtype=np.byte)
neighbors = np.zeros((W, H), dtype=np.byte)

while True:
    neighbors = (
        np.roll(world, 1, axis=1)
        + np.roll(world, -1, axis=1)
        + np.roll(world, 1, axis=0)
        + np.roll(world, -1, axis=0)
        + np.roll(world, (-1, -1), axis=(0, 1))
        + np.roll(world, (-1, 1), axis=(0, 1))
        + np.roll(world, (1, -1), axis=(0, 1))
        + np.roll(world, (1, 1), axis=(0, 1))
    )

    world &= neighbors == 2
    world |= neighbors == 3

    refresh()
    for y, row in enumerate(world):
        for x, life in enumerate(row):
            if life == 1:
                draw_pixel(y, x, WHITE)

    draw()
