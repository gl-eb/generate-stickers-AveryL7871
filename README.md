# generate-stickers-AveryL7871

This script reads sample names from a txt file (one name per line) and arranges them on a sheet of A4 paper so that they can be printed on Avery-Zweckform L7871 labels. The current version of the script is written in Python and is conceptually based on v1, which was written in bash.

## Requirements
- A UNIX type console (e.g. Terminal on macOS)
- Python 3.5 or higher (e.g. Python 3.9.1 from https://www.python.org/downloads/mac-osx/ or Python 3.8.5 as it comes with the latest Anaconda release https://www.anaconda.com/products/individual)
- LaTeX (e.g. TeX Live/MacTeX for macOS or any other TeX distribution, https://tug.org/mactex/)

## How to use
1. Put the script (generateStickers.py) in the folder that you want the output pdf to be in.
2. Navigate to this folder using the command line: cd path/to/your/folder
3. Run the script with: python3 generateStickers.py
4. Follow the instructions that appear in the console.
