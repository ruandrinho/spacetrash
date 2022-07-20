import time
import curses
from random import randint, choice
from control_tools import read_controls
from animations import blink, fire, animate_spaceship, fly_garbage
import global_vars


TIC_TIMEOUT = 0.1


def load_frame(model):
    with open(f'frames/{model}.txt') as file:
        return file.read()


def draw(canvas):
    global_vars.init()
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    rows, columns = canvas.getmaxyx()
    rocket_frame_1 = load_frame('rocket_frame_1')
    rocket_frame_2 = load_frame('rocket_frame_2')
    garbage_frame = load_frame('trash_large')
    coroutines = []
    coords_cache = [(0, 0)]
    for _ in range(200):
        y, x = 0, 0
        while (y, x) in coords_cache:
            y, x = randint(2, rows - 2), randint(2, columns - 2)
        coords_cache.append((y, x))
        coroutines.append(blink(canvas, y, x, choice('+*.:')))
    coroutines.append(fire(canvas, rows / 2, columns / 2))
    coroutines.append(animate_spaceship(canvas, rows//2 - 1, columns//2 - 2,
                                        rocket_frame_1, rocket_frame_2))
    coroutines.append(fly_garbage(canvas, 10, garbage_frame))
    while True:
        global_vars.rows_direction, global_vars.columns_direction,\
            global_vars.space_pressed = read_controls(canvas)
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        if not coroutines:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
