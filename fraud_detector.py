"""Transparent rules for the academic transaction risk demonstration."""

VALID_TYPES = {"PURCHASE", "TRANSFER", "WITHDRAWAL", "REFUND"}
HIGH_RISK_TYPES = set()  # Explicitly configurable; none enabled by default.
KNOWN_LOCATIONS = {"INDIA", "UNITED STATES", "UNITED KINGDOM", "CANADA", "AUSTRALIA", "SINGAPORE", "GERMANY", "FRANCE", "JAPAN"}


def classify_score(score: int) -> str:
    return "SUSPICIOUS" if score >= 50 else "LEGITIMATE"


def calculate_risk(amount: float, location: str, transaction_type: str) -> tuple[int, str]:
    points = 0
    if amount > 100_000:
        points += 30
    normalized = location.strip().upper()
    if normalized != "INDIA":
        points += 25
    if normalized not in KNOWN_LOCATIONS:
        points += 20
    if transaction_type in HIGH_RISK_TYPES:
        points += 25
    score = min(100, points)
    return score, classify_score(score)
