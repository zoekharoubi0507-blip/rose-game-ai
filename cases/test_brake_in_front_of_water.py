from rose.common import obstacles, actions
import mydriver
from . import register

# mydriver.py's CompetitionPolicy expects a full-size track: HEIGHT=9 rows,
# width a multiple of CELLS_PER_LANE=3,
# matching the shape used in rose/ai/server.py's docstring example).
NONE = obstacles.NONE
track = [
[NONE, NONE, NONE],
[NONE, NONE, NONE],
    [NONE, NONE, NONE],
    [NONE, NONE, NONE],
[NONE, NONE, NONE],
[NONE, NONE, NONE],
    [NONE, NONE, NONE],
    [obstacles.WATER, obstacles.BARRIER, obstacles.CRACK],
    [NONE, NONE, NONE],
]

register(
    name="water_block_stop",
    description=(
        "The car is positioned in the left lane (x=0). A water puddle is located one row ahead in the left lane,"
        " while a barrier and a crack are positioned in the center and right lanes, respectively."
        " Since all available lanes are blocked by hazards, "
        "the driver is expected to brake to avoid a collision."
    ),
    track=track,
    car={"x": 0, "y": 8},
    expected=actions.BRAKE,
    driver_module=mydriver,
)
