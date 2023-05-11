#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys


def open_file(path):
    """Open and return the file specified by path."""
    try:
        # Try to open the file for reading
        file = open(path, "r")
    except:
        # Exit the program with error message
        sys.exit("Error: can\'t find specified file - check file name is correct")
    else:
        return file


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    return input_file.read(1)


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:

        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading
        file_path = arguments[0]
        print(file_path)
        file = open_file(file_path)

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        file_length = len(file.read())
        file.seek(0, 0)
        for i in range(file_length):
            next_character = get_next_character(file)
            print(next_character, end='')

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces

        print("\nNow reading numbers...")
        # Print out all the numbers in the file

        print("\nNow reading names...")
        # Print out all the names in the file

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        # name = MyNames()
        # bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
        #                 name.lookup("Ghastly"), name.lookup("Awful")]


if __name__ == "__main__":
    main()
