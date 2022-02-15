import json

import azure.functions as func
import pytest
from unittest import mock

from Geocode import main
from Geocode import geocode
from Geocode import CACHE_EXPIRATION


@mock.patch("Geocode.geocode")
@mock.patch("redis.StrictRedis")
def test_main(mock_redis, mock_geocode):
    # Empty requests should be a 400
    resp = main(func.HttpRequest(method="GET", url="/", body="", params={}))
    assert resp.status_code == 400

    # Check a mainline request
    mock_geocode.return_value = {"lng": -75.123, "lat": 43.234}
    resp = main(
        func.HttpRequest(
            method="GET", url="/", body="", params={"address": "123 Fake St"}
        )
    )
    assert resp.status_code == 200
    mock_geocode.assert_called_with("123 Fake St", mock.ANY)

    coords = json.loads(resp.get_body())
    assert -75.123 == pytest.approx(coords.get("lng"))
    assert 43.234 == pytest.approx(coords.get("lat"))

    # Check that the geocoder raised an exception
    mock_geocode.side_effect = Exception("kablamo")
    resp = main(
        func.HttpRequest(
            method="GET", url="/", body="", params={"address": "234 Exception Ln"}
        )
    )
    assert resp.status_code == 500

    # Check what happens when we can't connect to redis
    mock_redis.side_effect = Exception("probably security groups")
    resp = main(func.HttpRequest(method="GET", url="/", body=""))

    assert resp.status_code == 400  # Should attempt to geocode anyway


@mock.patch("requests.get")
def test_geocode_cache_hit(mock_get):
    cache = mock.Mock()
    cache.get.return_value = json.dumps({"lng": -75.123, "lat": 43.234})

    resp = geocode("123 F@ke St", cache)
    assert cache.get.called_with("geocode::123FKEST")
    assert -75.123 == pytest.approx(resp.get("lng"))
    assert 43.234 == pytest.approx(resp.get("lat"))
    assert mock_get.not_called()


@mock.patch("requests.get")
def test_geocode_cache_miss(mock_get):
    cache = mock.Mock()
    cache.get.return_value = None

    mresp = mock.Mock()
    mresp.status_code = 200
    mresp.json.return_value = {
        "result": {"addressMatches": [{"coordinates": {"x": 1.0, "y": 2.0}}]}
    }

    mock_get.return_value = mresp

    resp = geocode("123 F@ke St", cache)
    mock_get.assert_called()
    assert 1.0 == pytest.approx(resp.get("lng"))
    assert 2.0 == pytest.approx(resp.get("lat"))
    cache.setex.assert_called_with(
        "geocode::123FKEST", CACHE_EXPIRATION, json.dumps(resp)
    )


@mock.patch("requests.get")
def test_geocode_failure(mock_get):
    cache = mock.Mock()
    cache.get.return_value = None

    mock_get.return_value = mock.Mock(status_code=500)

    with pytest.raises(Exception):
        geocode("123 Fake St", cache)

    cache.get.assert_called()
    cache.setex.assert_not_called()


@mock.patch("requests.get")
def test_geocode_empty(mock_get):
    cache = mock.Mock()
    cache.get.return_value = None

    mresp = mock.Mock()
    mresp.status_code = 200
    mresp.json.return_value = {"result": {"addressMatches": []}}

    mock_get.return_value = mresp

    with pytest.raises(Exception):
        geocode("123 Fake St", cache)

    cache.get.assert_called()
    cache.setex.assert_not_called()
