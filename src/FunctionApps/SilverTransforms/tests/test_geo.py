from unittest import mock

from Transform.geo import cached_geocode


@mock.patch("Transform.geo.geocode")
def test_cached_geocode(patched_geocode):
    """On a miss, we should geocode and then store it"""
    patched_geocode.return_value = {"hello": "world"}

    mock_collection = mock.Mock()
    mock_collection.find_one.return_value = None

    resp = cached_geocode(mock_collection, mock.Mock(), "123 Fake St")
    assert resp == {"hello": "world"}  # whatever the mock returns

    # Make sure we updated the cache
    mock_collection.find_one.assert_called_with({"key": "123FAKEST"})
    mock_collection.insert_one.assert_called()


@mock.patch("Transform.geo.geocode")
def test_cached_geocode_hit(patched_geocode):
    """On a hit, we shouldn't geocode at all"""
    mock_collection = mock.Mock()
    mock_collection.find_one.return_value = {
        "x": "some-key",
        "key": "should-remove-this",
    }

    resp = cached_geocode(mock_collection, mock.Mock(), "123 Fake St")
    patched_geocode.assert_not_called()

    assert resp == {"x": "some-key"}
