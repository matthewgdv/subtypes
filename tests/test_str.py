import pytest
from subtypes.str import Str

hi = Str("Hello World!")

# Str("| HiThis_is a CASINGTest-case &").case.snake() == "hi_this_is_a_casing_test_case"
# Str("| HiThis_is a CASINGTest-case &").case.camel() == "hiThisIsACasingTestCase"
# Str("| HiThis_is a CASINGTest-case &").case.pascal() == "HiThisIsACasingTestCase"
# Str("| HiThis_is a CASINGTest-case &").case.constant() == "HI_THIS_IS_A_CASING_TEST_CASE"
# Str("| HiThis_is a CASINGTest-case &").case.dash() == "hi-this-is-a-casing-test-case"
# Str("| HiThis_is a CASINGTest-case &").case.dot() == "hi.this.is.a.casing.test.case"
# Str("| HiThis_is a CASINGTest-case &").case.slash() == "Hi/This/is/a/CASING/Test/case"


class TestFuzzyMatcher:
    def test___call__(self):
        assert True

    def test___init__(self):
        assert True

    def test___repr__(self):
        assert True

    def test__determine_matcher(self):
        assert True

    def test_configure(self):
        assert True

    def test_match(self):
        assert True


class TestRegexSettings:
    def test___and__(self):
        assert True

    def test___call__(self):
        assert True

    def test___init__(self):
        assert True

    def test___or__(self):
        assert True

    def test___rand__(self):
        assert True

    def test___ror__(self):
        assert True

    def test_get_flag(self):
        assert True


class TestStr:
    def test___init__(self):
        assert True

    def test___setitem__(self):
        assert hi[1:4] == "ell"

    def test__slice_helper(self):
        assert True

    def test_after(self):
        assert hi.slice.after(r"w") == "orld!"
        with pytest.raises(ValueError):
            hi.slice.after(r"l")

    def test_after_first(self):
        assert hi.slice.after_first(r"l") == "lo World!"

    def test_after_last(self):
        assert hi.slice.after_last(r"l") == "d!"

    def test_before(self):
        assert hi.slice.before(r"w") == "Hello "
        with pytest.raises(ValueError):
            hi.slice.before(r"l")

    def test_before_first(self):
        assert hi.slice.before_first(r"l") == "He"

    def test_before_last(self):
        assert hi.slice.before_last(r"l") == "Hello Wor"

    def test_best_n_fuzzy_matches(self):
        assert [match for match, score in hi.fuzzy.best_n_matches(["Hello Worlds!", "Haii, I'm a world!", "Hiya World!", "Hi Friend!"], num=2)] == ["Hello Worlds!", "Hiya World!"]

    def test_camel_case(self):
        assert hi.case.camel() == "HelloWorld"

    def test_configure_fuzzy(self):
        accessor = Str("").fuzzy(tokenize=True, partial=True)
        assert accessor.settings.tokenize == True and accessor.settings.partial == True

    def test_configure_re(self):
        accessor = Str("").re(dotall=False, ignorecase=False, multiline=True)
        assert accessor.settings.dotall == False and accessor.settings.ignorecase == False and accessor.settings.multiline == True

    def test_extract_uk_postcode(self):
        assert Str("Hi, I'm located at eh165pn.").extract_uk_postcode() == "EH16 5PN"

    def test_find_all(self):
        assert hi.find_all("l") == [2, 3, 9]

    def test_finditer(self):
        assert [match.group() for match in hi.re.finditer(r"\b[A-Za-z]+\b")] == ["Hello", "World"]

    def test_from_(self):
        assert hi.slice.from_(r"w") == "World!"
        with pytest.raises(ValueError):
            hi.slice.from_(r"l")

    def test_from_first(self):
        assert hi.slice.from_first(r"l") == "llo World!"

    def test_from_last(self):
        assert hi.slice.from_last(r"l") == "ld!"

    def test_fuzzy_match(self):
        assert hi.fuzzy.match("Hello Worlds!") > 95

    def test_identifier(self):
        assert Str("123Hello World!").case.identifier() == "_123_hello_world"

    @pytest.mark.parametrize(["value", "expected"], [("Snake", "Snakes"), ("Hero", "Heroes"), ("Princess", "Princesses"), ("Leaf", "Leaves"), ("Man", "Men"), ("Woman", "Women"), ("Tooth", "Teeth"), ("Mouse", "Mice"), ("Deer", "Deer")])
    def test_plural(self, value, expected):
        assert Str(value).case.plural() == expected

    def test_search(self):
        assert hi.re.search(r"\bwor[A-Za-z]+\b").group() == "World"

    def test_snake_case(self):
        assert hi.case.snake() == "hello_world"

    def test_re_split(self):
        assert Str("Hi, how's it going?").re.split(r",?\s+") == ["Hi", "how's", "it", "going?"]

    def test_trim_non_alphanumeric(self):
        assert hi.trim.non_alphanumeric() == "HelloWorld"

    def test_trim_non_ascii(self):
        assert Str("★Hi!★").trim.non_ascii() == "Hi!"

    def test_trim_whitespace(self):
        assert Str("\nHello   World!\n\t").trim.all_whitespace() == "Hello World!"

    def test_re_sub(self):
        assert hi.re.sub(r"world", "Friend") == "Hello Friend!"

    def test_to_clipboard(self):
        assert True

    def test_until(self):
        assert hi.slice.until(r"w") == "Hello W"
        with pytest.raises(ValueError):
            hi.slice.until(r"l")

    def test_until_first(self):
        assert hi.slice.until_first(r"l") == "Hel"

    def test_until_last(self):
        assert hi.slice.until_last(r"l") == "Hello Worl"
