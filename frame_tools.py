def load_frame(model):
    with open(f'frames/{model}.txt') as file:
        return file.read()


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """
    Draw multiline text fragment on canvas,
    erase text instead of drawing if negative=True is specified.
    """

    canvas_height, canvas_width = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= canvas_height:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= canvas_width:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of
            # the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == canvas_height - 1 and column == canvas_width - 1:
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
