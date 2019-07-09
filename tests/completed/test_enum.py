import pytest
from subtypes.enum import Enum


class Animal(Enum):
    PYTHON, DOG, CAT, GERBIL = "snek", 1, None, False


@pytest.mark.parametrize(["value", "expected"], [(member.name, member.value) for member in Animal])
def test_enum__getattribute__(value, expected):
    assert getattr(Animal, value) == expected


@pytest.mark.parametrize(["value", "expected"], [(member, member.value) for member in Animal])
def test_enum__str__(value, expected):
    assert str(value) == str(expected)


def test_enum_extend_enum():
    Animal.extend_enum(name="OTTER", value=1.5)
    assert Animal.OTTER == 1.5
