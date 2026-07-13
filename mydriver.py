"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA

driver_name = "MyDriver"


def drive(world):
    x = world.car.x
    y = world.car.y
    line=[]
    for  i in range(0,3):
        line[i]=world.get((i, y - 1))
    possible=[]
    for i in range(0, 3):
        if line[i]==obstacles.NONE: possible[i]=0
        elif line[i]==obstacles.CRACK: possible[i]=5
        elif line[i]==obstacles.PENGUIN:possible[i]=10
        elif line[i] == obstacles.WATER: possible[i] = 4
        else : possible[i]=-10

    if x==0:
        maximum=max(possible[0],possible[1])
    elif x==2:
        maximum = max(possible[1], possible[2])
    else:
        maximum = max(possible[1], possible[2], possible[0])

    idxmax=possible.index(maximum)

    if idxmax==0:
        if x==1:
            actions.LEFT
        else:
            actions.NONE
    elif idxmax==1:
        if x==1:
            actions.NONE
        elif x==0:
            actions.RIGHT
        else:
            actions.LEFT
    else:
        if x==2:
            actions.NONE
        else:
            actions.RIGHT


    try:
        obstacle = world.get((x, y - 1))
        if obstacle== obstacles.PENGUIN:
            return actions.PICKUP
        elif obstacle==obstacles.CRACK:
            return actions.JUMP
        elif obstacle==obstacles.WATER:
            return actions.BRAKE
        else:
             return actions.NONE
    except IndexError:
        return actions.NONE
    return actions.NONE

