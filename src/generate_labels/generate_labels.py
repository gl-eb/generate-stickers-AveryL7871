"""Generate printable label layout from the command line

This package reads sample names from a file and arranges them on a sheet
of A4 paper for printing on Avery-Zweckform L7871 labels.

```
generate-labels -f sample_names.txt
```
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from importlib import resources
from pathlib import Path
from platform import system

from colorama import just_fix_windows_console


def main():
    """Generate printable label layout"""

    class color:
        """Objects used to format console output.

        https://stackoverflow.com/a/287944
        """

        PURPLE = "\033[95m"
        CYAN = "\033[96m"
        DARKCYAN = "\033[36m"
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"
        END = "\033[0m"

    ### Set up and check environment ######################################

    # Make sure LaTeX is installed
    EXEC_LATEX = "xelatex"
    if shutil.which(EXEC_LATEX) is None:
        sys.exit(f"{EXEC_LATEX} was not found. Please install LaTeX")

    # Fix ANSI text formatting on Windows
    just_fix_windows_console()

    ### Parse command line arguments ######################################

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--interactive",
        help="run generate-labels in interactive mode, requiring user input for "
        "any unset arguments",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--input-file",
        metavar="FILE",
        help="the text file containing one sample name per line",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        metavar="FILE",
        help="the name of the output file (default: same as input file)",
    )
    parser.add_argument(
        "-a",
        "--add-suffixes",
        help="interactively add suffixes to sample names",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--skip",
        type=int,
        metavar="INT",
        help="number of stickers to skip (default: 0)",
    )
    parser.add_argument(
        "-d",
        "--date",
        metavar="STR",
        help='"today", "none", or a custom date string (default: "today")',
    )
    args = parser.parse_args()

    # Print warning about command-line arguments if none are set
    if args.input_file is None and not args.interactive:
        print(
            f"{color.BOLD + color.YELLOW}"
            "As of version 2.4.0 generate-labels supports command-line "
            "arguments. Please run the script with the following command for a "
            "fully interactive experience:"
            "\n\ngenerate-labels --interactive"
            "\n\nMore information can be found at "
            "https://github.com/gl-eb/generate-stickers-AveryL7871 or by running"
            "\n\ngenerate-labels --help"
            f"{color.END}\n"
        )

    ### Initial sample name input #########################################

    retry = "no"

    # Keep asking for file names until file exists or user aborts script
    while True:
        # Check if input file has been set through cmd line args
        if args.input_file is None or retry == "yes":
            # Get input file name from user and store its name in variable
            input_file = input(
                f"{color.BOLD + color.DARKCYAN}"
                "Enter the name of the txt file containing your strain/isolate "
                "names (one per line) followed by [ENTER] to "
                f"confirm: {color.END}"
            )
        else:
            input_file = args.input_file

        # Check if user input includes ".txt" suffix and add it if absent
        if not input_file.endswith(".txt"):
            input_file += ".txt"

        # If file does not exist, print error message and exit script
        if not Path(input_file).exists():
            print(
                f"\n{color.BOLD + color.RED}File {input_file} not found. "
                "Make sure file is present in your working directory:\n"
                f"{Path().cwd()}\nTo change your working directory type "
                '"cd /Path/to/your/directory" then hit [ENTER]'
                f"{color.END}"
            )

            # If in interactive mode, ask user whether they want to try again
            if args.interactive:
                retry = input(
                    f"{color.BOLD + color.DARKCYAN}"
                    "Do you want to type the file name again? "
                    f'Type "yes" (default) or "no": \n{color.END}'
                )
                retry = retry.casefold()

                # If user wants to try again, restart loop, otherwise exit
                if retry == "yes" or not retry:
                    continue
                else:
                    sys.exit()
            else:
                sys.exit()

        else:
            break

    # Read lines from file, filter out empty ones and convert to list
    with open(input_file, "r") as file:
        names_list = list(filter(None, (line.rstrip() for line in file)))

    names_number = len(names_list)

    # Print some of the sample names
    print(
        f"\n{color.BOLD + color.DARKCYAN}"
        f"Your file contains {names_number} names:\n"
        f"{_print_samples(names_list, names_number)}"
        f"{color.END}"
    )

    name_output = input_file

    # Set name of output file depending on command line arguments
    if args.output_file is None:
        if args.interactive:
            # Ask user whether they want to continue with the sample names
            input_continue = input(
                f"{color.BOLD + color.DARKCYAN}Do you want to continue with these "
                'names? Type "yes" (default) or "no": '
                f"{color.END}"
            )
            input_continue = input_continue.casefold()

            # Exit script if user says no, otherwise continue
            if input_continue == "no":
                sys.exit()

            # Ask user for output file name
            name_output = input(
                f"\n{color.BOLD + color.DARKCYAN}Type the name of your output "
                'file without suffix (e.g. "file" instead of "file.txt"). '
                "Press [ENTER] to use the name of the input file (default): "
                f"{color.END}"
            )

            if not name_output:
                name_output = input_file
        else:
            name_output = input_file
    else:
        name_output = args.output_file

    # Set output file path to current folder
    path_output = Path(str(Path().absolute()) + "/" + name_output)

    ### Construct sample names using suffixes #############################

    if args.add_suffixes:
        input_suffix = True
    else:
        if args.interactive:
            # Ask user whether to add suffixes
            input_suffix = input(
                f"\n{color.BOLD + color.DARKCYAN}"
                "Do you want to add suffixes to your sample names? "
                f'Type "yes" or "no" (default): {color.END}'
            ).casefold()
        else:
            input_suffix = False

    if input_suffix is True or input_suffix == "yes":
        # Print explanation of how suffix addition works
        print(
            f"\n{color.BOLD + color.DARKCYAN}=========================================="
        )
        print(
            "\nIn the following part of the script you will supply groups of "
            "suffixes (e.g. treatment names or replicate numbers) separated by "
            'spaces: "CTRL TREAT1 TREAT2 TREAT3". Each suffix will be combined '
            "with each sample name (e.g. Strain1-TREAT1, Strain1-TREAT2 ... "
            "Strain10-TREAT3). You will also have the opportunity to supply "
            "multiple suffix groups one after the other (the result of this would "
            "be something like Strain1-TREAT1-Replicate1, "
            f"Strain1-TREAT1-Replicate2 ...).{color.END}"
        )

        # Initiate list with names to be modified
        names_list_new = []
        names_list_old = names_list

        # Keep asking for suffixes until user stops loop.
        while True:
            # Ask for group of suffixes
            input_suffix_group = input(
                f"{color.BOLD + color.DARKCYAN}\nEnter a group of suffixes: {color.END}"
            )

            # Exit suffixing logic if no suffixes provided
            if not input_suffix_group:
                print(f"\n{color.BOLD + color.RED}No suffix group entered.{color.END}")
            else:
                # Split input into list of words
                input_suffixes = input_suffix_group.split()

                names_list_new = []

                # Loop through names and add suffixe
                for name in names_list_old:
                    for suffix in input_suffixes:
                        names_list_new.append(f"{name}-{suffix}")

                names_list_old = names_list_new

            # Ask user whether to add another level of suffixes
            input_suffix_continue = input(
                f"\n{color.BOLD + color.DARKCYAN}"
                "Do you want to add another group of suffixes? "
                f'Type "yes" or "no" (default): {color.END}'
            ).casefold()

            # Break out of loop if user answers anything other than "yes"
            if input_suffix_continue != "yes":
                break
            else:
                continue

        # Set path to which txt file with suffixed sample names will be written
        path_suffix = Path(
            f"{str(path_output.parent)}/{path_output.stem}_suffix{path_output.suffix}"
        )

        # Remove old output file if it exists
        try:
            path_suffix.unlink()
        except FileNotFoundError:
            pass

        # Replace original list of sample names with suffixed names
        try:
            # Write new sample names to new output file
            with open(path_suffix, "a+") as file_samples:
                for item in names_list_new:
                    file_samples.write(f"{item}\n")

            names_list = names_list_new
        except NameError:
            print(
                f"\n{color.BOLD + color.RED}"
                "No suffixes entered. Skipping addition of suffixes"
                f"{color.END}"
            )

    ### Customise printable layout ########################################

    # Set number of skipped stickers depending on combination of arguments
    if args.skip is None:
        if args.interactive:
            # Ask user how many stickers they want to skip (default: 0)
            input_skip = input(
                f"\n{color.BOLD + color.DARKCYAN}"
                f"How many stickers do you want to skip, e.g. because they were "
                f"already used before (default = 0): {color.END}"
            ).casefold()

            # Deal with empty or non-numeric answers
            if not input_skip:
                input_skip = 0
            else:
                input_skip = int(input_skip)
        else:
            input_skip = 0
    else:
        input_skip = args.skip

    # Prepend empty items to list of names for each sticker to skip
    names_list = ([None] * input_skip) + names_list
    names_number = len(names_list)

    # Set date depending on combination of args
    if args.date is None:
        if args.interactive:
            # Give user choice whether to print date and in which format
            print(
                f"""{color.BOLD + color.DARKCYAN}
                Do you want to print a date to the second sticker row?
                - For today\'s date in yyyy-mm-dd format (default),
                leave empty or enter \"today\"
                - Type \"none\" to not print anything to the date field
                - Any other input will be printed verbatim as the date,
                e.g. \"2023\""""
            )
            input_date = input(f"Your choice: {color.END}")
        else:
            input_date = "today"
    else:
        input_date = args.date

    # Set str_date variable depending on user's date choice
    match input_date:
        case "today":
            str_date = date.today().isoformat()
        case "none":
            str_date = "\\phantom{empty date}"
        case _:
            str_date = input_date

    ### Typeset TeX file ##################################################

    # set paths to typesetting and output files
    DIR_RESOURCES = resources.files().joinpath("resources")
    PATH_PREAMBLE = DIR_RESOURCES.joinpath("preamble.tex")
    PATH_LATEX = path_output.with_suffix(".tex")

    # Remove old output file if one already exist
    try:
        PATH_LATEX.unlink()
    except FileNotFoundError:
        pass

    # Calculate number of pages necessary to fit all stickers (including skipped ones)
    latex_pages = names_number // 189
    # Add page for remaining stickers
    if names_number % 189 > 0:
        latex_pages = latex_pages + 1

    # Check if any sample names are above the maximum recommended length
    overlength = False
    for name in names_list:
        if name is not None:
            if len(name) > 30:
                overlength = True

    if overlength:
        print(
            f"\n{color.BOLD + color.RED}"
            "Warning: Some of the sample names are overly long, which might "
            "disrupt the final layout. Please inspect the resulting PDF carefully "
            "before printing"
            f"{color.END}"
        )

    # Create TeX file and write to it
    with open(PATH_LATEX, "a+") as file_output:
        # Write contents of preamble file to output file
        with open(PATH_PREAMBLE, "r") as file_preamble:
            for line in file_preamble:
                file_output.write(line)
            file_output.write("\n")

        n = 0
        """Track current position in the list of names"""

        # Loop through pages of final sticker layout
        for page_number in range(latex_pages):
            # Start each page with the opening of the table environment
            file_output.write(
                f"% Page {page_number + 1}\n"
                "\\begin{tabularhtx}{\\textheight}{\\linewidth}{@{}*{7}{Y}@{}}\n"
            )

            # Loop through rows
            for line_number in range(27):
                # Add tab character at beginning of line to increase readability
                file_output.write("\t")
                # Loop through columns
                for position in range(7):
                    # Print unprinted sample names
                    if position < 6:
                        file_output.write(
                            f"{_return_sticker(n, names_list, str_date)} & "
                        )
                    elif position == 6:
                        file_output.write(f"{_return_sticker(n, names_list, str_date)}")
                    else:
                        break
                    n += 1
                # Add whitespace between rows
                if line_number == 26:
                    file_output.write(" \\\\ \\interrowspace{-1em}\n")
                else:
                    file_output.write(" \\\\ \\interrowfill\n")
            # Close table environment at the end of the page
            file_output.write("\\end{tabularhtx}\n\n")
        # Reenable command line output and end document
        file_output.write("\\scrollmode\n\\end{document}")

    # Call LaTeX executable to typeset .tex file
    subprocess.run([EXEC_LATEX, PATH_LATEX], stdout=subprocess.DEVNULL)

    # Open resulting PDF in an OS-dependent manner
    if system() == "Darwin":
        subprocess.run(["open", PATH_LATEX.with_suffix(".pdf")])
    elif system() == "Windows":
        os.startfile(PATH_LATEX.with_suffix(".pdf"))  # type: ignore
    else:
        subprocess.run(["xdg-open", PATH_LATEX.with_suffix(".pdf")])


