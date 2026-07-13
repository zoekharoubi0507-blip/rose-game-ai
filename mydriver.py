"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA

driver_name = "MyDriver_elisha"


def drive(world):
    x = world.car.x
    y = world.car.y

    # ====== סריקת שתי השורות קדימה ======
    line1 = []  # שורה ראשונה (y - 1)
    line2 = []  # שורה שנייה (y - 2)

    for i in range(0, 3):
        line1.append(world.get((i, y - 1)))
        line2.append(world.get((i, y - 2)))

    # ====== חישוב ניקוד לכל משבצת ======
    def get_score(obstacle):
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

    # ניקודים לשורה הראשונה
    scores1 = [get_score(line1[i]) for i in range(3)]

    # ניקודים לשורה השנייה
    scores2 = [get_score(line2[i]) for i in range(3)]

    # ====== מציאת המסלול האופטימלי ======
    # נחפש את הנתיב הטוב ביותר: עמודה בשורה 1 -> עמודה בשורה 2

    best_score = float('-inf')
    best_next_x = None
    best_final_x = None

    # קבע אילו עמודות אפשר להגיע אליהן מהעמודה הנוכחית
    def can_reach(from_x, to_x):
        return abs(from_x - to_x) <= 1

    # בדוק כל נתיב אפשרי
    for next_x in range(3):  # עמודה בשורה הראשונה
        if not can_reach(x, next_x):
            continue  # לא יכול להגיע לשם

        for final_x in range(3):  # עמודה בשורה השנייה
            if not can_reach(next_x, final_x):
                continue  # לא יכול להגיע לשם

            # חשב את הניקוד הכולל לנתיב זה
            total_score = scores1[next_x] + scores2[final_x]

            if total_score > best_score:
                best_score = total_score
                best_next_x = next_x
                best_final_x = final_x

    # ====== החלטה איזה פעולה לעשות ======
    # בחר את הפעולה שתעביר אותנו לעמודה הטובה ביותר

    if best_next_x is None:
        best_next_x = x  # נשאר במקום אם אין אפשרות

    if best_next_x < x:
        move_action = actions.LEFT
    elif best_next_x > x:
        move_action = actions.RIGHT
    else:
        move_action = actions.NONE

    # ====== טיפול בעצם המכשול ======
    try:
        obstacle = world.get((x, y - 1))

        if obstacle == obstacles.PENGUIN:
            return actions.PICKUP
        elif obstacle == obstacles.CRACK:
            return actions.JUMP
        elif obstacle == obstacles.WATER:
            return actions.BRAKE
        else:
            return move_action
    except IndexError:
        return move_action