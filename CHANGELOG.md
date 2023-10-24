# Changelog

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
