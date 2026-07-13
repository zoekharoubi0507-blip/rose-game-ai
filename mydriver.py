from rose.common import obstacles, actions  # NOQA

driver_name = "MaxScoreDriver_dana"

def get_lane_score(world, lane_x, car_y, look_ahead=5):

    score = 0
    for i in range(1, look_ahead + 1):
        try:
            item = world.get((lane_x, car_y - i))
            
            if item == obstacles.PENGUIN:
                score += 20
            elif item == obstacles.CRACK:
                score += 15
            elif item == obstacles.WATER:
                score += 14
            elif item == obstacles.NONE:
                score += 10
            else:
                score -= 10 
        except IndexError:
            pass
            
    return score

def drive(world):
    x = world.car.x
    y = world.car.y
    
    try:
        immediate_obstacle = world.get((x, y - 2))
    except IndexError:
        immediate_obstacle = obstacles.NONE
        
    if immediate_obstacle == obstacles.PENGUIN:
        return actions.PICKUP
    elif immediate_obstacle == obstacles.CRACK:
        return actions.JUMP
    elif immediate_obstacle == obstacles.WATER:
        return actions.BRAKE
    
    lane_scores = {}
    for lane_x in range(3):
        lane_scores[lane_x] = get_lane_score(world, lane_x, y, look_ahead=5)
        
    best_lane = x
    best_score = lane_scores[x]
    
    for lane_x in range(3):
        if lane_scores[lane_x] > best_score:
            best_lane = lane_x
            best_score = lane_scores[lane_x]
            
    if best_lane > x:
        return actions.RIGHT
    elif best_lane < x:
        return actions.LEFT
        
    return actions.NONE