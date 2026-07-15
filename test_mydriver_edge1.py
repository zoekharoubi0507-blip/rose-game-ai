from rose.ai import world
from rose.common import obstacles, actions
import mydriver


def test_edge1_penguins_flanking_with_wall_ahead():
    """
    Track layout (row 0 = farthest ahead, last row = car's row):

        highest row (2 ahead): wall,    air,     air
        middle row  (1 ahead): penguin, air,     penguin
        lowest row  (car row): air,     car,     air

    Car sits in the middle lane. No obstacle directly in front of it,
    so it should just go straight (NONE).
    """
    track = [
        [obstacles.BARRIER, obstacles.NONE, obstacles.NONE],
        [obstacles.PENGUIN, obstacles.NONE, obstacles.PENGUIN],
        [obstacles.NONE, obstacles.NONE, obstacles.NONE],
    ]
    game_data = {
        "info": {"car": {"x": 1, "y": 2}},
        "track": track,
    }

    w = world.create(game_data)
    action = mydriver.drive(w)

    assert action == actions.NONE
