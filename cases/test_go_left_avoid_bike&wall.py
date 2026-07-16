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
    [NONE, NONE, NONE],
    [NONE, obstacles.BIKE, obstacles.BARRIER],
    [NONE, NONE, NONE],
]

register(
    name="bike_avoidance_path",
    description=(
        "The car is positioned in the center lane (x=1). A bike is detected in the center lane one row ahead, "
        "and a barrier is positioned in the right lane at the same distance. "
        "Since the left lane is clear and the current path is blocked by the bike, "
        "the driver is expected to shift to the left lane to bypass the obstacle."
    ),
    track=track,
    car={"x": 1, "y": 8},
    expected=actions.LEFT,
    driver_module=mydriver,
)
