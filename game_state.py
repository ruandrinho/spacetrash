import asyncio
from animations import sleep
from game_scenario import get_caption_by_year
import global_vars


async def count_year():
    while True:
        await sleep(15)
        global_vars.year += 1


async def print_game_state(canvas):
    rows, columns = canvas.getmaxyx()
    subcanvas = canvas.derwin(3, 48, rows - 3, 0)
    while True:
        caption = f'{global_vars.year} {get_caption_by_year(global_vars.year)}'
        subcanvas.addstr(1, 2, caption)
        subcanvas.border()
        subcanvas.refresh()
        await asyncio.sleep(0)
