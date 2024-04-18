from LED import *
import math, random, pygame
set_orientation(1) # horizontal
hue = 0
menu = "start"
menu_option = 0
options = ["play","options","scores","quit"]
networked = False
disable_networking()
set_fps(120)

# SPRITES
minos = create_sprite_sheet("tet.png",4,4,1,8)
MINO_SIZE = 4
grid_orientation = 1
mino_test = 0
menu_t_y_pos = -5
menu_t_x_pos = random.randint(0,get_width_adjusted()-MINO_SIZE)
menu_tetra_width = 0
tetra_x = 4
tetra_y = 0
tetra_rot = 0
cur_tetra = 0
menu_tetramino_rot = random.randint(0,3)
menu_cube = create_hypercube(4)
menu_tetra_move = 0
game_time = 0
drop_time = 100
drop_boost = 0

# Scores
score = 0
scores = []
highscore = False
username = ""

with open("highscores.txt") as highscores:
    for line in highscores.readlines():
        scores.append(line.split())

# these are super non-typical, but I like it cuz powers of 2
clear_scores = {0:0, 1:16, 2:32, 3:64, 4:256}

# MINOS
# the pieces are 3D arrays of [rotation][point]
I_PIECE = [[(0,0) for x in range(4)] for y in range(2)]
J_PIECE = [[(0,0) for x in range(4)] for y in range(4)]
L_PIECE = [[(0,0) for x in range(4)] for y in range(4)]
O_PIECE = [[(0,0) for x in range(4)] for y in range(1)]
S_PIECE = [[(0,0) for x in range(4)] for y in range(2)]
T_PIECE = [[(0,0) for x in range(4)] for y in range(4)]
Z_PIECE = [[(0,0) for x in range(4)] for y in range(2)]
TETRAMINO = [I_PIECE,J_PIECE,L_PIECE,O_PIECE,S_PIECE,T_PIECE,Z_PIECE]
menu_tetramino = random.randint(0,len(TETRAMINO)-1)
current_tetramino = TETRAMINO[menu_tetramino][menu_tetramino_rot % len(TETRAMINO[menu_tetramino])]

# I=piece
I_PIECE[0] = [(2,0),(2,1),(2,2),(2,3)]
I_PIECE[1] = [(0,1),(1,1),(2,1),(3,1)]

# J-piece
J_PIECE[0] = [(0,1),(1,1),(2,1),(2,2)]
J_PIECE[1] = [(0,2),(1,0),(1,1),(1,2)]
J_PIECE[2] = [(0,0),(0,1),(1,1),(2,1)]
J_PIECE[3] = [(1,0),(2,0),(1,1),(1,2)]

# L-piece
L_PIECE[0] = [(0,1),(1,1),(2,1),(0,2)]
L_PIECE[1] = [(0,0),(1,0),(1,1),(1,2)]
L_PIECE[2] = [(0,1),(1,1),(2,1),(2,0)]
L_PIECE[3] = [(1,0),(1,1),(1,2),(2,2)]

#O_PIECE
O_PIECE[0] = [(1,1),(1,2),(2,1),(2,2)]

#S_PIECE
S_PIECE[0] = [(0,2),(1,1),(1,2),(2,1)]
S_PIECE[1] = [(1,0),(1,1),(2,1),(2,2)]

#Z_PIECE
Z_PIECE[0] = [(0,1),(1,1),(1,2),(2,2)]
Z_PIECE[1] = [(1,1),(1,2),(2,0),(2,1)]

#T_PIECE
T_PIECE[0] = [(0,1),(1,1),(2,1),(1,2)]
T_PIECE[1] = [(1,0),(1,1),(1,2),(0,1)]
T_PIECE[2] = [(0,1),(1,1),(2,1),(1,0)]
T_PIECE[3] = [(1,0),(1,1),(1,2),(2,1)]

well_width = 12
well_height = 20
well  =  None

key_timer = [0 for x in range(0,3)]
REPEAT_DELAY = 35
HOLD_TIME = 8
pause = False
game_over = False

### COLORS
AQUA = (11,255,230)
BACKGROUND_COL = (11,25,32)

def make_well():
    global well_width
    global well_height
    global well
    global MINO_SIZE
    well_height = 1+get_height_adjusted()//MINO_SIZE # does 15 or 20 + one block for floor
    well  =  [[-1 for y in range(well_height)] for x in range(well_width)]
    
    # set walls of well
    for column in well[0:well_width:well_width-1]:
        for y_pos in range(well_height-1):
            column[y_pos] = 7
    # set floor of well
    bottom_row = well_height-1
    for x_pos, column in enumerate(well):
        well[x_pos][bottom_row] = 7

