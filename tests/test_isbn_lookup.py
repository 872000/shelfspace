"""Tests for the offline ISBN lookup stub."""
from library import isbn_lookup


class TestIsbnLookup:
    def test_known_isbn_resolves(self):
        entry = isbn_lookup.lookup_isbn("9780141439518")
        assert entry is not None
        assert entry["title"] == "Pride and Prejudice"
        assert entry["author"] == "Jane Austen"
        assert entry["pages"] == 432

    def test_dashes_and_spaces_are_stripped(self):
        entry = isbn_lookup.lookup_isbn("978-0-14-143951-8")
        assert entry is not None
        assert entry["title"] == "Pride and Prejudice"

    def test_unknown_isbn_returns_none(self):
        assert isbn_lookup.lookup_isbn("9780000000000") is None

    def test_empty_and_none_return_none(self):
        assert isbn_lookup.lookup_isbn("") is None
        assert isbn_lookup.lookup_isbn(None) is None

    def test_catalog_has_useful_size(self):
        assert isbn_lookup.catalog_size() >= 10

    def test_normalize_isbn(self):
        assert isbn_lookup.normalize_isbn(" 978-0-14-143951-8 ") == "9780141439518"
        assert isbn_lookup.normalize_isbn("") == ""

    def test_lookup_makes_no_network_calls(self, monkeypatch):
        import socket
        def _boom(*args, **kwargs):
            raise AssertionError("network call attempted")
        monkeypatch.setattr(socket, "socket", _boom)
        assert isbn_lookup.lookup_isbn("9780140817744")["title"] == "1984"
