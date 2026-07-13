"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA

driver_name = "MyDriverElisha3"




def get_score(obstacle):
    """מחזיר את הניקוד של מכשול נתון"""
    if obstacle == obstacles.NONE:
        return 0
    elif obstacle == obstacles.CRACK:
        return 5
    elif obstacle == obstacles.PENGUIN:
        return 10
    elif obstacle == obstacles.WATER:
        return 4
    else:
        return -10


def can_reach(from_x, to_x):
    """האם אפשר לזוז מעמודה from_x לעמודה to_x בצעד אחד (שמאלה/ימינה/ישר)"""
    return abs(from_x - to_x) <= 1


def find_best_lane(x, scores1, scores2):
    """
    בודק את כל הנתיבים האפשריים לאורך 2 השורות הקרובות
    ומחזיר את העמודה הראשונה (next_x) שמובילה לניקוד הכולל הגבוה ביותר.
    במקרה של תיקו - מעדיף להישאר הכי קרוב לעמודה הנוכחית (פחות תזוזה מיותרת).
    """
    best_score = float('-inf')
    best_next_x = x
    best_distance = float('inf')  # מרחק מהעמודה הנוכחית, לצורך שובר שוויון

    for next_x in range(3):
        if not can_reach(x, next_x):
            continue

        for final_x in range(3):
            if not can_reach(next_x, final_x):
                continue

            total_score = scores1[next_x] + scores2[final_x]
            distance = abs(next_x - x)

            # עדכן אם: (1) ניקוד גבוה יותר, או (2) ניקוד שווה אבל תזוזה קטנה יותר
            if total_score > best_score or (total_score == best_score and distance < best_distance):
                best_score = total_score
                best_next_x = next_x
                best_distance = distance

    return best_next_x


def drive(world):
    x = world.car.x
    y = world.car.y

    # ====== סריקת שתי השורות קדימה ======
    line1 = [world.get((i, y - 1)) for i in range(3)]
    line2 = [world.get((i, y - 2)) for i in range(3)]

    scores1 = [get_score(obstacle) for obstacle in line1]
    scores2 = [get_score(obstacle) for obstacle in line2]

    # ====== מציאת העמודה הבאה הכי טובה ======
    best_next_x = find_best_lane(x, scores1, scores2)

    # ====== קביעת פעולת התזוזה ======
    if best_next_x < x:
        move_action = actions.LEFT
    elif best_next_x > x:
        move_action = actions.RIGHT
    else:
        move_action = actions.NONE


    # ====== טיפול במכשול ישירות מלפנים (עדיפות ראשונה) ======
    obstacle_ahead = line1[x]

    if obstacle_ahead == obstacles.PENGUIN:
        return actions.PICKUP
    elif obstacle_ahead == obstacles.CRACK:
        return actions.JUMP
    elif obstacle_ahead == obstacles.WATER:
        return actions.BRAKE
    else:
        return move_action