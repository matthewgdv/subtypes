import pytest

from subtypes import Str


@pytest.fixture
def default_string():
    return Str("Hello World!")


@pytest.fixture
def casing_test_string():
    return Str("| HiThis_is a CASINGTest-case &")


class TestCase:
    pass


class TestReprMixin:
    pass


class TestRegexAccessor:
    class TestSettings:
        def test___int__(self):  # synced
            assert True

        def test___and__(self):  # synced
            assert True

        def test___or__(self):  # synced
            assert True

        def test___rand__(self):  # synced
            assert True

        def test___ror__(self):  # synced
            assert True

        def test_to_flag(self):  # synced
            assert True

    def test___call__(self):  # synced
        assert True

    def test_search(self, default_string):  # synced
        assert default_string.re.search(r"\bwor[A-Za-z]+\b").group() == "World"

    def test_sub(self, default_string):  # synced
        assert default_string.re.sub(r"world", "Friend") == "Hello Friend!"

    def test_findall(self, default_string):  # synced
        assert [match.group() for match in default_string.re.findall(r"\b[A-Za-z]+\b")] == ["Hello", "World"]

    def test_split(self):  # synced
        assert Str("Hi, how's it going?").re.split(r",?\s+") == ["Hi", "how's", "it", "going?"]

    def test_escape(self):  # synced
        assert True


class TestFuzzyAccessor:
    class TestSettings:
        pass

    def test___call__(self):  # synced
        assert True

    def test_match(self, default_string):  # synced
        assert default_string.fuzzy.match("Hello Worlds!") > 95

    def test_best_n_matches(self, default_string):  # synced
        assert [
            match for match, score in default_string.fuzzy.best_n_matches(
                ["Hello Worlds!", "Haii, I'm a world!", "Hiya World!", "Hi Friend!"], num=2
            ).items()
        ] == ["Hello Worlds!", "Hiya World!"]

    def test__determine_matcher(self):  # synced
        assert True


class TestCasingAccessor:
    def test___call__(self):  # synced
        assert True

    def test_snake(self, casing_test_string):  # synced
        assert casing_test_string.case.snake() == "hi_this_is_a_casing_test_case"

    def test_camel(self, casing_test_string):  # synced
        assert casing_test_string.case.camel() == "hiThisIsACasingTestCase"

    def test_pascal(self, casing_test_string):  # synced
        assert casing_test_string.case.pascal() == "HiThisIsACasingTestCase"

    def test_dash(self, casing_test_string):  # synced
        assert casing_test_string.case.dash() == "hi-this-is-a-casing-test-case"

    def test_constant(self, casing_test_string):  # synced
        assert casing_test_string.case.constant() == "HI_THIS_IS_A_CASING_TEST_CASE"

    def test_dot(self, casing_test_string):  # synced
        assert casing_test_string.case.dot() == "hi.this.is.a.casing.test.case"

    def test_slash(self, casing_test_string):  # synced
        assert casing_test_string.case.slash() == "Hi/This/is/a/CASING/Test/case"

    def test_backslash(self, casing_test_string):  # synced
        assert casing_test_string.case.backslash() == R"Hi\This\is\a\CASING\Test\case"

    def test_identifier(self, casing_test_string):  # synced
        assert Str("123 Hello-world").case.identifier() == "_123_hello_world"

    @pytest.mark.parametrize(["value", "expected"], [
        ("Snake", "Snakes"), ("Hero", "Heroes"), ("Princess", "Princesses"), ("Leaf", "Leaves"),
        ("Man", "Men"), ("Woman", "Women"), ("Tooth", "Teeth"), ("Mouse", "Mice"), ("Deer", "Deer")
    ])
    def test_plural(self, value, expected):  # synced
        assert Str(value).case.plural() == expected

    def test_from_enum(self):  # synced
        assert True