def _return_sticker(x: int, names_list: list, str_date: str) -> str:
    """
    Return sticker content

    Parameters
    ----------
    x: int
        Index of sticker to print
    names_list: list
        List of sticker contents
    str_dat: str
        Date to print on sticker

    Returns
    -------
    str
        Sticker contents written in TeX
    """

    if x >= len(names_list) or names_list[x] is None:
        # Return empty sticker
        sticker = "\\phantom{empty}\\par\\phantom{sticker}"
    else:
        sticker = _tex_escape(names_list[x])
        # Set smaller font size depending on sticker text length
        width_sticker = _str_width(sticker)
        if width_sticker >= 139:
            sticker = f"{{\\tiny {sticker} }}"
        elif width_sticker >= 104:
            sticker = f"{{\\ssmall {sticker} }}"
        elif width_sticker >= 88:
            sticker = f"{{\\scriptsize {sticker} }}"

        # If sticker is long, let TeX do the word splitting,
        # otherwise put date on new line
        if len(sticker) > 30:
            sticker = f"{sticker} {str_date}"
        else:
            sticker = f"{sticker} \\par {str_date}"
    return sticker


def _tex_escape(text: str) -> str:
    """
    Escape characters for TeX output

    https://stackoverflow.com/a/25875504

    Parameters
    ----------
    text: str
        Text to process for escapable characters

    Returns
    -------
    str
        Text escaped to appear correctly in TeX
    """

    conv = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\^{}",
        "\\": r"\textbackslash{}",
        "<": r"\textless{}",
        ">": r"\textgreater{}",
    }
    regex = re.compile(
        "|".join(
            re.escape(str(key))
            for key in sorted(conv.keys(), key=lambda item: -len(item))
        )
    )
    return regex.sub(lambda match: conv[match.group()], text)


