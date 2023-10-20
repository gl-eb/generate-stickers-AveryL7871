""" Version 2.3.2 (2023-10-20) by Gleb Ebert

    This script reads sample names from a list, presents the user with
    a couple of options to modify the names and arranges them on a
    sheet of A4 paper so that it can be printed on Avery-Zweckform
    L7871 labels
"""

from pathlib import Path, PurePath
from platform import system
import re
import shutil
import subprocess
import sys
import os


#######################################################################
# define functions and classes
#######################################################################

# function that returns sticker content
def return_sticker(x):
    # return empty sticker
    if (x >= len(names_list) or names_list[x] is None):
        sticker = "\\phantom{empty sticker}\\par"
    else:
        sticker = tex_escape(names_list[x])
        # reduce font size depending on how long text is
        if len(sticker) > 20:
            sticker = "{\\tiny " + sticker + "}"
        elif len(sticker) > 15:
            sticker = "{\\ssmall " + sticker + "}"
        if (input_date != "none"):
            # if sticker is long let latex do the word splitting
            if len(sticker) > 30:
                sticker = sticker + " \\DATE"
            else:
                sticker = sticker + "\\par\\DATE"
        else:
            # add newline to preserve table formatting w/o date
            if len(sticker) < 31:
                sticker = sticker + "\\par"
    return sticker

# function to escape characters for LaTeX output
# https://stackoverflow.com/a/25875504
def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile(
        '|'.join(re.escape(str(key)) for key in sorted(conv.keys(),
        key = lambda item: - len(item)))
    )
    return regex.sub(lambda match: conv[match.group()], text)

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

# make sure TeX is installed
if shutil.which("pdflatex") is None:
    sys.exit("pdflatex was not found. Please install LaTeX")

# fix ANSI colors on Windows: https://stackoverflow.com/a/54955094
os.system("")


#######################################################################
# initial sample name input
#######################################################################

# keep asking for file names until file exists or user aborts script
while True:
    # get input file name from user and store its name in variable
    input_file = input(f"{color.BOLD + color.DARKCYAN}"
        "Enter the name of the txt file containing your strain/isolate"
        " names (one per line) followed by [ENTER] to confirm: "
        f"{color.END}")

    # check if user input includes ".txt" suffix and add it if absent
    if not input_file.endswith(".txt"):
        input_file += ".txt"

    # if file does not exist, print error message and exit script
    if not Path(input_file).exists():
        print(f"\n{color.BOLD + color.RED}File {input_file} not found."
              " Make sure file is present in your working directory:\n"
              f"{Path().cwd()}\nTo change your working directory type "
              "'cd /Path/to/your/directory' then hit [ENTER]"
              f"{color.END}")

        # ask user whether they wants to type the file name again
        retry = input(f"{color.BOLD + color.DARKCYAN}"
            "Do you want to type the file name again? "
            f"Type \"yes\" (default) or \"no\": \n{color.END}")
        retry = retry.casefold()

        # if user wants to try again restart loop otherwise exit script
        if (retry == "yes" or not retry):
            continue
        else:
            quit()
    else:
        break

# read lines from file, filter out empty ones and convert to list
with open(input_file, "r", encoding='unicode_escape') as file:
    names_list = list(filter(None, (line.rstrip() for line in file)))

names_number = len(names_list)

# print some of the sample names
print(f"\n{color.BOLD + color.DARKCYAN}"
    f"Your file contains {names_number} names:\n"
    f"{names_list[0]}, {names_list[1]} ... "
    f"{names_list[-1]}{color.END}")

# ask user whether they want to continue with the sample names
input_continue = input(f"{color.BOLD + color.DARKCYAN}Do you want to "
    "continue with these names? Type \"yes\" (default) or \"no\": "
    f"{color.END}")
input_continue = input_continue.casefold()

# exit script if user says no, otherwise continue
if input_continue == "no":
    quit()

# query user on output file name
name_output = input(f"\n{color.BOLD + color.DARKCYAN}Type the name of "
    "your output file without suffix (e.g. \"file\" instead of "
    "\"file.txt\"). Press [ENTER] to use the name of the input file "
    f"(default): {color.END}")

# use input file name as output file name if user returned empty string
if not name_output:
    name_output = input_file

# set output file path
path_output = Path(str(Path().absolute()) + "/" + name_output)

#######################################################################
# construct sample names using suffixes
#######################################################################

# give user choice whether to add suffixes
input_suffix = input(f"\n{color.BOLD + color.DARKCYAN}"
    "Do you want to add suffixes to your sample names? "
    f"Type \"yes\" or \"no\" (default): {color.END}").casefold()