class TestSliceAccessor:
    class TestSettings:
        pass

    def test___call__(self):  # synced
        assert True

    def test_before(self, default_string):  # synced
        assert default_string.slice.before(r"w") == "Hello "
        with pytest.raises(ValueError):
            default_string.slice.before(r"l")

    def test_before_first(self, default_string):  # synced
        assert default_string.slice.before_first(r"l") == "He"

    def test_before_last(self, default_string):  # synced
        assert default_string.slice.before_last(r"l") == "Hello Wor"

    def test_after(self, default_string):  # synced
        assert default_string.slice.after(r"w") == "orld!"
        with pytest.raises(ValueError):
            default_string.slice.after(r"l")

    def test_after_first(self, default_string):  # synced
        assert default_string.slice.after_first(r"l") == "lo World!"

    def test_after_last(self, default_string):  # synced
        assert default_string.slice.after_last(r"l") == "d!"

    def test_from_(self, default_string):  # synced
        assert default_string.slice.from_(r"w") == "World!"
        with pytest.raises(ValueError):
            default_string.slice.from_(r"l")

    def test_from_first(self, default_string):  # synced
        assert default_string.slice.from_first(r"l") == "llo World!"

    def test_from_last(self, default_string):  # synced
        assert default_string.slice.from_last(r"l") == "ld!"

    def test_until(self, default_string):  # synced
        assert default_string.slice.until(r"w") == "Hello W"
        with pytest.raises(ValueError):
            default_string.slice.until(r"l")

    def test_until_first(self, default_string):  # synced
        assert default_string.slice.until_first(r"l") == "Hel"

    def test_until_last(self, default_string):  # synced
        assert default_string.slice.until_last(r"l") == "Hello Worl"

    def test__slice_helper(self):  # synced
        assert True


class TestTrimAccessor:
    def test___call__(self):  # synced
        assert True

    def test_all_whitespace(self):  # synced
        assert True

    def test_whitespace_runs(self):  # synced
        assert Str("\nHello   World!\n\t").trim.whitespace_runs() == "Hello World!"

    def test_non_alphanumeric(self, default_string):  # synced
        assert default_string.trim.non_alphanumeric() == "HelloWorld"

    def test_non_ascii(self):  # synced
        assert Str("★Hi!★").trim.non_ascii() == "Hi!"


class TestBaseStr:
    def test___add__(self):  # synced
        assert True

    def test___radd__(self):  # synced
        assert True

    def test___mul__(self):  # synced
        assert True

    def test___rmul__(self):  # synced
        assert True

    def test___mod__(self):  # synced
        assert True

    def test___rmod__(self):  # synced
        assert True

    def test_capitalize(self):  # synced
        assert True

    def test_casefold(self):  # synced
        assert True

    def test_center(self):  # synced
        assert True

    def test_expandtabs(self):  # synced
        assert True

    def test_format(self):  # synced
        assert True

    def test_format_map(self):  # synced
        assert True

    def test_join(self):  # synced
        assert True

    def test_ljust(self):  # synced
        assert True

    def test_lower(self):  # synced
        assert True

    def test_lstrip(self):  # synced
        assert True

    def test_partition(self):  # synced
        assert True

    def test_replace(self):  # synced
        assert True

    def test_rjust(self):  # synced
        assert True

    def test_rpartition(self):  # synced
        assert True

    def test_rstrip(self):  # synced
        assert True

    def test_strip(self):  # synced
        assert True

    def test_swapcase(self):  # synced
        assert True

    def test_title(self):  # synced
        assert True

    def test_translate(self):  # synced
        assert True

    def test_upper(self):  # synced
        assert True

    def test_zfill(self):  # synced
        assert True


class TestStr:
    class TestAccessors:
        pass

    def test_re(self):  # synced
        assert True

    def test_case(self):  # synced
        assert True

    def test_slice(self):  # synced
        assert True

    def test_trim(self):  # synced
        assert True

    def test_fuzzy(self):  # synced
        assert True

    def test_to_clipboard(self):  # synced
        assert True

    def test_from_clipboard(self):  # synced
        assert True
