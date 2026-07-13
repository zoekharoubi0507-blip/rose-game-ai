"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA

driver_name = "CarDriver"

def drive(world):
    score = 0
    x = world.car.x
    y = world.car.y
    try:
        obstacle = world.get((x, y - 1))
    except IndexError:
        return actions.NONE
    else:
        obstacle = world.get((x, y - 2))

    ## מסתכל שלוש צעדים קדימה ובודק
    LOOK_AHEAD = 3
    for i in range(1, LOOK_AHEAD + 1):  # לולאה של 3 צעדים
        target_y = y - i
        try:
            obstacle_ahead = world.get((x, target_y))
        except IndexError:
            return actions.NONE
        if obstacle_ahead == obstacles.PENGUIN:
            if i == 1:
                score += 10
                return actions.PICKUP
            return actions.NONE

        elif obstacle_ahead == obstacles.CRACK:
            if i == 1:
                score += 5
                return actions.JUMP
            return actions.NONE

        elif obstacle_ahead == obstacles.WATER:
            if i == 1:
                score += 4
                return actions.BRAKE
            return actions.NONE

        elif obstacle == obstacles.NONE:
            return actions.NONE

        ###עקיפת מכשולים
        elif obstacle_ahead != obstacles.NONE:
            try:
                right_lane = world.get((x + 1, y))
                if right_lane == obstacles.NONE:
                    return actions.RIGHT
            except IndexError:
                pass
            try:
                left_lane = world.get((x - 1, y))
                if left_lane == obstacles.NONE:
                    return actions.LEFT
            except IndexError:
                pass
            return actions.NONE

        else:
            return actions.RIGHT if (x % 3) == 0 else actions.LEFT

    return actions.NONE


