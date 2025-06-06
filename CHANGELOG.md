# Changelog

## v3.0.0

- Convert generateStickers into the `generate-labels` package
- Add `-n` / `--no-open` flag to prevent the resulting PDF being opened
- Typography
  - Change font to Computer Modern Unicode Sans Serif Bold to increase the number of available glyphs
  - Increase font size and adapt spacing to accomodate increased line height
- Improve consistency and reliability of sticker layout
- Improvements to handling of file system paths
  - Allow use to supply a path through the `--output-file` flag
  - All files generated by running `xelatex` are now placed in the same directory as the output file, not the current working directory
  - Work with absolute paths internally
- Merge `before_body.tex` into `preamble.tex`
- Use astral-sh/ruff-action@v3 action to run `ruff check`
- Implement some unit testing
- Refactor code and improve documentation

## v2.6.0

- Process date in Python instead of TeX. This removes the requirement fo the datetime2 package
- Improve printing of sample names to command line (fixes #16)
- Prevent skipped stickers collapsing into a single line
- Prevent an empty page at the end of the document in case stickers exactly fill up one or multiple pages

## v2.5.0

- Use xelatex executable instead of pdflatex
- Let locale dictate input encoding (usually UTF-8 on Unix, ANSI on Windows)
- Refactor code
- Bump minimum Python version to 3.11 (from 3.10)

## v2.4.0

- Add command line arguments allowing to run generateStickers in non-interactively
  A warning message has also been added when running the script without any arguments
- Check if LaTeX is installed and available. Exit script if this is not the case
- Open PDF using platform-specific command
- Use [Colorama](https://github.com/tartley/colorama) for cross-platform text formatting
- Warn user if overly long sample names are used

## v2.3.2

- Fix ANSI text formatting not working on Windows

## v2.3.1

- Bug fix: Update number of stickers to print after skipping stickers
- Minor code and comment refactoring

## v2.3

- Allow user to print empty stickers at the beginning of the sheets. This is useful if a number of stickers from a sheet have already been used
- Change how user is queried for date printing: By default today's date is printed in iso format (yyyy-mm-dd). No date or custom dates (directly put in by the user) are also possible
- Introduced sensible default options for all choices the user has to make. This makes it possible to simply press `[ENTER]` on each query, speeding up the process of typesetting a sticker sheet
- Print empty sticker if index is out of bound. This ensures that table rows are filled up and fixes a bug that occured when the number of stickers was not a multiple of 7
- Moved bigger chunks of LaTeX into their own files located in the `resources` folder
- Fix bug which caused empty lines in the sample names file to crash the script
- Escape a bigger set of special characters in LaTeX output. Function adapted from <https://stackoverflow.com/a/25875504>
- Allow reading lines from file with non-unicode encoding
- Did some code refactoring and cleaning

## v2.2

- Fixed an issue where sample names longer than 20 characters would break the layout
- Made further changes to case handling of user input and fixed samples names as well as file names being converted to lower case
- If user does not want to include the date on the sticker, they are not asked further questions about date formatting anymore

## v2.1

- Changed location of input file deletion command as it lead to its unwanted loss under certain circumstances and moved definition of file path to accommodate that change
- Added logic to put date on new line if sticker name is short and moved special character escape after string length is used for formatting
- Removed a couple of newline characters from output to make it more compact
- Changed case handling of user input
- LaTeX formatting: Took `\DATE` command out of `\mbox` as it was unnecessary and lead to extra whitespaces under certain circumstances
- LaTeX formatting: switched to `\par` from `\newline` to avoid horizontal space added by the latter command
- expanded How To Use section, added changelog and some other small changes to README
- Added .DS_Store file to gitignore

## v2.0

- initial release of the completely rewritten Python version (v1.X was written in Bash)
