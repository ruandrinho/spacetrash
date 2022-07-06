import time
import asyncio
import curses
from random import randint, choice

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258
TIC_TIMEOUT = 0.1


def load_animation(model):
    with open(f'animations/{model}.txt') as file:
        return file.read()


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """
    Draw multiline text fragment on canvas,
    erase text instead of drawing if negative=True is specified.
    """

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of
            # the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """
    Calculate size of multiline text fragment,
    return pair — number of rows and colums.
    """

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def animate_spaceship(canvas, start_row, start_column, frame1, frame2,
                            speed=1):
    global rows_direction, columns_direction
    frame_counter = 0
    rows, columns = canvas.getmaxyx()
    height, width = get_frame_size(frame1)
    while True:
        if frame_counter % 4 < 2:
            negative_frame = frame1
            positive_frame = frame2
        else:
            negative_frame = frame2
            positive_frame = frame1
        frame_counter += 1
        draw_frame(canvas, start_row, start_column, negative_frame,
                   negative=True)
        draw_frame(canvas, start_row, start_column, positive_frame,
                   negative=True)
        start_row += rows_direction * speed
        start_column += columns_direction * speed
        if start_row < 1:
            start_row = 1
        if start_row + height > rows - 1:
            start_row = rows - 1 - height
        if start_column < 1:
            start_column = 1
        if start_column + width > columns - 1:
            start_column = columns - 1 - width
        draw_frame(canvas, start_row, start_column, positive_frame)
        await asyncio.sleep(0)


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


def draw(canvas):
    global rows_direction, columns_direction, space_pressed
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    rows, columns = canvas.getmaxyx()
    rocket_frame_1 = load_animation('rocket_frame_1')
    rocket_frame_2 = load_animation('rocket_frame_2')
    coroutines = []
    coords_cache = [(0, 0)]
    for i in range(200):
        y, x = 0, 0
        while (y, x) in coords_cache:
            y, x = randint(2, rows - 2), randint(2, columns - 2)
        coords_cache.append((y, x))
        coroutines.append(blink(canvas, y, x, choice('+*.:')))
    coroutines.append(fire(canvas, rows / 2, columns / 2))
    coroutines.append(animate_spaceship(canvas, rows//2 - 1, columns//2 - 2,
                                        rocket_frame_1, rocket_frame_2))
    while True:
        rows_direction, columns_direction, space_pressed =\
            read_controls(canvas)
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        if len(coroutines) == 0:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
