from unittest.mock import Mock

import pytest

import cached_backend


def test_fetch_data_calls_function_once():
    fetch = Mock(return_value=['ok'])
    cached = cached_backend.CachedBackendCall(fetch)

    assert cached.fetch_data() == ['ok']
    assert cached.fetch_data() == ['ok']
    assert fetch.call_count == 1


def test_fetch_data_fails_fast():
    fetch = Mock(side_effect=RuntimeError('down'))
    cached = cached_backend.CachedBackendCall(fetch)

    with pytest.raises(RuntimeError, match='down'):
        cached.fetch_data()

    assert fetch.call_count == 1
