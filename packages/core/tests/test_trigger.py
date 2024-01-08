from hypothesis import given
import hypothesis.strategies as st
import rpi_sentry_core.api as api
import rpi_sentry_core.trigger as under_test
from unittest.mock import patch


@given(
    rank=st.floats(allow_infinity=False, allow_nan=False, min_value=0.0, max_value=1.0),
    timestamp=st.integers(min_value=0),
)
def test_file_is_inside_two_character_dir(rank, timestamp):
    event = api.TriggerEvent(rank=rank, timestamp=timestamp)
    path = under_test.file_path(event)
    assert len(path.dir_name) == 2


@given(
    rank=st.floats(allow_infinity=False, allow_nan=False, min_value=0.0, max_value=1.0),
    timestamp=st.integers(min_value=0),
)
def test_file_base_name_is_forty_two_chars_long(rank, timestamp):
    event = api.TriggerEvent(rank=rank, timestamp=timestamp)
    path = under_test.file_path(event)
    assert len(path.file_base_name) == 42


@given(
    rank=st.floats(allow_infinity=False, allow_nan=False, min_value=0.1, max_value=1.0),
    timestamp=st.integers(min_value=0),
)
def test_higher_rank_file_base_name_further_in_alphabetical_order(rank, timestamp):
    third_of_rank = rank / 3.0
    lower_rank = third_of_rank
    higher_rank = 2 * third_of_rank
    lower_rank_event = api.TriggerEvent(rank=lower_rank, timestamp=timestamp)
    higher_rank_event = api.TriggerEvent(rank=higher_rank, timestamp=timestamp)
    lower_rank_path = under_test.file_path(lower_rank_event)
    higher_rank_path = under_test.file_path(higher_rank_event)

    assert lower_rank_path.file_base_name < higher_rank_path.file_base_name


@given(
    later_timestamp=st.integers(min_value=2),
)
def test_no_file_base_name_collision_between_different_timestamps(later_timestamp):
    rank = 0.5
    earlier_timestamp = round(later_timestamp / 2)
    later_event = api.TriggerEvent(rank=rank, timestamp=later_timestamp)
    earlier_event = api.TriggerEvent(rank=rank, timestamp=earlier_timestamp)
    later_path = under_test.file_path(later_event)
    earlier_path = under_test.file_path(earlier_event)

    assert later_path.file_base_name != earlier_path.file_base_name


@given(
    dir_name=st.text(min_size=2, max_size=2),
    file_base_name=st.text(min_size=4, max_size=4),
    rank=st.floats(allow_infinity=False, allow_nan=False, min_value=0.5, max_value=1.0),
    timestamp=st.integers(min_value=0),
)
def test_records_events_ranked_half_or_more(dir_name, file_base_name, rank, timestamp):
    event = api.TriggerEvent(rank=rank, timestamp=timestamp)
    file_path = under_test.CaptureFilePath(
        dir_name=dir_name, file_base_name=file_base_name
    )
    with patch(
        "rpi_sentry_core.trigger.file_path", return_value=file_path
    ) as trigger_file_path_mock:
        with patch.object(api.Camera, "shoot") as camera_shoot_mock:
            under_test.activate(api.Camera(), None)(event)
            trigger_file_path_mock.assert_called_once_with(event)
            camera_shoot_mock.assert_called_once_with(rank, file_path)


@given(
    rank=st.floats(
        allow_infinity=False, allow_nan=False, min_value=0.0, max_value=0.49
    ),
    timestamp=st.integers(min_value=0),
)
def test_does_not_record_events_ranked_below_half(rank, timestamp):
    event = api.TriggerEvent(rank=rank, timestamp=timestamp)
    with patch.object(api.Camera, "shoot") as camera_shoot_mock:
        under_test.activate(api.Camera(), None)(event)
        camera_shoot_mock.assert_not_called()
