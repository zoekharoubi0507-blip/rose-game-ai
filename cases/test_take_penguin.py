from rose.common import obstacles, actions
import mydriver
from . import register

# mydriver.py's CompetitionPolicy expects a full-size track: HEIGHT=9 rows,
# width a multiple of CELLS_PER_LANE=3
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
    [NONE, obstacles.PENGUIN, obstacles.CRACK],
    [NONE, obstacles.BIKE, NONE],
]

register(
    name="penguin_and_crack_avoidance",
    description=(
        "The car is currently positioned in the left lane (x=0). Obstacles are detected one row ahead: "
        "a penguin in the center lane and a crack in the right lane."
        " Since the center lane is directly blocked by the penguin, the driver is expected to shift to the right lane, "
        "going around around the central obstacle to maintain forward progress."
    ),
    track=track,
    car={"x": 0, "y": 8},
    expected=actions.RIGHT,
    driver_module=mydriver,
)
