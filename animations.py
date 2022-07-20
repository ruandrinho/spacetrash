import asyncio
import curses
from random import randint, choice
from itertools import cycle
from frame_tools import get_frame_size, draw_frame, load_frame
import global_vars


async def fill_orbit_with_garbage(canvas, columns):
    while True:
        frame = load_frame(choice(['trash_small', 'trash_large', 'trash_xl']))
        global_vars.coroutines.append(
            fly_garbage(canvas, randint(2, columns - 2), frame)
        )
        for _ in range(randint(5, 20)):
            await asyncio.sleep(0)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def animate_spaceship(canvas, start_row, start_column, frame1, frame2,
                            speed=1):
    rows, columns = canvas.getmaxyx()
    height, width = get_frame_size(frame1)
    for frame in cycle([frame2, frame2, frame1, frame1]):
        start_row += global_vars.rows_direction * speed
        start_column += global_vars.columns_direction * speed
        start_row = max(1, start_row)
        start_row = min(rows - 1 - height, start_row)
        start_column = max(1, start_column)
        start_column = min(columns - 1 - width, start_column)
        draw_frame(canvas, start_row, start_column, frame)
        await asyncio.sleep(0)
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
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)
