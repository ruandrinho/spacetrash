import asyncio
import curses
from random import randint, choice
from itertools import cycle
from frame_tools import get_frame_size, draw_frame, load_frame
from physics import update_speed
from obstacles import Obstacle
from explosion import explode
from game_scenario import get_garbage_delay_tics
import global_vars


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def start_animations(canvas):
    canvas_height, canvas_width = canvas.getmaxyx()

    coords_cache = [(0, 0)]
    for _ in range(200):
        y, x = 0, 0
        while (y, x) in coords_cache:
            y, x = randint(2, canvas_height - 2), randint(2, canvas_width - 2)
        coords_cache.append((y, x))
        global_vars.coroutines.append(blink(canvas, y, x, choice('+*.:')))

    global_vars.coroutines.append(
        run_spaceship(canvas, canvas_height//2 - 1, canvas_width//2 - 2))

    global_vars.coroutines.append(
        fill_orbit_with_garbage(canvas))


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


async def run_spaceship(canvas, row, column, row_speed=0,
                        column_speed=0):
    frame1 = load_frame('rocket_frame_1')
    frame2 = load_frame('rocket_frame_2')

    canvas_height, canvas_width = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(frame1)

    for frame in cycle([frame2, frame1]):
        if global_vars.space_pressed and global_vars.year >= 2020:
            global_vars.coroutines.append(
                fire(canvas, row, column + frame_width//2)
            )

        row_speed, column_speed = update_speed(
            row_speed, column_speed, global_vars.rows_direction,
            global_vars.columns_direction, 5, 10)
        row += row_speed
        column += column_speed
        row = max(1, row)
        row = min(canvas_height - 1 - frame_height, row)
        column = max(1, column)
        column = min(canvas_width - 1 - frame_width, column)

        draw_frame(canvas, row, column, frame)
        await sleep(2)
        draw_frame(canvas, row, column, frame, negative=True)

        for obstacle in global_vars.obstacles:
            if obstacle.has_collision(round(row), round(column),
                                      frame_height, frame_width):
                global_vars.obstacles_in_last_collision.append(obstacle)
                global_vars.coroutines.append(show_gameover(canvas))
                return


async def fill_orbit_with_garbage(canvas):
    canvas_height, canvas_width = canvas.getmaxyx()

    while True:
        garbage_delay_tics = get_garbage_delay_tics(global_vars.year)
        if not garbage_delay_tics:
            await sleep(15)
            continue

        global_vars.coroutines.append(
            fly_garbage(canvas, randint(2, canvas_width - 2))
        )
        await sleep(garbage_delay_tics)


async def fly_garbage(canvas, column, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""

    frame = load_frame(choice(['trash_small', 'trash_large', 'trash_xl']))

    canvas_height, canvas_width = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, canvas_width - 1)

    row = 0

    while row < canvas_height:
        draw_frame(canvas, row, column, frame)
        frame_height, frame_width = get_frame_size(frame)

        obstacle = Obstacle(row, column, frame_height, frame_width)
        global_vars.obstacles.append(obstacle)

        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)
        global_vars.obstacles.remove(obstacle)

        for injured in global_vars.obstacles_in_last_collision:
            if obstacle == injured:
                global_vars.coroutines.append(
                    explode(canvas, row + frame_height/2,
                            column + frame_width/2)
                )
                return

        row += speed


async def fire(canvas, row, column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    canvas_height, canvas_width = canvas.getmaxyx()
    max_row, max_column = canvas_height - 1, canvas_width - 1

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


async def show_gameover(canvas):
    frame = load_frame('gameover')
    canvas_height, canvas_width = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(frame)

    while True:
        draw_frame(canvas, canvas_height/2 - frame_height/2,
                   canvas_width/2 - frame_width/2, frame)
        await asyncio.sleep(0)
