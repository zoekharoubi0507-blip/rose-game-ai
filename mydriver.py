"""
This driver does not do any action.
"""

from rose.common import obstacles, actions  # NOQA



driver_name = "CarDriver"

DEBUG = True  # שנה ל-False כשהכל עובד טוב


def safe_get(world, x, y):
    """
    קריאה בטוחה ל-world.get - אף פעם לא זורקת שגיאה.
    מחזירה None אם המיקום לא חוקי (מחוץ למסלול).
    """
    try:
        return world.get((x, y))
    except IndexError:
        return None
    except Exception:
        return None


def direct_action_for(obstacle):
    """
    מחזיר (ניקוד, פעולה) עבור התמודדות ישירה (בלי לזוז לעמודה אחרת) עם המכשול.
    מחזיר (None, None) אם אי אפשר להתמודד ישירות (חייבים לעקוף - trash/bike/barrier),
    או אם obstacle הוא None (מיקום לא חוקי).
    """
    if obstacle is None:
        return None, None
    if obstacle == obstacles.NONE:
        return 0, actions.NONE
    if obstacle == obstacles.PENGUIN:
        return 10, actions.PICKUP
    if obstacle == obstacles.WATER:
        return 4, actions.BRAKE
    if obstacle == obstacles.CRACK:
        return 5, actions.JUMP
    # obstacles.TRASH / obstacles.BIKE / obstacles.BARRIER / כל דבר אחר לא מוכר
    return None, None


def rough_score(obstacle):
    """ניקוד גס להערכת מכשול, לשימוש בתכנון קדימה (שורה שנייה) בלבד"""
    if obstacle is None:
        return 0  # מיקום לא חוקי - נייטרלי, לא מעניש
    if obstacle == obstacles.NONE:
        return 0
    if obstacle == obstacles.PENGUIN:
        return 10
    if obstacle == obstacles.WATER:
        return 4
    if obstacle == obstacles.CRACK:
        return 5
    return -10  # trash / bike / barrier - עדיף להימנע


def drive(world):
    x = world.car.x
    y = world.car.y

    obstacle_ahead = safe_get(world, x, y - 1)

    options = []  # (ניקוד_כולל, פעולה, עמודת_יעד) - רק אפשרויות חוקיות

    # ====== אפשרות 1: להישאר באותה עמודה ולהתמודד ישירות ======
    stay_score, stay_action = direct_action_for(obstacle_ahead)
    if stay_action is not None:
        # ניקוד לשורה השנייה קדימה באותה עמודה (רק אם רלוונטי, מוגן מלא)
        lookahead_val = rough_score(safe_get(world, x, y - 2))
        options.append((stay_score + lookahead_val, stay_action, x))

    # ====== אפשרות 2: לעקוף שמאלה - בודקים אם זה בכלל חוקי (לא מניחים טווח) ======
    left_test = safe_get(world, x - 1, y - 1)
    if left_test is not None:
        lookahead_val = rough_score(safe_get(world, x - 1, y - 2))
        options.append((0 + lookahead_val, actions.LEFT, x - 1))

    # ====== אפשרות 3: לעקוף ימינה ======
    right_test = safe_get(world, x + 1, y - 1)
    if right_test is not None:
        lookahead_val = rough_score(safe_get(world, x + 1, y - 2))
        options.append((0 + lookahead_val, actions.RIGHT, x + 1))

    if DEBUG:
        print(f"[drive] x={x} y={y} obstacle_ahead={obstacle_ahead!r} options={options}")

    # ====== אם משום מה אין אף אפשרות חוקית - חזרה בטוחה ======
    if not options:
        if DEBUG:
            print("[drive] אין אפשרויות חוקיות! מחזיר NONE כברירת מחדל")
        return actions.NONE

    # ====== בחירת האפשרות הטובה ביותר ======
    # שובר שוויון: קודם מעדיפים "להישאר" (x==target), ואז הכי קרוב לעמודה הנוכחית
    best_total, best_action, best_target = max(
        options,
        key=lambda opt: (opt[0], opt[2] == x, -abs(opt[2] - x))
    )

    if DEBUG:
        print(f"[drive] נבחר: action={best_action} (target_x={best_target}, score={best_total})")

    return best_action