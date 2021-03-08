""" Version 2.1 dated March 3rd 2021 by Gleb Ebert

    This script reads sample names from a list, presents the user with
    a couple of options to modify the names and arranges them on a
    sheet of A4 paper so that it can be printed on Avery-Zweckform
    L7871 labels
"""

from pathlib import Path # we use this for file path operations
import subprocess # this is for passing commands to unix shell

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
        f"{color.END}").casefold()

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
        input_file_again = input(f"{color.BOLD + color.DARKCYAN}"
            "Do you want to type the file name again? "
            f"Type \"yes\" or \"no\": \n{color.END}").casefold()

        # if user wants to try again, restart loop
        # otherwise exit script
        if input_file_again == "yes":
            continue
        else:
            quit()
    else:
        break

# open file in read mode
with open(input_file, "r") as file_handle:
    # convert file contents into a list
    names_list_original = file_handle.read().splitlines()

names_number = len(names_list_original) # get number of names

# print some of the sample names
print(f"\n{color.BOLD + color.DARKCYAN}"
    f"Your file contains {names_number} names:\n{names_list_original[0]}, "
    f"{names_list_original[1]} ... {names_list_original[-1]}{color.END}")

# ask user whether he wants to type the file name again
input_file_ok = input(f"{color.BOLD + color.DARKCYAN}Do you want to continue "
    f"with these names? Type \"yes\" or \"no\": {color.END}").casefold()

# exit script if user says no, otherwise continue
if input_file_ok == "no":
    quit()

# query user on output file name
output_file_name = input(f"\n{color.BOLD + color.DARKCYAN}Type the name of "
    f"your output file without suffix: {color.END}").casefold()

# check if user input includes ".txt" suffix and add it if not
if not output_file_name.endswith(".txt"):
    output_file_name += ".txt"

# set output file path
output_file_path = Path(str(Path().absolute()) + "/" + output_file_name)

#######################################################################
# The following section deals with name suffixes
#######################################################################

# give user choice whether to add suffixes
input_suffix_if = input(f"\n{color.BOLD + color.DARKCYAN}"
    "Do you want to add suffixes to your sample names? "
    f"Type \"yes\" or \"no\": {color.END}").casefold()

if input_suffix_if == "yes":
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
    names_list_old = names_list_original

    # Keep asking for suffixes and adding them to sample names
    # until user stops loop.
    while True:
        # ask for group of suffixes
        input_suffix_group = input(f"{color.BOLD + color.DARKCYAN}"
            f"\nEnter a group of suffixes: {color.END}").casefold()

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
        output_file_path.unlink()
    except (FileNotFoundError):
        pass

    # Create output file in append mode, loop through latest list with
    # modified names and write each one to a new line in the file.
    with open(output_file_path, "a+") as sampleFile:
        for item in names_list_new:
            sampleFile.write(f"{item}\n")
else:
    names_list_new = names_list_original

#######################################################################
# logic and parameters for LaTeX typesetting
#######################################################################

# give user choice whether to print month and year
input_date_if = input(f"\n{color.BOLD + color.DARKCYAN}"
    "Do you want to print the current month and year on the stickers? "
    f"Type \"yes\" or \"no\":  {color.END}").casefold()

# give user choice whether to print month and year
input_date_format = input(f"\n{color.BOLD + color.DARKCYAN}"
    "Do you want the date to include the day in addition to month and year?"
    f" Type \"yes\" or \"no\":  {color.END}").casefold()

if input_date_format == "yes":
    latex_date = "\t\t\\DTMtwodigits{##3}-\\DTMtwodigits{##2}-##1"
else:
    latex_date = "\t\t\\DTMtwodigits{##2}-##1"

# function that returns sticker content
def return_sticker(x):
    sticker = names_list_new[x]
    if len(sticker) >= 16: # if sticker too long, reduce font size
        sticker = "{\\ssmall " + sticker + "}"
    if input_date_if == "yes": # add date if specified
        # if sticker is short, put date on new line by ending the paragraph
        if (len(sticker) < 10 and input_date_format == "yes"):
            sticker = sticker + "\\par\\DATE"
        elif (len(sticker) < 13 and input_date_if == "yes"):
            sticker = sticker + "\\par\\DATE"
        else:
            sticker = sticker + " \\DATE"
    else: # add newline to preserve table formatting if no date is added
        sticker = sticker + "\\par"
    # escape underscores last to not interfere with name length
    sticker = sticker.replace("_", "\_")
    return sticker