if input_suffix == "yes":
    # print explanation of inner workings once before continuing
    print(f"\n{color.BOLD + color.DARKCYAN}"
        "==========================================")
    print("\nIn the following part of the script you will supply "
    "groups of suffixes (e.g. treatment names or replicate numbers)"
    " separated by spaces: \"CTRL TREAT1 TREAT2 TREAT3\". Each suffix"
    " will be combined with each sample name (e.g. Strain1-TREAT1, "
    "Strain1-TREAT2 ... Strain10-TREAT3). You will also have the "
    "opportunity to supply multiple suffix groups one after the other "
    "(the result of this would be something like "
    "Strain1-TREAT1-Replicate1, Strain1-TREAT1-Replicate2 ...)."
    "{color.END}")

    # initiate list with names to be modified
    names_list_old = names_list

    # keep asking for suffixes and adding them to sample names
    # until user stops loop.
    while True:
        # ask for group of suffixes
        input_suffix_group = input(f"{color.BOLD + color.DARKCYAN}"
            f"\nEnter a group of suffixes: {color.END}")

        # split input into list of words
        input_suffixes = input_suffix_group.split()

        # reinitiate list so it is empty
        names_list_new = []

        # loop through all names and add each suffix
        for name in names_list_old:
            for suffix in input_suffixes:
                names_list_new.append(name + "-" + suffix)

        # replace old with new list
        names_list_old = names_list_new

        # ask user whether to run through another interation of the
        # suffix loop
        input_suffix_continue = input(f"\n{color.BOLD + color.DARKCYAN}"
            "Do you want to add another group of suffixes? "
            f"Type \"yes\" or \"no\" (default): {color.END}").casefold()

        # if user answers anything other than yes break out of loop,
        # otherwise repeat
        if input_suffix_continue != "yes":
            break
        else:
            continue

    # set path to which file with suffixed sample names will be written
    path_suffix = Path(path_output, "_suffix.txt")

    # remove old output file and ignore error if it does not exist
    try:
        path_suffix.unlink()
    except (FileNotFoundError):
        pass

    # write new sample names to new output file
    with open(path_suffix, "a+") as file_samples:
        for item in names_list_new:
            file_samples.write(f"{item}\n")

    # replace original list of names with suffixed names
    names_list = names_list_new

#######################################################################
# customization of output
#######################################################################

# ask user how many stickers they want to skip (default: 0)
input_skip = input(f"\n{color.BOLD + color.DARKCYAN}"
    f"How many stickers do you want to skip, e.g. because they were "
    f"already used before (default = 0): {color.END}").casefold()

# deal with empty or non-numeric answers
if not input_skip:
    input_skip = 0
else:
    input_skip = int(input_skip)

# prepend empty items to list of names for each sticker to skip
names_list = ([None] * input_skip) + names_list
names_number = len(names_list)

# give user choice whether to print date and in which format
print(f"""{color.BOLD + color.DARKCYAN}
Do you want to print a date to the second sticker row?
    - For today's date in yyyy-mm-dd format (default),
      leave empty or enter \"today\"
    - Type \"none\" to not print anything to the date field
    - Any other input will be printed verbatim as the date,
      e.g. \"2023\""""
)
input_date = input(f"Your choice: {color.END}").casefold()

# set latex_date variable depending on user's date choice
match input_date:
    case "today" | "" | "none":
        latex_date = "\\newcommand{\\DATE}{\\today}"
    case "none":
        latex_date = "\\newcommand{\\DATE}{}"
    case _:
        latex_date = "\\newcommand{\\DATE}{"f"{input_date}""}"


#######################################################################
# typeset LaTeX file
#######################################################################

# set paths to typesetting and output files
dir_avery = PurePath(__file__).parent
path_preamble = Path(dir_avery, "resources", "preamble.tex")
path_before_body = Path(dir_avery, "resources", "before_body.tex")
path_latex = path_output.with_suffix(".tex")

# remove old output file if one already exist
try:
    path_latex.unlink()
except (FileNotFoundError):
    pass

# calculate number of pages necessary to fit all stickers
# (including skipped ones)
latex_pages = (names_number // 189) + 1

# create .tex file and write to it
with open(path_latex, "a+") as file_output:
    # write contents of preamble file to output file
    with open(path_preamble, "r") as file_preamble:
        for line in file_preamble:
            file_output.write(line)

    # write date macro to output file
    file_output.write(latex_date)

    # write contents of before_header file to output file
    with open(path_before_body, "r") as file_before_body:
        for line in file_before_body:
            file_output.write(line)

    # variable to track the current position in the list of names
    n = 0

    # loop through pages of final sticker layout
    for page_number in range(latex_pages):
        # start each page with the opening of the table environment
        file_output.write(f"% Page {page_number+1}\n"
            "\\begin{tabularx}{\\linewidth}{@{}*{7}{Y}@{}}\n")

        # loop through all rows
        for line_number in range(27):
            # add tab character at beginning of line
            file_output.write("\t")
            # loop through columns
            for position in range(7):
                # print unprinted sample names
                if (position < 6):
                    file_output.write(f"{return_sticker(n)} & ")
                elif (position == 6):
                    file_output.write(f"{return_sticker(n)}")
                else:
                    break
                n += 1
            file_output.write(" \\\\")  # end line after 7 stickers
            # add whitespace after lines
            if (line_number == 26):
                file_output.write(" \\addlinespace[0.05cm]\n")
            else:
                file_output.write(" \\addlinespace[0.470878cm]\n")
            # if all names were printed, break loop
            if (n >= names_number):
                break
        # close table environment at the end of the page
        file_output.write("\\end{tabularx}\n\n")
    # reenable command line output and end document
    file_output.write("\\scrollmode\n\\end{document}")

# call pdflatex to typeset .tex file
subprocess.run(["pdflatex", path_latex], stdout=subprocess.DEVNULL)

# open resulting pdf file in an OS-dependent manner
if system() == 'Darwin':
    subprocess.run(["open", path_latex.with_suffix(".pdf")])
elif system() == 'Windows':
    os.startfile(path_latex.with_suffix(".pdf"))
else:
    subprocess.run(["xdg-open", path_latex.with_suffix(".pdf")])
