def init():
    global rows_direction, columns_direction, space_pressed, coroutines,\
        obstacles, obstacles_in_last_collision
    rows_direction = 0
    columns_direction = 0
    space_pressed = False
    coroutines = []
    obstacles = []
    obstacles_in_last_collision = []
