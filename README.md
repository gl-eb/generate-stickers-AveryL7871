# Generate Avery L7871 Stickers

This script reads sample names from a txt file (one name per line) and arranges them on a sheet of A4 paper so that they can be printed on **Avery-Zweckform L7871** labels. This version of the script is written in Python and is conceptually based on v1, which was written in bash.

## Requirements

- This script was developed primarily for a UNIX type **command-line interface** (e.g. Terminal on macOS), but it should also work on Windows
- **Python 3.11** or higher (also confirmed to work on 3.12 and 3.13) with the following packages installed:
  - [Colorama](https://github.com/tartley/colorama)
- **LaTeX** (e.g. TeX Live/MacTeX for macOS or any other TeX distribution). If you are using a small TeX distribution such as BasicTeX, make sure you have the following packages installed:
  - booktabs
  - datetime2
  - moresize
- You will need a **plain text file** (with the `.txt` suffix), ideally UTF-8 encoded, containing one sample name per line.
  Sample names should ideally be 30 characters long at most.
  Longer names could mess up the layout and prevent proper printing on the sticker sheet

## User Guide (UNIX)

Download this repository either using the GitHub interface (click the green `<> Code` button and then `Download ZIP`) or `git clone`

```bash
git clone https://github.com/gl-eb/generate-stickers-AveryL7871
```

Open your command-line interface of choice and navigate to the folder that contains your input file.
The pdf file generated by this script will be placed in the same folder

```bash
cd path/to/your/folder
```

Run the script using python with any of the command-line options listed below.
Replace `generateStickers.py` with `path/to/script/generateStickers.py` if the script is not located in the same folder

```bash
python generateStickers.py
```

### Aliases

You can also create an alias for generateStickers in your shell.
If you are using bash, add it to the `~/.bashrc` file in your home directory.
The equivalent file for zsh is `~/.zshrc`.
The following alias will change the current directory to one where you want your sticker files to live and then calls generateStickers from a subdirectory.

```bash
alias avery='cd ~/path/to/input_output_directory/ && python ./generate-stickers-AveryL7871/generateStickers.py'
```

You can even use the alias in combination with command-line options

```bash
avery -i
```

### Without Command-Line Options

Executing generateStickers without any command-line options will ask the user to interactively provide the minimum set of options necessary.
Currently this is just the input file (`-f / --input-file`).
The default values will be used for the remaining options

```bash
python generateStickers.py
```

### Command-Line Options Only

If generateStickers is called and the path to a input file (`-f / --input-file`) is provided, the script runs without needing any input from the user.
Again, default values will be used for any unspecified options

```bash
python generateStickers.py -f <path/to/input_file>
```

```bash
python generateStickers.py -f <path/to/input_file> -o <path/to/output_file> -s 20 -d "July 1st 2023"
```

### Interactive Mode

In interactive mode (`-i / --interactive`) the user will be asked to provide any option that has not been set in the command line

```bash
python generateStickers.py -i
```

```bash
python generateStickers.py -i -f <path/to/input_file> -d none
```

### Suffixing Sample Names

Adding suffixes to sample names (e.g. appending the name of an experimental treatment) can currently only be done interactively.
One use case for suffixing is a set of microbial strains of cell lines that went through multiple treatment arms of an experiment in multiple replicates:

- Say you have three strains: Strain1, Strain2, Strain3
- The first suffix group could then be the treatment: Control, Treatment1, Treatment2
- Numbered replicate lines would be suffix group number two: 1, 2, 3

The resulting stickers would then be `Strain1-Control-1, Strain1-Control-2, Strain1-Control-3, Strain1-Treatment1-1, ... , Strain3-Treatment2-3`.
Please keep in mind that adding suffixes can push sample names above the recomended limit of 30 characters.
Check the resulting PDF carefully before printing

```bash
python generateStickers.py -f <path/to/input_file> -a
```

### Command-Line Options

```
> python generateStickers.py -h
usage: generateStickers.py [-h] [-i] [-f FILE] [-o FILE] [-a] [-s INT] [-d STR]

options:
  -h, --help            show this help message and exit
  -i, --interactive     run generateStickers in interactive mode, requiring user input for any unset arguments
  -f FILE, --input-file FILE
                        the text file containing one sample name per line
  -o FILE, --output-file FILE
                        the name of the output file (default: same as input file)
  -a, --add-suffixes    interactively add suffixes to sample names
  -s INT, --skip INT    number of stickers to skip (default: 0)
  -d STR, --date STR    "today", "none", or a custom date string(default: "today")
```
