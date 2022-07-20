def init():
    global rows_direction, columns_direction, space_pressed, coroutines,\
        obstacles, obstacles_in_last_collision, year
    rows_direction = 0
    columns_direction = 0
    space_pressed = False
    year = 1957
    coroutines = []
    obstacles = []
    obstacles_in_last_collision = []
