import time
import curses
from control_tools import read_controls
from animations import start_animations
from game_state import count_year, print_game_state
import global_vars

TIC_TIMEOUT = 0.1


def draw(canvas):
    global_vars.init()
    canvas.nodelay(True)
    curses.curs_set(False)
    start_animations(canvas)
    global_vars.coroutines.append(count_year())
    global_vars.coroutines.append(print_game_state(canvas))
    while True:
        global_vars.rows_direction, global_vars.columns_direction,\
            global_vars.space_pressed = read_controls(canvas)
        for coroutine in global_vars.coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                global_vars.coroutines.remove(coroutine)
        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        if not global_vars.coroutines:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
