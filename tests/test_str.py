import pytest
from subtypes.str import Str

hi = Str("Hello World!")


def test_FuzzyMatcher___call__():
    assert True


def test_FuzzyMatcher___init__():
    assert True


def test_FuzzyMatcher___repr__():
    assert True


def test_FuzzyMatcher__determine_matcher():
    assert True


def test_FuzzyMatcher_configure():
    assert True


def test_FuzzyMatcher_match():
    assert True


def test_RegexSettings___and__():
    assert True


def test_RegexSettings___call__():
    assert True


def test_RegexSettings___init__():
    assert True


def test_RegexSettings___or__():
    assert True


def test_RegexSettings___rand__():
    assert True


def test_RegexSettings___ror__():
    assert True


def test_RegexSettings_get_flag():
    assert True


def test_Str___init__():
    assert True


def test_Str___setitem__():
    assert hi[1:4] == "ell"


def test_Str__slice_helper():
    assert True


def test_Str_after():
    assert hi.after(r"w") == "orld!"
    with pytest.raises(ValueError):
        hi.after(r"l")


def test_Str_after_first():
    assert hi.after_first(r"l") == "lo World!"


def test_Str_after_last():
    assert hi.after_last(r"l") == "d!"


def test_Str_before():
    assert hi.before(r"w") == "Hello "
    with pytest.raises(ValueError):
        hi.before(r"l")


def test_Str_before_first():
    assert hi.before_first(r"l") == "He"


def test_Str_before_last():
    assert hi.before_last(r"l") == "Hello Wor"


def test_Str_best_n_fuzzy_matches():
    assert [match for match, score in hi.best_n_fuzzy_matches(["Hello Worlds!", "Haii, I'm a world!", "Hiya World!", "Hi Friend!"], num=2)] == ["Hello Worlds!", "Hiya World!"]


def test_Str_camel_case():
    assert hi.camel_case() == "HelloWorld"


def test_Str_configure_fuzzy():
    val = Str("")
    val.configure_fuzzy(tokenize=True, partial=True)
    assert val.fuzzy.tokenize == True and val.fuzzy.partial == True


def test_Str_configure_re():
    val = Str("")
    val.configure_re(dotall=False, ignorecase=False, multiline=True)
    assert val.re.dotall == False and val.re.ignorecase == False and val.re.multiline == True


def test_Str_extract_uk_postcode():
    assert Str("Hi, I'm located at eh165pn.").extract_uk_postcode() == "EH16 5PN"


def test_Str_find_all():
    assert hi.find_all("l") == [2, 3, 9]


def test_Str_finditer():
    assert [match.group() for match in hi.finditer(r"\b[A-Za-z]+\b")] == ["Hello", "World"]


def test_Str_from_():
    assert hi.from_(r"w") == "World!"
    with pytest.raises(ValueError):
        hi.from_(r"l")


def test_Str_from_first():
    assert hi.from_first(r"l") == "llo World!"


def test_Str_from_last():
    assert hi.from_last(r"l") == "ld!"


def test_Str_fuzzy_match():
    assert hi.fuzzy_match("Hello Worlds!") > 95


def test_Str_identifier():
    assert Str("123Hello World!").identifier() == "_123_hello_world"


@pytest.mark.parametrize(["value", "expected"], [("Snake", "Snakes"), ("Hero", "Heroes"), ("Princess", "Princesses"), ("Leaf", "Leaves"), ("Man", "Men"), ("Woman", "Women"), ("Tooth", "Teeth"), ("Mouse", "Mice"), ("Deer", "Deer")])
def test_Str_plural(value, expected):
    assert Str(value).plural() == expected


def test_Str_search():
    assert hi.search(r"\bwor[A-Za-z]+\b").group() == "World"


def test_Str_snake_case():
    assert hi.snake_case() == "hello_world"


def test_Str_splitre():
    assert Str("Hi, how's it going?").splitre(r",?\s+") == ["Hi", "how's", "it", "going?"]


def test_Str_strip_non_alphanumeric():
    assert hi.strip_non_alphanumeric() == "HelloWorld"


def test_Str_strip_non_ascii():
    assert Str("★Hi!★").strip_non_ascii() == "Hi!"


def test_Str_strip_whitespace():
    assert Str("\nHello   World!\n\t").strip_whitespace() == "Hello World!"


def test_Str_sub():
    assert hi.sub(r"world", "Friend") == "Hello Friend!"


def test_Str_to_clipboard():
    assert True


def test_Str_until():
    assert hi.until(r"w") == "Hello W"
    with pytest.raises(ValueError):
        hi.until(r"l")


def test_Str_until_first():
    assert hi.until_first(r"l") == "Hel"


def test_Str_until_last():
    assert hi.until_last(r"l") == "Hello Worl"
