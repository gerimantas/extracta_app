import textwrap
from pathlib import Path

try:
    from src.common.mapping_loader import load_mapping_config, resolve_headers  # type: ignore
except ImportError:
    load_mapping_config = None  # type: ignore
    resolve_headers = None  # type: ignore


YAML_CONTENT = textwrap.dedent(
    """
    version: v1
    synonyms:
      amount_out: ["debit", "money out"]
      amount_in: ["credit", "money in"]
    rules:
      Date: transaction_date
      Description: description
    file_overrides:
      - pattern: "special_statement.pdf"
        headers:
          Outgoing: amount_out
    """
)


def write_yaml(tmp_path: Path) -> Path:
    p = tmp_path / 'mappings.yml'
    p.write_text(YAML_CONTENT, encoding='utf-8')
    return p


def test_mapping_loader_basic(tmp_path: Path):
    assert load_mapping_config is not None, "mapping_loader not implemented (Task 16 pending)"
    config_path = write_yaml(tmp_path)
    cfg = load_mapping_config(config_path)
    assert cfg.version == 'v1'
    # synonyms present
    assert 'amount_out' in cfg.synonyms


def test_header_resolution_precedence(tmp_path: Path):
    assert resolve_headers is not None, "mapping_loader not implemented (Task 16 pending)"
    config_path = write_yaml(tmp_path)
    cfg = load_mapping_config(config_path)
    headers = ["Outgoing", "Credit", "Date", "Description", "debit"]
    result = resolve_headers(headers, source_file="special_statement.pdf", config=cfg)
    # precedence: file override for Outgoing
    assert result["Outgoing"] == "amount_out"
    # synonyms mapping for Credit -> amount_in
    assert result["Credit"] == "amount_in"
    # rule mapping for Date / Description
    assert result["Date"] == "transaction_date"
    assert result["Description"] == "description"
    # synonym lower-case match
    assert result["debit"] == "amount_out"


def test_header_resolution_no_match_returns_none(tmp_path: Path):
    config_path = write_yaml(tmp_path)
    cfg = load_mapping_config(config_path)
    headers = ["Unrelated"]
    result = resolve_headers(headers, source_file="other.pdf", config=cfg)
    assert result["Unrelated"] is None
