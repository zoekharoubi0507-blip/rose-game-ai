"""
Registry of driver edge-case scenarios.

Drop a new file in this directory that calls `register(...)` at import
time and it will automatically show up in CASES - both for the pytest
suite (test_edge_cases.py) and for the browser viewer (viz_server.py).
No other file needs to change.
"""

import importlib
import pkgutil
from dataclasses import dataclass

from rose.ai import world


@dataclass
class Case:
    name: str
    track: list
    car: dict
    expected: str
    driver_module: object
    description: str = ""


CASES = []


def register(name, track, car, expected, driver_module, description=""):
    CASES.append(
        Case(
            name=name,
            track=track,
            car=car,
            expected=expected,
            driver_module=driver_module,
            description=description,
        )
    )


def run(case):
    """
    Run a case's driver against its track.

    Returns (actual_action, error). error is None on success, otherwise the
    string representation of whatever exception the driver raised.
    """
    game_data = {"info": {"car": case.car}, "track": case.track}
    w = world.create(game_data)
    reset = getattr(case.driver_module, "reset_state", None)
    try:
        if reset is not None:
            reset()
        return case.driver_module.drive(w), None
    except Exception as e:
        return None, str(e)


def _discover():
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module_name}")


_discover()
