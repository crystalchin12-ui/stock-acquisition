from bursa_screener.exclusions import exclusion_reason, is_excluded


def test_known_syndicate_codes_are_excluded():
    assert is_excluded("7154")  # NexG Bina Berhad
    assert is_excluded("0200")  # Revenue Group Berhad
    assert exclusion_reason("7154")
    assert exclusion_reason("0200")


def test_unrelated_code_is_not_excluded():
    assert not is_excluded("03029")  # GPP Resources Berhad
    assert exclusion_reason("03029") == ""
