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
    # create class with objects to format console output
    # https://stackoverflow.com/a/287944
    class color:
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

    #######################################################################
    # set up and check environment
    #######################################################################

    # make sure LaTeX is installed
    exec_latex = "xelatex"
    if shutil.which(exec_latex) is None:
        sys.exit(f"{exec_latex} was not found. Please install LaTeX")

    # fix ANSI text formatting on Windows
    just_fix_windows_console()

    #######################################################################
    # parse command line arguments
    #######################################################################

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

    # print warning about command-line arguments if none are set
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

    #######################################################################
    # initial sample name input
    #######################################################################

    retry = "no"

    # keep asking for file names until file exists or user aborts script
    while True:
        # check if input file has been set through cmd line args
        if args.input_file is None or retry == "yes":
            # get input file name from user and store its name in variable
            input_file = input(
                f"{color.BOLD + color.DARKCYAN}"
                "Enter the name of the txt file containing your strain/isolate "
                "names (one per line) followed by [ENTER] to "
                f"confirm: {color.END}"
            )
        else:
            input_file = args.input_file

        # check if user input includes ".txt" suffix and add it if absent
        if not input_file.endswith(".txt"):
            input_file += ".txt"

        # if file does not exist, print error message and exit script
        if not Path(input_file).exists():
            print(
                f"\n{color.BOLD + color.RED}File {input_file} not found. "
                "Make sure file is present in your working directory:\n"
                f"{Path().cwd()}\nTo change your working directory type "
                '"cd /Path/to/your/directory" then hit [ENTER]'
                f"{color.END}"
            )

            # if in interactive mode, ask user whether they want to type
            # the file name again
            if args.interactive:
                retry = input(
                    f"{color.BOLD + color.DARKCYAN}"
                    "Do you want to type the file name again? "
                    f'Type "yes" (default) or "no": \n{color.END}'
                )
                retry = retry.casefold()

                # if user wants to try again restart loop otherwise exit
                if retry == "yes" or not retry:
                    continue
                else:
                    sys.exit()
            else:
                sys.exit()

        else:
            break

    # read lines from file, filter out empty ones and convert to list
    with open(input_file, "r") as file:
        names_list = list(filter(None, (line.rstrip() for line in file)))

    names_number = len(names_list)

    # print some of the sample names
    print(
        f"\n{color.BOLD + color.DARKCYAN}"
        f"Your file contains {names_number} names:\n"
        f"{print_samples(names_list, names_number)}"
        f"{color.END}"
    )

    # set output file name to input file name
    name_output = input_file

    # set name of output file depending on command line arguments
    if args.output_file is None:
        if args.interactive:
            # ask user whether they want to continue with the sample names
            input_continue = input(
                f"{color.BOLD + color.DARKCYAN}Do you want to continue with these "
                'names? Type "yes" (default) or "no": '
                f"{color.END}"
            )
            input_continue = input_continue.casefold()

            # exit script if user says no, otherwise continue
            if input_continue == "no":
                sys.exit()

            # query user on output file name
            name_output = input(
                f"\n{color.BOLD + color.DARKCYAN}Type the name of your output "
                'file without suffix (e.g. "file" instead of "file.txt"). '
                "Press [ENTER] to use the name of the input file (default): "
                f"{color.END}"
            )

            # deal with empty answer
            if not name_output:
                name_output = input_file
        else:
            name_output = input_file
    else:
        name_output = args.output_file

    # set output file path
    path_output = Path(str(Path().absolute()) + "/" + name_output)

    #######################################################################
    # construct sample names using suffixes
    #######################################################################

    if args.add_suffixes:
        input_suffix = True
    else:
        if args.interactive:
            # give user choice whether to add suffixes
            input_suffix = input(
                f"\n{color.BOLD + color.DARKCYAN}"
                "Do you want to add suffixes to your sample names? "
                f'Type "yes" or "no" (default): {color.END}'
            ).casefold()
        else:
            input_suffix = False

    if input_suffix is True or input_suffix == "yes":
        # print explanation of inner workings once before continuing
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

        # initiate list with names to be modified
        names_list_new = []
        names_list_old = names_list

        # keep asking for suffixes and adding them to sample names
        # until user stops loop.
        while True:
            # ask for group of suffixes
            input_suffix_group = input(
                f"{color.BOLD + color.DARKCYAN}\nEnter a group of suffixes: {color.END}"
            )

            # exit suffixing logic if not suffixes provided
            if not input_suffix_group:
                print(f"\n{color.BOLD + color.RED}No suffix group entered.{color.END}")
            else:
                # split input into list of words
                input_suffixes = input_suffix_group.split()

                # reinitiate list so it is empty
                names_list_new = []

                # loop through all names and add each suffix
                for name in names_list_old:
                    for suffix in input_suffixes:
                        names_list_new.append(f"{name}-{suffix}")

                # replace old with new list
                names_list_old = names_list_new

            # ask user whether to run through another interation of the
            # suffix loop
            input_suffix_continue = input(
                f"\n{color.BOLD + color.DARKCYAN}"
                "Do you want to add another group of suffixes? "
                f'Type "yes" or "no" (default): {color.END}'
            ).casefold()

            # if user answers anything other than yes break out of loop,
            # otherwise repeat
            if input_suffix_continue != "yes":
                break
            else:
                continue

        # set path to which file with suffixed sample names will be written
        path_suffix = Path(
            f"{str(path_output.parent)}/{path_output.stem}_suffix{path_output.suffix}"
        )

        # remove old output file and ignore error if it does not exist
        try:
            path_suffix.unlink()
        except FileNotFoundError:
            pass

        # replace original list of names with suffixed names
        try:
            # write new sample names to new output file
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

    #######################################################################
    # customization of output
    #######################################################################

    # set number of skipped stickers depending on combination of args
    if args.skip is None:
        if args.interactive:
            # ask user how many stickers they want to skip (default: 0)
            input_skip = input(
                f"\n{color.BOLD + color.DARKCYAN}"
                f"How many stickers do you want to skip, e.g. because they were "
                f"already used before (default = 0): {color.END}"
            ).casefold()

            # deal with empty or non-numeric answers
            if not input_skip:
                input_skip = 0
            else:
                input_skip = int(input_skip)
        else:
            input_skip = 0
    else:
        input_skip = args.skip

    # prepend empty items to list of names for each sticker to skip
    names_list = ([None] * input_skip) + names_list
    names_number = len(names_list)

    # set date depending on combination of args
    if args.date is None:
        if args.interactive:
            # give user choice whether to print date and in which format
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

    # set str_date variable depending on user's date choice
    match input_date:
        case "today":
            str_date = date.today().isoformat()
        case "none":
            str_date = "\\phantom{empty date}"
        case _:
            str_date = input_date

    #######################################################################
    # typeset LaTeX file
    #######################################################################

    # set paths to typesetting and output files
    dir_resources = resources.files().joinpath("resources")
    path_preamble = dir_resources.joinpath("preamble.tex")
    path_latex = path_output.with_suffix(".tex")

    # remove old output file if one already exist
    try:
        path_latex.unlink()
    except FileNotFoundError:
        pass

    # calculate number of pages necessary to fit all stickers
    # (including skipped ones)
    latex_pages = names_number // 189
    # add page for remaining stickers
    if names_number % 189 > 0:
        latex_pages = latex_pages + 1

    # check if any sample names are above the maximum recommended length
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

    # create .tex file and write to it
    with open(path_latex, "a+") as file_output:
        # write contents of preamble file to output file
        with open(path_preamble, "r") as file_preamble:
            for line in file_preamble:
                file_output.write(line)
            file_output.write("\n")

        # variable to track the current position in the list of names
        n = 0

        # loop through pages of final sticker layout
        for page_number in range(latex_pages):
            # start each page with the opening of the table environment
            file_output.write(
                f"% Page {page_number + 1}\n"
                "\\begin{tabularhtx}{\\textheight}{\\linewidth}{@{}*{7}{Y}@{}}\n"
            )

            # loop through all rows
            for line_number in range(27):
                # add tab character at beginning of line
                file_output.write("\t")
                # loop through columns
                for position in range(7):
                    # print unprinted sample names
                    if position < 6:
                        file_output.write(
                            f"{return_sticker(n, names_list, str_date)} & "
                        )
                    elif position == 6:
                        file_output.write(f"{return_sticker(n, names_list, str_date)}")
                    else:
                        break
                    n += 1
                # add whitespace between rows
                if line_number == 26:
                    file_output.write(" \\\\ \\interrowspace{-1em}\n")
                else:
                    # maximum allowable space determined by trial and error
                    file_output.write(" \\\\ \\interrowfill\n")
            # close table environment at the end of the page
            file_output.write("\\end{tabularhtx}\n\n")
        # reenable command line output and end document
        file_output.write("\\scrollmode\n\\end{document}")

    # call LaTeX executable to typeset .tex file
    subprocess.run([exec_latex, path_latex], stdout=subprocess.DEVNULL)

    # open resulting pdf file in an OS-dependent manner
    if system() == "Darwin":
        subprocess.run(["open", path_latex.with_suffix(".pdf")])
    elif system() == "Windows":
        os.startfile(path_latex.with_suffix(".pdf"))  # type: ignore
    else:
        subprocess.run(["xdg-open", path_latex.with_suffix(".pdf")])


# function that returns sticker content
def return_sticker(x, names_list, str_date):
    # return empty sticker
    if x >= len(names_list) or names_list[x] is None:
        sticker = "\\phantom{empty}\\par\\phantom{sticker}"
    else:
        sticker = tex_escape(names_list[x])
        # set smaller font size depending on sticker text length
        if str_width(sticker) >= 139:
            sticker = f"{{\\tiny {sticker} }}"
        elif str_width(sticker) >= 104:
            sticker = f"{{\\ssmall {sticker} }}"
        elif str_width(sticker) >= 88:
            sticker = f"{{\\scriptsize {sticker} }}"

        # if sticker is long let latex do the word splitting,
        # otherwise put date on new line
        if len(sticker) > 30:
            sticker = f"{sticker} {str_date}"
        else:
            sticker = f"{sticker} \\par {str_date}"
    return sticker


# function to escape characters for LaTeX output
# https://stackoverflow.com/a/25875504
def tex_escape(text):
    """
    :param text: a plain text message
    :return: the message escaped to appear correctly in LaTeX
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


# print some of the sample names
def print_samples(names_list, names_number):
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


def str_width(string: str, size: int = 10) -> float:
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
