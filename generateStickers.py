""" Version 2.2 dated April 15th 2021 by Gleb Ebert

    This script reads sample names from a list, presents the user with
    a couple of options to modify the names and arranges them on a
    sheet of A4 paper so that it can be printed on Avery-Zweckform
    L7871 labels
"""

from pathlib import Path, PurePath # file path operations
import re # regular expressions
import subprocess # passing commands to unix shell

# create class with objects to format console output
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
# This section deals with the initial input of sample names.
#######################################################################

# keep asking for file names until file exists or user aborts script
while True:
    # get input file name from user and store its name in variable
    input_file = input(f"{color.BOLD + color.DARKCYAN}"
        "Enter the name of the txt file containing your strain/isolate names "
        f"(one per line) followed by [ENTER] to confirm: "
        f"{color.END}")

    # check if user input includes ".txt" suffix and add it if absent
    if not input_file.endswith(".txt"):
        input_file += ".txt"

    # if file does not exist, print error message and exit script
    if not Path(input_file).exists():
        print(f"\n{color.BOLD + color.RED}File {input_file} not found. "
              "Make sure file is present in your working directory:\n"
              f"{Path().cwd()}\n"
              "To change your working directory type "
              f"'cd /Path/to/your/directory' then hit [ENTER]{color.END}")

        # ask user whether he wants to type the file name again
        retry = input(f"{color.BOLD + color.DARKCYAN}"
            "Do you want to type the file name again? "
            f"Type \"yes\" or \"no\": \n{color.END}").casefold()

        # if user wants to try again, restart loop
        # otherwise exit script
        if retry == "yes":
            continue
        else:
            quit()
    else:
        break

# open file in read mode, read lines, filter out empty ones and convert to list
with open(input_file, "r", encoding='unicode_escape') as file:
    names_list = list(filter(None, (line.rstrip() for line in file)))

names_number = len(names_list) # get number of names

# print some of the sample names
print(f"\n{color.BOLD + color.DARKCYAN}"
    f"Your file contains {names_number} names:\n"
    f"{names_list[0]}, {names_list[1]} ... "
    f"{names_list[-1]}{color.END}")

# ask user whether they want to continue with the sample names
input_continue = input(f"{color.BOLD + color.DARKCYAN}Do you want to continue "
    f"with these names? Type \"yes\" or \"no\": {color.END}").casefold()

# exit script if user says no, otherwise continue
if input_continue == "no":
    quit()

# query user on output file name
name_output = input(f"\n{color.BOLD + color.DARKCYAN}Type the name of "
    f"your output file without suffix: {color.END}")

# check if user input includes ".txt" suffix and add it if not
if not name_output.casefold().endswith(".txt"):
    name_output += ".txt"

# set output file path
path_output = Path(str(Path().absolute()) + "/" + name_output)

#######################################################################
# The following section deals with name suffixes
#######################################################################

# give user choice whether to add suffixes
input_suffix = input(f"\n{color.BOLD + color.DARKCYAN}"
    "Do you want to add suffixes to your sample names? "
    f"Type \"yes\" or \"no\": {color.END}").casefold()

if input_suffix == "yes":
    # print explanation of inner workings once before continuing
    print(f"\n{color.BOLD + color.DARKCYAN}"
        "==========================================")
    print("\nIn the following part of the script you will supply groups of "
        "suffixes (e.g. treatment names or replicate numbers) separated by "
        "spaces: \"CTRL TREAT1 TREAT2 TREAT3\". Each suffix will be combined "
        "with each sample name (e.g. Strain1-TREAT1, Strain1-TREAT2 ... "
        "Strain10-TREAT3). You will also have to opportunity to supply "
        "multiple suffix groups one after the other (the result of this would "
        "be something like Strain1-TREAT1-Replicate1, "
        "Strain1-TREAT1-Replicate2 ...).{color.END}")

    # initiate list with names to be modified
    names_list_old = names_list

    # Keep asking for suffixes and adding them to sample names
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
            f"Type \"yes\" or \"no\": {color.END}").casefold()

        # if user answers anything other than yes break out of loop,
        # otherwise repeat
        if input_suffix_continue != "yes":
            break
        else:
            continue

    # remove old output file and ignore error if it does not exist
    try:
        path_output.unlink()
    except (FileNotFoundError):
        pass

    # Create output file in append mode, loop through latest list with
    # modified names and write each one to a new line in the file.
    with open(path_output, "a+") as file_samples:
        for item in names_list_new:
            file_samples.write(f"{item}\n")

    # replace old list of names with new one
    names_list = names_list_new

#######################################################################
# logic and parameters for LaTeX typesetting
#######################################################################

