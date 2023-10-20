# Generate Avery L7871 Stickers

This script reads sample names from a txt file (one name per line) and arranges them on a sheet of A4 paper so that they can be printed on **Avery-Zweckform L7871** labels. This version of the script is written in Python and is conceptually based on v1, which was written in bash.

## Requirements

- This script was developed primarily for a UNIX type **command-line interface** (e.g. Terminal on macOS), but it should also work on Windows
- **Python 3.10** or higher (confirmed to work on 3.11, 3.12) with the following packages installed:
  - [Colorama](https://github.com/tartley/colorama)
- **LaTeX** (e.g. TeX Live/MacTeX for macOS or any other TeX distribution). If you are using a small TeX distribution such as BasicTeX, make sure you have the following packages installed:
  - booktabs
  - datetime2
  - moresize

## How to use (UNIX)

1. Open your command-line interface of choice
2. Navigate to the folder that you want the output pdf to be in using the command `cd path/to/your/folder`
3. Run the script with `python3 generateStickers.py` (replace `generateStickers.py` with `path/to/script/generateStickers.py` if the script is not located in the same folder)
4. Follow the instructions that appear in the console.
