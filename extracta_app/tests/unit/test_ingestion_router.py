import pytest

try:
    from src.ingestion.router import detect_file_type  # type: ignore
except ImportError:
    detect_file_type = None  # type: ignore


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("statement.pdf", "pdf"),
        ("receipt.PNG", "image"),
        ("photo.JpG", "image"),
    ],
)
def test_detect_file_type_supported(filename, expected):
    assert detect_file_type is not None, "detect_file_type not implemented (Task 18 pending)"
    assert detect_file_type(filename) == expected


@pytest.mark.parametrize("filename", ["notes.txt", "archive.zip", "data.csv"])
def test_detect_file_type_unsupported(filename):
    assert detect_file_type is not None, "detect_file_type not implemented (Task 18 pending)"
    with pytest.raises(ValueError):
        detect_file_type(filename)
