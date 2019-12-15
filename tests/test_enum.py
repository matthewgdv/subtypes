import pytest
from subtypes.enums import Enum


class Animal(Enum):
    PYTHON, DOG, CAT, GERBIL = "snek", 1, None, False


class TestEnumMeta:
    @pytest.mark.parametrize(["value", "expected"], [(member.name, member.value) for member in Animal])
    def test___getattribute__(self, value, expected):
        assert getattr(Animal, value) == expected

    def test___repr__(self):
        assert True

    @pytest.mark.parametrize(["value", "expected"], [(member, member.value) for member in Animal])
    def test___str__(self, value, expected):
        assert str(value) == str(expected)

    def test_extend_enum(self):
        Animal.extend_enum(name="OTTER", value=1.5)
        assert Animal.OTTER == 1.5