# ask user how many stickers they want to skip (default: 0)
input_skip = input(f"\n{color.BOLD + color.DARKCYAN}"
    f"How many stickers do you want to skip, e.g. because they were already"
    f" used before (default: 0): {color.END}").casefold()

# deal with empty or non-numeric answers
if input_skip == "":
    input_skip = 0
else:
    input_skip = int(input_skip)

# prepend empty items to list of names for each sticker to skip
names_list = ([None] * input_skip) + names_list

# set variable for date as empty
latex_date = ""

# give user choice whether to print month and year
input_date = input(f"\n{color.BOLD + color.DARKCYAN}"
    "Do you want to print the current month and year on the stickers? "
    f"Type \"yes\" or \"no\": {color.END}").casefold()

if input_date == "yes":
    # give user choice whether to print month and year
    input_date_format = input(f"\n{color.BOLD + color.DARKCYAN}"
        "Do you want the date to include the day in addition to month and year?"
        f" Type \"yes\" or \"no\": {color.END}").casefold()

    # redefine date format to be in the yyyy-mm format
    if input_date_format != "yes":
        latex_date = \
            """% define new date style
            \\DTMnewdatestyle{mydate}{
                \\renewcommand{\\DTMdisplaydate}[4]{##1-\\DTMtwodigits{##2}}
                \\renewcommand{\\DTMDisplaydate}{\\DTMdisplaydate}
            }
            \\DTMsetdatestyle{mydate} % set new datestyle as default
             """

# function that returns sticker content
def return_sticker(x):
    # return empty sticker
    if (x >= len(names_list) or names_list[x] is None):
        sticker = "\\phantom{empty sticker}\\par"
    else:
        sticker = names_list[x]
        if len(sticker) > 20: # if text is very long, reduce font size
            sticker = "{\\tiny " + sticker + "}"
        elif len(sticker) > 15: # if text is long, reduce font size less
            sticker = "{\\ssmall " + sticker + "}"
        if input_date == "yes": # add date if specified
            # if sticker is short, put date on new line by ending the paragraph
            if (len(sticker) < 10 and input_date_format == "yes"):
                sticker = sticker + "\\par\\DATE"
            elif (len(sticker) < 13 and input_date == "yes"):
                sticker = sticker + "\\par\\DATE"
            else:
                sticker = sticker + " \\DATE"
        else: # add newline to preserve table formatting w/o date
            sticker = sticker + "\\par"
        # escape underscores last to not interfere with name length
        sticker = sticker.replace("_", "\\_")

    return sticker

# set output file to .tex
path_latex = path_output.with_suffix(".tex")

# remove old output file and ignore error if file does not exist
try:
    path_latex.unlink()
except (FileNotFoundError):
    pass

# Round number of pages needed to fit all stickers up to nearest
# whole page.
names_number = len(names_list)
latex_pages = (names_number // 189) + 1

#######################################################################
# typeset LaTeX file
#######################################################################

# set paths to files
dir_avery = PurePath(__file__).parent
path_preamble = Path(dir_avery, "resources", "preamble.tex")
path_before_body = Path(dir_avery, "resources", "before_body.tex")

# create .tex file and write to it
with open(path_latex, "a+") as file_output:
    # write contents of preamble file to output file
    with open(path_preamble, "r") as file_preamble:
        for line in file_preamble:
            file_output.write(line)

    # write date redefinition command to output file
    # this might be an empty string if the date does not need to be redefined
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

        # loop through each line of and write sticker contents to it
        for line_number in range(27):
            # add tab character at beginning of line
            file_output.write("\t")
            #
            for position in range(7):
                # if unprinted sample names left, do so
                if (position < 6):
                    file_output.write(f"{return_sticker(n)} & ")
                elif (position == 6):
                    file_output.write(f"{return_sticker(n)}")
                else:
                    break
                n += 1
            # end line after 7 stickers
            file_output.write(" \\\\")
            # if line is the last one of the page
            if (line_number == 26):
                file_output.write(" \\addlinespace[0.05cm]\n")
            # if next line is not the last line of the page
            else:
                file_output.write(" \\addlinespace[0.470878cm]\n")
            # if all names were printed, break loop
            if (n >= names_number):
                break
        # close table environment at the end of the page
        file_output.write("\\end{tabularx}\n\n")
    # reenable command line output and end document
    file_output.write("\\scrollmode\n\\end{document}")

# call pdflatex to typeset .tex file # text = FALSE
subprocess.run(["pdflatex", path_latex], stdout=subprocess.DEVNULL)
# open resulting pdf file
subprocess.run(["open", path_latex.with_suffix(".pdf")])
