from hypothesis import given
import hypothesis.strategies as st
import rpi_sentry_core.camera as under_test
import os


@given(
    rank=st.floats(allow_infinity=False, allow_nan=False, min_value=0.0, max_value=1.0),
    timestamp=st.integers(min_value=0),
)
def test_photo_file_is_inside_two_character_dir(rank, timestamp):
    event = {"rank": rank, "timestamp": timestamp}
    assert under_test.photo_file_path(event)[2] == os.sep


@given(
    rank=st.floats(allow_infinity=False, allow_nan=False, min_value=0.0, max_value=1.0),
    timestamp=st.integers(min_value=0),
)
def test_photo_file_path_is_thirty_one_chars_long(rank, timestamp):
    event = {"rank": rank, "timestamp": timestamp}
    assert len(under_test.photo_file_path(event)) == 31


@given(
    rank=st.floats(allow_infinity=False, allow_nan=False, min_value=0.1, max_value=1.0),
    timestamp=st.integers(min_value=0),
)
def test_higher_file_name_order_for_higher_ranks(rank, timestamp):
    third_of_rank = rank / 3.0
    lower_rank = third_of_rank
    higher_rank = 2 * third_of_rank
    lower_rank_event = {"rank": lower_rank, "timestamp": timestamp}
    higher_rank_event = {"rank": higher_rank, "timestamp": timestamp}
    lower_rank_file_name = under_test.photo_file_path(lower_rank_event)[3:]
    higher_rank_file_name = under_test.photo_file_path(higher_rank_event)[3:]

    assert lower_rank_file_name < higher_rank_file_name
