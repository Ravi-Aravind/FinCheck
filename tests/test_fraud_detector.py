import pytest

from fraud_detector import calculate_risk, classify_score


def test_low_risk_india_purchase():
    assert calculate_risk(2500, "India", "PURCHASE") == (0, "LEGITIMATE")


def test_high_value_amount_adds_thirty():
    assert calculate_risk(100001, "India", "PURCHASE")[0] == 30


def test_exactly_high_value_limit_does_not_add_points():
    assert calculate_risk(100000, "India", "PURCHASE")[0] == 0


def test_international_transaction_adds_twenty_five():
    assert calculate_risk(10, "United States", "PURCHASE")[0] == 25


def test_unknown_india_alias_gets_unknown_points_only_when_india_is_known():
    assert calculate_risk(10, "Atlantis", "PURCHASE")[0] == 45


def test_combined_rules_and_cap():
    assert calculate_risk(200000, "Atlantis", "PURCHASE") == (75, "SUSPICIOUS")


@pytest.mark.parametrize("score,status", [(0,"LEGITIMATE"),(49,"LEGITIMATE"),(50,"SUSPICIOUS"),(51,"SUSPICIOUS"),(100,"SUSPICIOUS")])
def test_threshold_classification(score,status):
    assert classify_score(score) == status