def update_game():
    # controls
    global menu_option
    global menu
    global tetra_x
    global tetra_y
    global tetra_rot
    global cur_tetra
    global networked
    global pause
    global score
    global game_over
    global scores
    global highscore
    global drop_boost
    global drop_time

    # Framerate capping
    if menu=="start":
        if get_key_pressed("up"):
            menu_option-=1
        elif get_key_pressed("down"):
            menu_option+=1
        elif get_key_pressed("right") or get_key_pressed("enter"):
            if menu_option == 0:
                make_well()
                menu="game"
                tetra_rot = 0
                score = 0
                tetra_x = 5
                tetra_y = 0
                cur_tetra = random.randint(0,6)
            elif menu_option == 1:
                menu_option = 0
                menu="option"
            elif menu_option == 2:
                menu="scores"
            elif menu_option == 3:
                exit()

        menu_option = menu_option % len(options)
    elif menu=="game":
        if get_key_pressed("esc"):
            # write score
            if score > int(scores[-1][1]):
                menu="highscore"
            else:
                menu="start"
            game_over = False
            pause = False

        if get_key_pressed("p"):
            pause = not pause

        if (not pause) and (not game_over):
            if get_key_pressed("z"):
                new_rot = (tetra_rot+1) % len(TETRAMINO[cur_tetra])
                if not collision(tetra_x,tetra_y,TETRAMINO[cur_tetra][new_rot]):
                    tetra_rot = new_rot
            if get_key_pressed("x"):
                new_rot = (tetra_rot-1) % len(TETRAMINO[cur_tetra])
                if not collision(tetra_x,tetra_y,TETRAMINO[cur_tetra][new_rot]):
                    tetra_rot = new_rot
            if get_key_pressed("right"):
                if not collision(tetra_x+1,tetra_y,TETRAMINO[cur_tetra][tetra_rot]):
                    tetra_x += 1
            if get_key_pressed("left"):
                if not collision(tetra_x-1,tetra_y,TETRAMINO[cur_tetra][tetra_rot]):
                    tetra_x -= 1
            if get_key_pressed("down"):
                if not collision(tetra_x,tetra_y+1,TETRAMINO[cur_tetra][tetra_rot]):
                    tetra_y += 1

            # Checking holds
            if get_key("right"):
                if  key_timer[0] == 0:
                    if not collision(tetra_x+1,tetra_y,TETRAMINO[cur_tetra][tetra_rot]):
                        tetra_x += 1
                        key_timer[0] = HOLD_TIME
                else:
                    key_timer[0]-=1
            else:
                key_timer[0] = REPEAT_DELAY

            if get_key("left"):
                if  key_timer[1] == 0:
                    if not collision(tetra_x-1,tetra_y,TETRAMINO[cur_tetra][tetra_rot]):
                        tetra_x -= 1
                        key_timer[1] = HOLD_TIME
                else:
                    key_timer[1]-=1
            else:
                key_timer[1] = REPEAT_DELAY

            if get_key("down"):
                if  key_timer[2] == 0:
                    if not collision(tetra_x,tetra_y+1,TETRAMINO[cur_tetra][tetra_rot]):
                        tetra_y += 1
                        key_timer[2] = HOLD_TIME
                else:
                    key_timer[2]-=1
            else:
                key_timer[2] = REPEAT_DELAY 

    elif menu=="option":
        global grid_orientation

        if get_key_pressed("right") or get_key_pressed("enter"):
            if (menu_option == 0):
                grid_orientation = 1-grid_orientation
            elif (menu_option == 1):
                new_brightness = (get_brightness()+0.1) % 1
                set_brightness(1 if (new_brightness<0.1) else new_brightness)
            elif (menu_option == 2):
                networked = not networked
            else:
                drop_boost = (drop_boost + 1) % 10
        if get_key_pressed("esc"):
            set_orientation(grid_orientation)
            menu = "start"
            menu_option = 0
            drop_time = 100//(1+drop_boost)
            if networked:
                enable_networking()
            else:
                disable_networking()
        if get_key_pressed("left"):
            if (menu_option == 0):
                grid_orientation = 1-grid_orientation
            elif (menu_option == 1):
                new_brightness = (get_brightness()-0.1) % 1
                set_brightness(1 if (new_brightness<0.1) else new_brightness)
            elif (menu_option == 2):
                networked = not networked
            else:
                drop_boost = (drop_boost - 1) % 10
        if get_key_pressed("up"):
            menu_option-=1
        elif get_key_pressed("down"):
            menu_option+=1
        menu_option = menu_option % 4
    
    elif menu=="scores":
        if get_key_pressed("esc"):
            menu_option = 0
            menu = "start"

def collision(x,y,tetramino):
    for mino in tetramino:
        mino_x, mino_y = mino[0], mino[1]

        # check if in range
        if (y+mino_y < well_height-1) and (x+mino_x < well_width-1):
            if (well[x+mino_x][y+mino_y] != -1):
                return True
        else:
            return True
    return False

