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
