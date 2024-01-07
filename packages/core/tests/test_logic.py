from hypothesis import given
import hypothesis.strategies as st
import rpi_sentry_core.logic as under_test


@given(delta=st.floats(allow_nan=False), window=st.integers(min_value=1))
def test_rank_is_never_negative(delta, window):
    assert under_test.rank(window, delta) >= 0.0


@given(delta=st.floats(allow_nan=False), window=st.integers(min_value=1))
def test_rank_is_never_greater_than_one(delta, window):
    assert under_test.rank(window, delta) <= 1.0


@given(delta=st.floats(allow_nan=False), window=st.integers(min_value=1))
def test_rank_same_for_same_delta(delta, window):
    assert under_test.rank(window, delta) == under_test.rank(window, delta)


@given(window=st.integers(min_value=3))
def test_rank_higher_for_lower_deltas(window):
    third_of_window = window / 3.0
    higher_delta = 2 * third_of_window
    lower_delta = third_of_window
    assert under_test.rank(window, lower_delta) > under_test.rank(window, higher_delta)