def _print_samples(names_list: list, names_number: int) -> str:
    """
    Print up to three sample names for quality control

    Parameters
    ----------
    names_list: list
        List of sample names found in input file
    names_number: int
        Number of sample names found in input file

    Returns
    -------
    str
        Message that can be printed to the command line
    """

    message = f"{names_list[0]}"
    if names_number > 1:
        message = f"{message}, {names_list[1]}"
    if names_number > 3:
        message = f"{message} ... "
    elif names_number == 3:
        message = f"{message}, "
    if names_number > 2:
        message = f"{message}{names_list[-1]}"
    return message


def _str_width(string: str, size: int = 10) -> float:
    """
    Calculate width of string in Computer Modern Unicode Sans Serif Bold

    https://stackoverflow.com/a/77351575

    Parameters
    ----------
    string: str
        String to be measured
    size: int
        Font size in pts of string (default: 10)

    Returns
    -------
    float
        Width of string in pts
    """

    # fmt: off
    WIDTH_DICT={
        '0': 55, '1': 55, '2': 55, '3': 55, '4': 55, '5': 55, '6': 55, '7': 55,
        '8': 55, '9': 55, 'a': 53, 'b': 56, 'c': 49, 'd': 56, 'e': 51, 'f': 39,
        'g': 55, 'h': 56, 'i': 26, 'j': 36, 'k': 53, 'l': 26, 'm': 87, 'n': 56,
        'o': 55, 'p': 56, 'q': 56, 'r': 37, 's': 42, 't': 40, 'u': 56, 'v': 50,
        'w': 74, 'x': 50, 'y': 50, 'z': 48, 'A': 73, 'B': 73, 'C': 70, 'D': 79,
        'E': 64, 'F': 61, 'G': 73, 'H': 79, 'I': 33, 'J': 52, 'K': 76, 'L': 58,
        'M': 98, 'N': 79, 'O': 79, 'P': 70, 'Q': 79, 'R': 70, 'S': 61, 'T': 73,
        'U': 76, 'V': 73, 'W': 104, 'X': 73, 'Y': 73, 'Z': 67, '!': 37, '"': 55,
        '#': 92, '$': 55, '%': 103, '&': 83, "'": 31, '(': 43, ')': 43, '*': 55,
        '+': 86, ',': 31, '-': 37, '.': 31, '/': 55, ':': 31, ';': 31, '<': 86,
        '=': 86, '>': 86, '?': 52, '@': 73, '[': 34, '\\': 55, ']': 34, '^': 67,
        '_': 86, '`': 55, '{': 55, '|': 31, '}': 55, '~': 67, ' ': 37
    }

    AVERAGE_WIDTH = 58.810526315789474

    width = sum(WIDTH_DICT.get(s, AVERAGE_WIDTH) for s in string) * (size / 100)

    return round(width)
