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
    [NONE, obstacles.PENGUIN, obstacles.WATER],
    [NONE, NONE, NONE],
]

register(
    name="penguin_and_water_avoidance",
    description=(
"The car is positioned in the right lane (x=2). A penguin is located in the center lane one row ahead, "
        "and a water puddle is situated in the right lane, directly in the car's path, two rows ahead. "
        "The driver is expected to shift to the left lane to "
        "avoid the water while navigating past the obstacle in the center lane."
    ),
    track=track,
    car={"x": 2, "y": 8},
    expected=actions.LEFT,
    driver_module=mydriver,
)
