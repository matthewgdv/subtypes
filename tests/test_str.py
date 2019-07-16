import pytest
from subtypes.str import Str

hi = Str("Hello World!")


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
        assert hi.after(r"w") == "orld!"
        with pytest.raises(ValueError):
            hi.after(r"l")

    def test_after_first(self):
        assert hi.after_first(r"l") == "lo World!"

    def test_after_last(self):
        assert hi.after_last(r"l") == "d!"

    def test_before(self):
        assert hi.before(r"w") == "Hello "
        with pytest.raises(ValueError):
            hi.before(r"l")

    def test_before_first(self):
        assert hi.before_first(r"l") == "He"

    def test_before_last(self):
        assert hi.before_last(r"l") == "Hello Wor"

    def test_best_n_fuzzy_matches(self):
        assert [match for match, score in hi.best_n_fuzzy_matches(["Hello Worlds!", "Haii, I'm a world!", "Hiya World!", "Hi Friend!"], num=2)] == ["Hello Worlds!", "Hiya World!"]

    def test_camel_case(self):
        assert hi.camel_case() == "HelloWorld"

    def test_configure_fuzzy(self):
        val = Str("")
        val.configure_fuzzy(tokenize=True, partial=True)
        assert val.fuzzy.tokenize == True and val.fuzzy.partial == True

    def test_configure_re(self):
        val = Str("")
        val.configure_re(dotall=False, ignorecase=False, multiline=True)
        assert val.re.dotall == False and val.re.ignorecase == False and val.re.multiline == True

    def test_extract_uk_postcode(self):
        assert Str("Hi, I'm located at eh165pn.").extract_uk_postcode() == "EH16 5PN"

    def test_find_all(self):
        assert hi.find_all("l") == [2, 3, 9]

    def test_finditer(self):
        assert [match.group() for match in hi.finditer(r"\b[A-Za-z]+\b")] == ["Hello", "World"]

    def test_from_(self):
        assert hi.from_(r"w") == "World!"
        with pytest.raises(ValueError):
            hi.from_(r"l")

    def test_from_first(self):
        assert hi.from_first(r"l") == "llo World!"

    def test_from_last(self):
        assert hi.from_last(r"l") == "ld!"

    def test_fuzzy_match(self):
        assert hi.fuzzy_match("Hello Worlds!") > 95

    def test_identifier(self):
        assert Str("123Hello World!").identifier() == "_123_hello_world"

    @pytest.mark.parametrize(["value", "expected"], [("Snake", "Snakes"), ("Hero", "Heroes"), ("Princess", "Princesses"), ("Leaf", "Leaves"), ("Man", "Men"), ("Woman", "Women"), ("Tooth", "Teeth"), ("Mouse", "Mice"), ("Deer", "Deer")])
    def test_plural(self, value, expected):
        assert Str(value).plural() == expected

    def test_search(self):
        assert hi.search(r"\bwor[A-Za-z]+\b").group() == "World"

    def test_snake_case(self):
        assert hi.snake_case() == "hello_world"

    def test_splitre(self):
        assert Str("Hi, how's it going?").splitre(r",?\s+") == ["Hi", "how's", "it", "going?"]

    def test_strip_non_alphanumeric(self):
        assert hi.strip_non_alphanumeric() == "HelloWorld"

    def test_strip_non_ascii(self):
        assert Str("★Hi!★").strip_non_ascii() == "Hi!"

    def test_strip_whitespace(self):
        assert Str("\nHello   World!\n\t").strip_whitespace() == "Hello World!"

    def test_sub(self):
        assert hi.sub(r"world", "Friend") == "Hello Friend!"

    def test_to_clipboard(self):
        assert True

    def test_until(self):
        assert hi.until(r"w") == "Hello W"
        with pytest.raises(ValueError):
            hi.until(r"l")

    def test_until_first(self):
        assert hi.until_first(r"l") == "Hel"

    def test_until_last(self):
        assert hi.until_last(r"l") == "Hello Worl"
