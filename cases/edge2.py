from rose.common import obstacles, actions
import mydriver
from . import register

# mydriver.py's CompetitionPolicy expects a full-size track: HEIGHT=9 rows,
# width a multiple of CELLS_PER_LANE=3 (this is 2 lanes of 3 cells each,
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
    [NONE, NONE, NONE],
    [NONE, NONE, NONE],
]

register(
    name="penguins_flanking_wall_ahead",
    description=(
        "Car sits centered in the left lane (x=1). Penguins flank it one "
        "row ahead in the left/right lanes; a wall sits two rows ahead in "
        "the left lane. Nothing blocks the car's own lane directly, so it "
        "should go straight."
    ),
    track=track,
    car={"x": 2, "y": 2},
    expected=actions.LEFT,
    driver_module=mydriver,
)
