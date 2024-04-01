from random import randint
from LED import *

W, H = get_width_adjusted(), get_height_adjusted()

points = [[randint(0, W), randint(0, H), i * (255 / 20)] for i in range(20)]
colored_points = []
offset = 0

for x in range(W):
    for y in range(H):
        prev_distance = 10000
        my_hue, merge = 0, 1
        
        for px, py, hue in points:
            distance = ((px - x) ** 2 + (py - y) ** 2)
            
            if distance < prev_distance:
                prev_hue = my_hue
                merge = 0 if (prev_distance == 0) else (distance / prev_distance)
                my_hue = hue + (prev_hue - hue) * merge
                prev_distance = distance
        
        colored_points.append((x, y, my_hue, merge))

while True:
    for point in colored_points:
        offset += 0.0005
        draw_pixel(point[0], point[1], color_hsv(point[2] + offset, 255, point[3] * 255))
    draw()