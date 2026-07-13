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



    try:
        obstacle1 = world.get((x, y - 1))
    except IndexError:


    else:
        # Choose the best action for obstacle
    return actions.NONE

