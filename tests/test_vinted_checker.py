from unittest.mock import MagicMock, patch

from vinted_checker import search_item


@patch("vinted_checker.requests.get")
def test_search_item_hit(mock_get):
    resp = MagicMock()
    resp.json.return_value = {"items": [1]}
    resp.raise_for_status.return_value = None
    mock_get.return_value = resp
    assert search_item("shoes", 10.0)


@patch("vinted_checker.requests.get")
def test_search_item_miss(mock_get):
    resp = MagicMock()
    resp.json.return_value = {"items": []}
    resp.raise_for_status.return_value = None
    mock_get.return_value = resp
    assert not search_item("shoes", 10.0)
