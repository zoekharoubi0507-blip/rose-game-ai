"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA

driver_name = "MyDriver"


def drive(world):
    x = world.car.x
    y = world.car.y
    try:
        obstacle = world.get((x, y - 1))
    except IndexError:
        else:
        # Choose the best action for obstacle
    return actions.NONE
