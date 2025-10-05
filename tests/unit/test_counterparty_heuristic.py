import pytest

# Phase 1.1: initial failing imports (heuristic not yet implemented)
from extracta_app.src.normalization import counterparty_heuristic as ch  # type: ignore


@pytest.mark.parametrize(
    "description,expected",
    [
        ("", "Unknown"),  # empty
        ("   ", "Unknown"),  # whitespace
        ("12345", "Unknown"),  # numeric only (<3 non-digit letters)
        ("payment to visa", "Unknown"),  # stopword-only after filtering
        ("CARD PAYMENT RIMI LIETUVA", "Rimi Lietuva"),
        ("TRANSFER- SEB BANK", "Seb Bank"),
        ("pos: IKI     PREKYBA", "Iki Prekyba"),
        ("TRF   AMAZON EU SARL", "Amazon Eu Sarl"),
        ("purchase LIDL", "Lidl"),
        ("Card:  COFFEE-ISLAND-CAFE", "Coffee Island Cafe"),
    ],
)
def test_extract_counterparty_basic(description: str, expected: str):
    assert ch.extract_counterparty_name(description) == expected


def test_tie_break_longest_then_lex():
    # Construct description with two equal-length candidate sequences to force tie rule
    desc = "TRANSFER AAA BBB CCC"  # After stopwords removal AAA BBB CCC - choose earliest longest contiguous => AAA BBB CCC
    assert ch.extract_counterparty_name(desc) == "Aaa Bbb Ccc"


def test_placeholder_when_short_token():
    assert ch.extract_counterparty_name("PAYMENT TO AB") == "Unknown"  # 'ab' < 3 chars after filtering


def test_repository_integration_get_or_create(monkeypatch):
    calls = {"inserted": [], "lookups": []}

    class MockRepo:
        def __init__(self):
            self.store = {}
            self.seq = 1

        def get_or_create(self, normalized: str, display: str):
            calls["lookups"].append(normalized)
            if normalized in self.store:
                return self.store[normalized]
            self.store[normalized] = self.seq
            calls["inserted"].append(normalized)
            self.seq += 1
            return self.store[normalized]

    repo = MockRepo()
    # Two descriptions mapping to the same normalized name must yield one repo insert
    d1 = "CARD PAYMENT RIMI"
    d2 = "payment rimi"
    id1 = ch.get_or_create_counterparty_id(repo.get_or_create, d1)
    id2 = ch.get_or_create_counterparty_id(repo.get_or_create, d2)
    assert id1 == id2
    assert len(calls["inserted"]) == 1


# Negative / edge deterministic stability
@pytest.mark.parametrize("text", ["RIMI", "rimi", "Rimi   ", "rimi!!!"])
def test_normalization_stable(text: str):
    base = ch.extract_counterparty_name("Card Payment " + text)
    assert base == "Rimi"
