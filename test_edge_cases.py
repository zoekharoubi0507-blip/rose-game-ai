import pytest

import cases


@pytest.mark.parametrize("case", cases.CASES, ids=lambda c: c.name)
def test_edge_case(case):
    actual, error = cases.run(case)
    assert error is None, f"driver raised an exception: {error}"
    assert actual == case.expected
