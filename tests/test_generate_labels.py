import pytest
from generate_labels import generate_labels
from importlib import resources
from pathlib import Path


def create_testfile(tmp_path: Path, file: str = "test_small.txt") -> Path:
    """Copy test file from resources to temp directory"""

    dir_res = resources.files().joinpath("resources")
    dir_tmp = tmp_path
    file_in = dir_res.joinpath(file)
    file_out = dir_tmp.joinpath(file)

    file_out.write_text(file_in.read_text())

    return file_out


def test_generate_labels_small(tmp_path):
    file_input = str(create_testfile(tmp_path=tmp_path))
    test_args = ["-f", file_input]
    generate_labels.main(test_args)


def test_generate_labels_full(tmp_path):
    file_input = str(create_testfile(tmp_path=tmp_path, file="test_full.txt"))
    test_args = ["-f", file_input, "-n"]
    generate_labels.main(test_args)


def test_generate_labels_output(tmp_path):
    file_input = str(create_testfile(tmp_path=tmp_path))
    file_output = str(tmp_path.joinpath("file_output.txt"))
    test_args = ["-f", file_input, "-o", file_output, "-n"]
    generate_labels.main(test_args)


def test_generate_labels_date(tmp_path):
    file_input = str(create_testfile(tmp_path=tmp_path))
    test_args = ["-f", file_input, "-d", "1970-01-01", "-n"]
    generate_labels.main(test_args)


@pytest.mark.parametrize("skip", ["0", "42", "188", "377"])
def test_generate_labels_skip(tmp_path, skip: str):
    file_input = str(create_testfile(tmp_path=tmp_path))
    test_args = ["-f", file_input, "-s", skip, "-n"]
    generate_labels.main(test_args)
