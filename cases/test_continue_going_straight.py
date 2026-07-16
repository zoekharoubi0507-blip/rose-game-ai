from rose.common import obstacles, actions
import mydriver
from tests_runner import register

# mydriver.py's CompetitionPolicy expects a full-size track: HEIGHT=9 rows,
# width a multiple of CELLS_PER_LANE=3 ,
# matching the shape used in rose/ai/server.py's docstring example).
NONE = obstacles.NONE
track = [
[NONE, NONE, NONE],
[NONE, NONE, NONE],
    [NONE, NONE, NONE],
    [NONE, NONE, NONE],
[NONE, NONE, NONE],
[NONE, NONE, NONE],
    [obstacles.BARRIER, obstacles.PENGUIN, obstacles.BARRIER],
    [obstacles.BARRIER, NONE, obstacles.BARRIER],
    [NONE, NONE, NONE],
]

register(
    name="trapped_penguin_block",
    description=(
        "The car is positioned in the center lane (x=1). The path ahead is heavily obstructed: barriers are placed on both the left and right lanes one row ahead, "
        "and a penguin is located in the center lane one row ahead. "
        "Since there is no clear path to shift lanes and the center lane is occupied, "
        "the driver is expected to perform none (or wait) "
        "until a clear path is identified."
    ),
    track=track,
    car={"x": 1, "y": 8},
    expected=actions.NONE,
    driver_module=mydriver,
)
