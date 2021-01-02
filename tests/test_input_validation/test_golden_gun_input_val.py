from src.input_validation import golden_gun


def test_valid_input(author):
    content = "1 8 15 24 28"
    expected = {1, 8, 15, 24, 28}
    out, err = golden_gun(content, author)
    assert err == None
    assert out == expected


def test_negative_input(author):
    content = "-1"
    expected = None
    out, err = golden_gun(content, author)
    assert out == expected
    assert (
        err
        == "@AuthorName, the following could not be parsed to an integer.\nTry the `heros` command for a list of valid inputs\n\t['-1']"
    )


def test_too_large_digit(author):
    content = "1000000"
    expected_err = "@AuthorName, the following digits do not correspond to a valid hero.\nTry the `heros` command for a list of valid inputs\n\t['1000000']"
    out, err = golden_gun(content, author)
    assert out == None
    assert err == expected_err
