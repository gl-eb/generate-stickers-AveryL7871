# Generate Avery L7871 Stickers

This script reads sample names from a txt file (one name per line) and arranges them on a sheet of A4 paper so that they can be printed on **Avery-Zweckform L7871** labels. This version of the script is written in Python and is conceptually based on v1, which was written in bash.

## Requirements
- A UNIX type **command-line interface** (e.g. Terminal on macOS)
- **Python 3.5** or higher (confirmed to work on 3.8.5 and 3.9+)
- **LaTeX** (e.g. TeX Live/MacTeX for macOS or any other TeX distribution)\
  if you are using a small TeX distribution such as BasicTeX, make sure you have the following packages installed:
    - tabularx
    - booktabs
    - datetime2
    - moresize

## How to use
1. Open your command-line interface of choice
2. Navigate to the folder that you want the output pdf to be in using the command `cd path/to/your/folder`
3. Run the script with `python3 generateStickers.py`\
(replace `generateStickers.py` with `path/to/script/generateStickers.py` if the script is not located in the same folder)
4. Follow the instructions that appear in the console.

## Changelog
### v2.1 (2021-03-08)
- Changed location of input file deletion command as it lead to its unwanted loss under certain circumstances and moved definition of file path to accommodate that change
- Added logic to put date on new line if sticker name is short and moved special character escape after string length is used for formatting
- Removed a couple of newline characters from output to make it more compact
- Changed case handling of user input
- LaTeX formatting: Took `\DATE` command out of `\mbox` as it was unnecessary and lead to extra whitespaces under certain circumstances
- LaTeX formatting: switched to `\par` from `\newline` to avoid horizontal space added by the latter command
- Added .DS_Store file to gitignore

### v2.0 (2021-02-24)
- initial release of the completely rewritten Python version (v1.X was written in Bash)