def check_clear():
    global well_height
    global well_width
    global well
    global BACKGROUND_COL
    global score

    clear_am = 0
    reset = False

    # checking every row
    for y_pos in range(well_height-1):
        clear = True

        # checking if the row below our current row is full
        for x_pos in range(len(well)-2):
            if well[x_pos+1][y_pos] == -1:
                clear = False
                break
        
        # if the row above it is full, then swap places
        if clear:
            BACKGROUND_COL = merge_color(BACKGROUND_COL,WHITE,0.025)
            reset = True
            clear_am += 1
            for x_pos in range(len(well)-2):
                well[x_pos+1][y_pos] = -1

        # shifting all the rows down
        if reset:
            for y_pos in reversed(range(well_height-2)):
                shift_row = True
                for x_pos in range(len(well)-2):
                    if well[x_pos+1][y_pos+1] != -1:
                        shift_row = False
                        break
                if shift_row:
                    for x_pos in range(len(well)-2):
                        well[x_pos+1][y_pos+1] = well[x_pos+1][y_pos]
                    
                    # empty fallen cells
                    for x_pos, column in enumerate(well):
                            column[y_pos] = 7 if (x_pos == 0 or x_pos == well_width-1) else -1
    score += clear_scores[clear_am]


def well_set_piece(x,y,tetramino):
    global cur_tetra

    for mino in tetramino:
        mino_x, mino_y = mino[0], mino[1]
        well[x+mino_x][y+mino_y] = cur_tetra

    check_clear()

