# import pytest


class TestMarkup:
    def test__tag(self):  # synced
        assert True

    class TestTag:
        pass


class TestHtml:
    def test___str__(self):  # synced
        assert True

    def test_text(self):  # synced
        assert True


class TestXml:
    def test___str__(self):  # synced
        assert True


class TestTagAccessor:
    def test___call__(self):  # synced
        assert True

    def test___getattr__(self):  # synced
        assert True


class TestTagProxy:
    def test___call__(self):  # synced
        assert True
