from LED import *
from random import randint

set_orientation(1)
W , H = get_width_adjusted(), get_height_adjusted()

# construct a sorted array
test_array = [val*(H/W) for val in range(W)]

# scrambling the array
def scramble_array(data):
    new_array = []
    for time in range(len(data)):
        val = data[randint(0,len(data)-1)]
        new_array.append(val)
        data.remove(val)
    return new_array


# n^2 run time
# compare every item to the one on its left, and swap theme in the correct order
# hmm proof?
def bubble_sort(data):
    for i in range(len(data)):
        for j in range(len(data)-1):
            # sort it
            if(data[j] > data[j+1]):
                tmp = data[j]
                data[j] = data[j+1]
                data[j+1] = tmp

            # draw it, untab this to see a different view of how this works
            refresh()
            for x, val in enumerate(data):
                col = FUCHSIA if x == i else CYAN
                col = YELLOW if x == j else col
                draw_line(x,H,x,H-val,col)
            draw()

# work left to right
# examine each item and compare it to the items on its left
# *insert* the item  in the correct spot
def insertion_sort(data):
    for i in range(1,len(data)):
        tmp = data[i]
        j = i - 1

        while (j >= 0 and tmp < data[j]):
            # shift it forward until we find the right spot
            data[j+1] = data[j]
            j-=1

            refresh()
            for x, val in enumerate(data):
                col = FUCHSIA if x == i else CYAN
                col = YELLOW if x == j else col
                draw_line(x,H,x,H-val,col)
            draw()

        data[j+1] = tmp

# selection sort
# find the smallest element in the list, move it to the front
# advance forward, finding the smallest element in the sublist
# O(n^2)
def selection_sort(data):
    for i in range(len(data)):
        smallest = i
        for j in range(i+1,len(data)):
            if data[smallest] >= data[j]:
                smallest = j
            # tab it in to see it slower
            refresh()
            for x, val in enumerate(data):
                col = FUCHSIA if x == i else CYAN
                col = YELLOW if x == j else col
                draw_line(x,H,x,H-val,col)
            draw()

        tmp = data[i]
        data[i] = data[smallest]
        data[smallest] = tmp

# merge sort
# O(n*logn)

# Split
# recursively split in half if array has greater than one item
# the binary tree made by splitting is log(n) high, hence the log(n) portion of this problem's complexity
# [1,4,3,5]       |
# [1,4] [3,5]     | log(n) height
# [1] [4] [3] [5] |
# NOTE: x_off is only for display purposes, not integral to the algorithm
def merge_sort(data,x_off=0,level=0):
    if len(data) == 1:
        return data
    
    mid = len(data)//2

    # refresh the part we are overwriting
    draw_rectangle(x_off,0,len(data)-1,H,BLACK)

    # draw sorted list
    for x, val in enumerate(data):
        draw_line(x_off+x,H,x_off+x,H-val,color_hsv(127+level*32,255,255))
    draw()
    
    # go into a recursion tree
    left = merge_sort(data[:mid],x_off,level+1)
    right = merge_sort(data[mid:],x_off+mid-1,level+1)

    sorted = merge(left,right,x_off,level)

    return sorted

# Merge
def merge(left,right,x_off,level):
    sorted = []
    i, j = 0, 0

    while (i < len(left) and j < len(right)):
        if left[i] < right[j]:
            sorted.append(left[i])
            i+=1
        else:
            sorted.append(right[j])
            j+=1

        # refresh the part we are overwriting
        draw_rectangle(x_off,0,len(left+right),H,BLACK)

        # draw sorted list
        for x, val in enumerate(sorted):
            draw_line(x_off+x,H,x_off+x,H-val,color_hsv(127+level*32,255,255))
        draw()
    # making sure if one list is bigger than the other, to ad the result of the input
    sorted.extend(left[i:])
    sorted.extend(right[j:])

    # refresh the part we are overwriting
    draw_rectangle(x_off,0,len(left+right),H,BLACK)

    # draw sorted list
    for x, val in enumerate(sorted):
        draw_line(x_off+x,H,x_off+x,H-val,color_hsv(127+level*32,255,255))
    draw()

    return sorted

sort_num = 0

while True:
    if sort_num == 0:
        func = merge_sort
        sort = "Merge Sort"
    elif sort_num == 1:
        func = bubble_sort
        sort = "Bubble Sort"
    elif sort_num == 2:
        func = insertion_sort
        sort = "Insertion Sort"
    else:
        func = selection_sort
        sort = "Selection Sort"

    set_font(FNT_SMALL)
    draw_text(2,-3,sort,WHITE)

    if get_key_pressed("space"):
        test_array = scramble_array(test_array)
        func(test_array)
    
    if get_key_pressed("right"):
        sort_num = (sort_num+1) % 4
        refresh()

    if get_key_pressed("left"):
        sort_num = (sort_num-1) % 4
        refresh()
    draw()