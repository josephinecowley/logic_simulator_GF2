"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
import sys

class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line_number = None
        self.end_position = None

class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        # open the definition file using path
        self.file = self.open_file(path)

        # keep track of current location in file
        self.line_number = 1 # one-based indexing for error reporting
        self.position = 0
        
        # assign the instance of the names class to self.names
        self.names = names

        # initialises a list of symbol types
        self.symbol_type_list = [self.BRACKET_OPEN, self.BRACKET_CLOSE, self.BRACE_OPEN, self.BRACE_CLOSE, self.COMMA, self.FULLSTOP, 
            self.SEMICOLON, self.EQUALS, self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(12)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITORS", "END"]

        # populates name table with keywords and assigns keywork IDs
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITORS_ID,
            self.END_ID] = self.names.lookup(self.keywords_list)

        # hold the last character read from the definition file
        self.current_character = ""

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace or \n

        if self.current_character.isalpha():  # name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
                self.load_scanner_data(symbol)
            else:
                symbol.type = self.NAME
                self.load_scanner_data(symbol)
            symbol.id = self.names.lookup([name_string])[0] # lookup a symbol id

        elif self.current_character.isdigit():  # number
            number = self.get_number()
            symbol.type = self.NUMBER
            symbol.id = self.names.lookup([number])[0]
            self.load_scanner_data(symbol)

        elif self.current_character == "=":  # punctuation
            symbol.type = self.EQUALS
            self.load_scanner_data(symbol)
            self.advance()

        elif self.current_character == ",":
            symbol.type = self.COMMA
            self.load_scanner_data(symbol)
            self.advance()

        elif self.current_character == ".":
            symbol.type = self.FULLSTOP
            self.load_scanner_data(symbol)
            self.advance()
        
        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self.load_scanner_data(symbol)
            self.advance()

        elif self.current_character == "{":
            symbol.type = self.BRACE_OPEN
            self.load_scanner_data(symbol)
            self.advance()

        elif self.current_character == "}":
            symbol.type = self.BRACE_CLOSE
            self.load_scanner_data(symbol)
            self.advance()
        
        elif self.current_character == "(":
            symbol.type = self.BRACKET_OPEN
            self.load_scanner_data(symbol)
            self.advance()

        elif self.current_character == ")":
            symbol.type = self.BRACKET_CLOSE
            self.load_scanner_data(symbol)
            self.advance()

        elif self.current_character == "":  # end of file
            symbol.type = self.EOF
            self.load_scanner_data(symbol)

        else:  # not a valid character
            self.advance()

        return symbol

    def open_file(self, path):
        """Open and return the file specified by path."""
        try:
            # Try to open the file for reading
            file = open(path, "r")
        except:
            # raise a value error
            raise ValueError("Error: can\'t find specified file - check file name is correct")
        else:
            return file

    def load_scanner_data(self, symbol):
        """Update the location attributes of symbol using Scanner's current location attributes."""
        symbol.line_number = self.line_number
        symbol.end_position = self.position

    def advance(self):
        """Reads the next character in file and places it in current_character.
           Increments position in line for every call.
        """
        self.current_character = self.file.read(1)
        if self.current_character == "\n":
            self.line_number += 1
            self.position = 0
        else:
            self.position += 1

    def skip_spaces(self):
        """Calls advance() method until current character is not space or is '\n'. 
        If character is '\n', update line number and position"""
        while self.current_character.isspace():
            self.advance()
    
    def skip_comment(self):
        """Assumes current character is a # or " and """

    def get_name(self):
        """Assumes that current character is alphabetical and returns an alphanumeric name."""
        name = f"{self.current_character}" # put first character in string 
        self.advance() # get next character
        while self.current_character.isalnum(): # updating alnum chars to string
            name += self.current_character
            self.advance()
        return name

    def get_number(self):
        """Assumes that current character is a number and returns a string of integer number."""
        num = f"{self.current_character}" # put first digit in string
        self.advance() # get next character
        while self.current_character.isdigit(): # updating digits to string
            num += self.current_character
            self.advance()
        return num #returns the number as a string 

    def display_line_and_marker(self, symbol):
        """Takes a symbol instance and prints its line in the file. 
        If the 'name' is over length one, use tildes, otherwise use caret."""

        # find the whole line where that symbol appears
        for i, line in enumerate(self.file, start=1):
            if i == symbol.line_number:
                line_text = line
                break
        
        line_length = len(line_text)

        if symbol.type in [self.KEYWORD, self.NAME, self.NUMBER]:
            name = self.names.get_name_string(symbol.id)
            name_length = len(name)

            if name_length == 1:
                caret_position = symbol.end_position
                caret_string = " " * line_length
                caret_list = list(caret_string)
                caret_list[caret_position] = "^"

                print(line_text)
                print("".join(caret_list))
            
            else:
                start_position = symbol.end_position - name_length + 1
                tilde_string = " " * line_length
                tilde_list = list(tilde_string)
                tilde_list[start_position: start_position + name_length] = list("~" * name_length)

                print(line_text)
                print("".join(tilde_list))
        else:
                caret_position = symbol.end_position
                caret_string = " " * line_length
                caret_list = list(caret_string)
                caret_list[caret_position] = "^"

                print(line_text)
                print("".join(caret_list))            