def draw_game():
    global hue
    global mino_test
    global menu_t_y_pos
    global menu_t_x_pos
    global tetra_x
    global tetra_y
    global menu_tetramino
    global menu_tetramino_rot
    global menu_tetra_width
    global current_tetramino
    global cur_tetra
    global tetra_rot
    global menu_tetra_move
    global game_time
    global BACKGROUND_COL
    global game_over

    game_time+=1
    
    hue += 0.5
    mino_test+=0.01
    menu_t_y_pos+=0.1
    
    rainbow = color_hsv(hue,255,255)
    BACKGROUND_COL = merge_color(BACKGROUND_COL,(11,25,32),0.01)
    set_background_color(BACKGROUND_COL)

    option_offset = [0] * len(options)
    option_color  = [AQUA] * len(options)

    option_offset[menu_option] = 2+math.sin(hue/8)*2
    option_color[menu_option]  = WHITE

    if menu=="start":
        mino_rightmost = max(current_tetramino, key = lambda i : i[0])[0]
        menu_tetra_width = (mino_rightmost)+1
        screen_width = (get_width_adjusted()/MINO_SIZE)-menu_tetra_width
        menu_t_x_pos = max(0,min(screen_width,menu_t_x_pos+menu_tetra_move))

        # Tetris fun on screen
        for mino in current_tetramino:
            draw_sprite(math.floor(menu_t_x_pos)*MINO_SIZE+mino[0]*MINO_SIZE,MINO_SIZE+mino[1]*MINO_SIZE+math.floor(menu_t_y_pos)*MINO_SIZE,minos[menu_tetramino])

        if (random.randint(0,100) == 0):
            menu_tetramino_rot += 1
            current_tetramino = TETRAMINO[menu_tetramino][menu_tetramino_rot % len(TETRAMINO[menu_tetramino])]

        if (random.randint(0,275) == 0):
            menu_tetra_move = random.choice([-0.05, 0.05])

        if (menu_t_y_pos*4 > get_height_adjusted()):
            menu_tetra_move = 0
            menu_t_y_pos = -5
            menu_tetramino = random.randint(0,len(TETRAMINO)-1)
            menu_tetramino_rot = random.randint(0,3)
            current_tetramino = TETRAMINO[menu_tetramino][menu_tetramino_rot % len(TETRAMINO[menu_tetramino])]
            mino_rightmost = max(current_tetramino, key = lambda i : i[0])[0]
            menu_tetra_width = (mino_rightmost)+1
            screen_width = (get_width_adjusted()/MINO_SIZE)-menu_tetra_width
            menu_t_x_pos = random.randint(0,screen_width)

        # Menu Text
        draw_text(4,1,"TETNIS",rainbow)
        draw_line(4,13,38,13,rainbow)

        for order, option in enumerate(options):
            draw_text(6+option_offset[order],12+order*10,"> " + option,option_color[order])

    elif menu=="game":
        # Drawing the tetris piece
        for mino in TETRAMINO[cur_tetra][tetra_rot]:
            sprite = colorize(minos[cur_tetra],RED) if game_over else minos[cur_tetra]
            draw_sprite(mino[0]*MINO_SIZE+tetra_x*MINO_SIZE,mino[1]*MINO_SIZE+tetra_y*MINO_SIZE,sprite,0,0)
                        
        if get_orientation() == 0:
            for pos, char in enumerate(str(score)):
                draw_text(49,-3+8*pos,char,WHITE)
        else:
            draw_text(49,-3,"Score",WHITE)
            draw_text(49,6,str(score),WHITE) 

        # Drawing the minos in the well
        for row in range(0,well_height):
            for column in range(0,well_width):
                if (well[column][row] >= 0):
                    sprite = colorize(minos[well[column][row]],RED) if game_over else minos[well[column][row]]
                    draw_sprite(column*MINO_SIZE,row*MINO_SIZE,sprite)

        if (not pause) and (not game_over):
            if (game_time % drop_time == 0):
                if not collision(tetra_x,tetra_y+1,TETRAMINO[cur_tetra][tetra_rot]):
                    tetra_y+=1
                else:
                    well_set_piece(tetra_x,tetra_y,TETRAMINO[cur_tetra][tetra_rot])
                    tetra_y = 0
                    cur_tetra = random.randint(0,6)
                    tetra_rot = 0
                    tetra_x = 4
                    if well[6][2] != -1:
                        game_over = True

        else:
            center_text()
            draw_text(get_width_adjusted()//2,get_height_adjusted()//2,"Game Over" if game_over else "Paused",WHITE)
            reset_text()

    elif menu=="option":
        # Like with a lot of this code, there's way better ways to do this, this is kinda embarassing lol
        # This should not be copy and pasted like this, but I was lazy
        option_color = [(WHITE if row == menu_option else AQUA) for row in range(4)]

        options_menu = [("Vertical" if (grid_orientation==0) else "Horizontal"),
                       ("Light " + str(math.floor(get_brightness()*100)) + "%"),
                       ("Display: " + ("Yes" if (networked) else "No")),
                       ("Speed: " + str(1+drop_boost))]

        for row, title in enumerate(options_menu):
            draw_text(4,1+12*row,title, option_color[row])

    elif menu=="scores":
        # Draw hypercubes
        draw_hypercube(get_width_adjusted()//2,get_height_adjusted()//2,menu_cube,15*math.sin(hue/500),CYAN,[hue,hue*0.9,hue*0.8,hue*0.7])
        draw_hypercube(get_width_adjusted()//2,get_height_adjusted()//2,menu_cube,14.5*math.tan(hue/500),FUCHSIA,[hue,hue*0.9,hue*0.8,hue*0.7])

        # Draw overlay light
        set_blend_mode(BM_ADD)
        draw_image(get_width_adjusted()//2-30,get_height_adjusted()//2-30,"light.png",0,0,color_hsv(169+math.sin(hue/100)*42,255,159))
        set_blend_mode(BM_NORMAL)

        # darken background
        set_alpha(64)
        draw_rectangle(0,0,80,80,(0,0,0))
        set_alpha(255)

        # draw text
        draw_text(1,-2,"High Scores",WHITE)
        set_font(FNT_SMALL)
        for pos, text in enumerate(scores):
            draw_text(2,pos*10+8,text[0],WHITE)
            align_text_right()
            draw_text(get_width_adjusted()-1,pos*10+8,text[1],WHITE)
            align_text_left()
        reset_font()

def draw_scoreboard():
    global username
    global menu
    global scores

    center_text_horizontal()
    align_text_bottom()

    if get_orientation() % 2 == 0:
        set_font(FNT_SMALL)
    draw_text(get_width_adjusted()//2,get_height_adjusted()//2,"Enter Name!",WHITE)
    set_font(FNT_NORMAL)
    align_text_top()
    draw_text(get_width_adjusted()//2,get_height_adjusted()//2,username,WHITE)
    reset_text()
    draw()

    # max of 7 scores, I love my magical numbers lol, nope this isn't a constant or variable
    new_scores = []
    added = False

    # get keyboard input
    if get_key_pressed("enter"):
        menu = "scores"

        # adding the score where it belongs
        for old_score in scores:
            if not added and score > int(old_score[1]):
                added = True
                new_scores.append([username,str(score)])
            new_scores.append(old_score)

        scores = new_scores

        # saving the score file
        with open("highscores.txt", "w") as f:
            for possible_score in scores[0:7]:
                f.write(f"{possible_score[0]} {possible_score[1]}\n")

        # resetting the username
        username = "" 
    elif get_key_pressed("backspace"):
        username =  username[:-1]
    elif len(username) < 5:
        keys = "qwertyuiop[]\\asdfghjkl;'zxcvbnm,.1234567890/~!@#$%^&*()-_+ "
        for key in (keys.upper() if get_key("shift") else keys):
            if get_key_pressed(key):
                username += key
                username = username.replace(" ", "_")

while True:
    refresh()
    if menu == "highscore": # highscore: #
        draw_scoreboard()
    else:
        update_game()
        draw_game()
        draw()