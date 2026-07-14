from rose.common import obstacles, actions

driver_name = "Group_8"
def drive(world):
    x = world.car.x
    y = world.car.y
    try:
        front = world.get((x, y - 1))
    except IndexError:
        front = obstacles.NONE

    if front == obstacles.PENGUIN:
        return actions.PICKUP

    if front == obstacles.CRACK:
        return actions.JUMP

    if front == obstacles.WATER:
        return actions.BRAKE
    lane_scores = {}
    for lane in range(3):
        score = 0
        blocked = False
        for dist in range(1, 5):
            try:
                obj = world.get((lane, y - dist))
            except IndexError:
                continue
            multiplier = 7 - dist
            if obj == obstacles.PENGUIN:
                score += 20 * multiplier
            elif obj == obstacles.CRACK:
                score += 15 * multiplier
            elif obj == obstacles.WATER:
                score += 14 * multiplier
            elif obj == obstacles.NONE:
                score += 10 * multiplier
            else:
                # obstacles
                score -= 10 * multiplier
                if dist == 1:
                    blocked = True
        if blocked:
            score -= 200
        lane_scores[lane] = score
    best_lane = x
    best_score = lane_scores[x]
    for lane in range(3):
        if lane_scores[lane] > best_score + 10:
            best_lane = lane
            best_score = lane_scores[lane]
    if best_lane > x:
        try:
            if world.get((x + 1, y - 1)) == obstacles.NONE:
                return actions.RIGHT
        except IndexError:
            pass
    elif best_lane < x:

        try:
            if world.get((x - 1, y - 1)) == obstacles.NONE:
                return actions.LEFT
        except IndexError:
            pass
    return actions.NONE