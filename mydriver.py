"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA

driver_name = "MyDriverElisha4"



from rose.common import obstacles, actions

driver_name = "Michael Schumacher"  # אפשר לשנות לשם שתרצה שיוצג במשחק


LANE_WIDTH = 3  # 3 מסלולים בתוך הנתיב שלך: 0, 1, 2


def get_obstacle(world, x, y):
    """מחזיר את המכשול במיקום (x, y), או None אם המיקום מחוץ למסלול"""
    try:
        return world.get((x, y))
    except IndexError:
        return None


def stay_score_and_action(obstacle):
    """
    בודק אם ניתן להתמודד עם המכשול "ישר" (בלי לזוז לעמודה אחרת).
    מחזיר (ניקוד, פעולה).
    אם המכשול מחייב עקיפה (trash/bike/barrier) - מחזיר (None, None),
    כי אי אפשר "להישאר" מולו.
    """
    if obstacle is None or obstacle == obstacles.NONE:
        return 0, actions.NONE
    elif obstacle == obstacles.PENGUIN:
        return 10, actions.PICKUP
    elif obstacle == obstacles.WATER:
        return 4, actions.BRAKE
    elif obstacles.CRACK == obstacle:
        return 5, actions.JUMP
    else:
        # obstacles.TRASH, obstacles.BIKE, obstacles.BARRIER
        # אלו מכשולים שחובה לעקוף - אין דרך "להישאר" מולם
        return None, None


def lookahead_score(obstacle):
    """
    ניקוד גס להערכת מכשול בשורה השנייה קדימה (y - 2),
    לצורך תכנון לאיזה כיוון כדאי לעקוף.
    """
    if obstacle is None or obstacle == obstacles.NONE:
        return 0
    elif obstacle == obstacles.PENGUIN:
        return 10
    elif obstacle == obstacles.WATER:
        return 4
    elif obstacle == obstacles.CRACK:
        return 5
    else:
        # trash / bike / barrier - נעדיף לא להגיע לשם אם אפשר
        return -10


def drive(world):
    x = world.car.x
    y = world.car.y

    obstacle_ahead = get_obstacle(world, x, y - 1)

    # ניקוד לשורה השנייה קדימה, לכל אחד משלושת המסלולים - עוזר לבחור כיוון עקיפה חכם
    scores2 = [lookahead_score(get_obstacle(world, i, y - 2)) for i in range(LANE_WIDTH)]

    options = []  # (ניקוד_כולל, פעולה, עמודת_יעד)

    # אפשרות 1: להישאר באותה עמודה ולהתמודד ישירות עם המכשול (אם אפשרי)
    stay_score, stay_action = stay_score_and_action(obstacle_ahead)
    if stay_action is not None:
        options.append((stay_score + scores2[x], stay_action, x))

    # אפשרות 2: לעקוף שמאלה (bypass) - חוקי כמעט תמיד, גם לגבי trash/bike/barrier
    if x - 1 >= 0:
        options.append((0 + scores2[x - 1], actions.LEFT, x - 1))

    # אפשרות 3: לעקוף ימינה
    if x + 1 <= LANE_WIDTH - 1:
        options.append((0 + scores2[x + 1], actions.RIGHT, x + 1))

    # בחר את האפשרות הכי טובה.
    # שובר שוויון: קודם מעדיפים "להישאר" (פחות תזוזה מיותרת), ואז הכי קרוב לעמודה הנוכחית.
    best_total, best_action, best_target = max(
        options,
        key=lambda opt: (opt[0], opt[2] == x, -abs(opt[2] - x))
    )



    return best_action