# set output file to .tex
latex_file_path = output_file_path.with_suffix(".tex")

# remove old output file and ignore error if file does not exist
try:
    latex_file_path.unlink()
except (FileNotFoundError):
    pass

# Round number of pages needed to fit all stickers up to nearest
# whole page.
names_number_new = len(names_list_new)
latex_pages = (names_number_new // 189) + 1

#######################################################################
# typeset LaTeX file
#######################################################################

# save latex document preamble in variable
latex_preamble = \
"""\\batchmode % disable command line output
\\documentclass[a4paper]{article} % document definition
% used to adjust page margins to 3.5mm
\\usepackage[top=1.2cm, bottom=1.2cm, left=0.5cm, right=0.5cm]{geometry}
% used for table with columns of a defined width
\\usepackage{tabularx}
% used to add white space after column rows
\\usepackage{booktabs}
% to format date
\\usepackage{datetime2}
% for more font sizes
\\usepackage{moresize}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\pagestyle{empty} % no page numbers
\\setlength{\\parindent}{0pt} % set paragraph indent to zero

% define new date style
\\DTMnewdatestyle{mydate}{%
    \\renewcommand{\\DTMdisplaydate}[4]{%
"""\
f"{latex_date}"\
"""
    }%
    \\renewcommand{\\DTMDisplaydate}{\\DTMdisplaydate}%
}
\\DTMsetdatestyle{mydate} % set new datestyle as default
\\newcommand{\\DATE}{\\today} % create alias for current date command

% defines custom column type for table
\\newcolumntype{Y}{>{\\centering\\arraybackslash}X}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{document}

% scriptsize/ssmall, bold and sans-serif font throughout the entire document
\\scriptsize \\bfseries \\sffamily
% table definition: spans the entire page in (text)width
% @{} removes white space before first and after last row
% *{7}{Y} defines seven columns of equal width with text centering
% sample name and date rows alternate with different amounts of spacing\n\n"""

# create .tex file and write to it
with open(latex_file_path, "a+") as latex_file:
    latex_file.write(latex_preamble) # write preamble once
    
    # variable to track the current position in the list of names
    n = 0
    
    # loop through pages of final sticker layout
    for page_number in range(latex_pages):
        # start each page with the opening of the table environment
        latex_file.write(f"% Page {page_number+1}\n"
            "\\begin{tabularx}{\linewidth}{@{}*{7}{Y}@{}}\n")
        
        # loop through each line of and write sticker contents to it
        for line_number in range(27):
            # add tab character at beginning of line
            latex_file.write("\t")
            # 
            for l in range (7):
                # if names to be printed still left, do so
                if (n < (names_number_new-1) and l < 6):
                    latex_file.write(f"{return_sticker(n)} & ")
                elif (n == (names_number_new-1) or l == 6):
                    latex_file.write(f"{return_sticker(n)}")
                else:
                    break
                n += 1
            # end line after 7 stickers
            latex_file.write(" \\\\")
            # if line is the last one of the page
            if (line_number == 26):
                latex_file.write(" \\addlinespace[0.05cm]\n")
            # if next line is not the last line of the page
            else:
                latex_file.write(" \\addlinespace[0.470878cm]\n")
            # if all names were printed, break loop
            if (n == names_number_new):
                break
        # close table environment at the end of the page
        latex_file.write("\\end{tabularx}\n\n")
    # reenable command line output and end document
    latex_file.write("\\scrollmode\n\\end{document}")

# call pdflatex to typeset .tex file # text = FALSE
subprocess.run(["pdflatex", latex_file_path], stdout=subprocess.DEVNULL)
# open resulting pdf file 
subprocess.run(["open", latex_file_path.with_suffix(".pdf")])