import time
import curses
from random import randint, choice
from control_tools import read_controls
from animations import blink, fire, animate_spaceship
from animations import fill_orbit_with_garbage
from frame_tools import load_frame
import global_vars


TIC_TIMEOUT = 0.1


def print_on_canvas(canvas, row, column, *args):
    output = ''
    for arg in args:
        output += str(arg)
    canvas.addstr(row, column, output)


def draw(canvas):
    global_vars.init()
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    rows, columns = canvas.getmaxyx()
    rocket_frame_1 = load_frame('rocket_frame_1')
    rocket_frame_2 = load_frame('rocket_frame_2')
    coords_cache = [(0, 0)]
    for _ in range(200):
        y, x = 0, 0
        while (y, x) in coords_cache:
            y, x = randint(2, rows - 2), randint(2, columns - 2)
        coords_cache.append((y, x))
        global_vars.coroutines.append(blink(canvas, y, x, choice('+*.:')))
    # global_vars.coroutines.append(fire(canvas, rows / 2, columns / 2))
    global_vars.coroutines.append(
        animate_spaceship(canvas, rows//2 - 1, columns//2 - 2,
                          rocket_frame_1, rocket_frame_2))
    global_vars.coroutines.append(fill_orbit_with_garbage(canvas, columns))
    while True:
        global_vars.rows_direction, global_vars.columns_direction,\
            global_vars.space_pressed = read_controls(canvas)
        for coroutine in global_vars.coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                global_vars.coroutines.remove(coroutine)
        canvas.border()
        print_on_canvas(canvas, 2, 2, len(global_vars.coroutines))
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        if not global_vars.coroutines:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
