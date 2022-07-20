import asyncio
import curses
from random import randint, choice
from itertools import cycle
from frame_tools import get_frame_size, draw_frame, load_frame
from physics import update_speed
from obstacles import Obstacle
from explosion import explode
import global_vars


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def fill_orbit_with_garbage(canvas, columns):
    while True:
        frame = load_frame(choice(['trash_small', 'trash_large', 'trash_xl']))
        global_vars.coroutines.append(
            fly_garbage(canvas, randint(2, columns - 2), frame)
        )
        await sleep(randint(5, 20))


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        height, width = get_frame_size(garbage_frame)
        obstacle = Obstacle(row, column, height, width)
        global_vars.obstacles.append(obstacle)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        global_vars.obstacles.remove(obstacle)
        for injured in global_vars.obstacles_in_last_collision:
            if obstacle == injured:
                global_vars.coroutines.append(
                    explode(canvas, row + height/2, column + width/2)
                )
                return
        row += speed


async def run_spaceship(canvas, start_row, start_column, frame1, frame2,
                        row_speed=0, column_speed=0):
    rows, columns = canvas.getmaxyx()
    height, width = get_frame_size(frame1)
    for frame in cycle([frame2, frame1]):
        if global_vars.space_pressed:
            global_vars.coroutines.append(
                fire(canvas, start_row, start_column + width//2)
            )
        row_speed, column_speed = update_speed(
            row_speed, column_speed, global_vars.rows_direction,
            global_vars.columns_direction, 5, 10)
        start_row += row_speed
        start_column += column_speed
        start_row = max(1, start_row)
        start_row = min(rows - 1 - height, start_row)
        start_column = max(1, start_column)
        start_column = min(columns - 1 - width, start_column)
        draw_frame(canvas, start_row, start_column, frame)
        await sleep(2)
        draw_frame(canvas, start_row, start_column, frame,
                   negative=True)


async def fire(canvas, start_row, start_column, rows_speed=-0.3,
               columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in global_vars.obstacles:
            if obstacle.has_collision(round(row), round(column)):
                global_vars.obstacles_in_last_collision.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    for _ in range(randint(1, 20)):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)
