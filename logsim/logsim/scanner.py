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
        self.line_number = 0
        self.start_position = 0
        self.end_position = 0

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
        
        # assign the instance of the names class to self.names
        self.names = names

        # initialises a list of symbol types
        self.symbol_type_list = [self.BRACE_OPEN, self.BRACE_CLOSE, self.COMMA, self.SEMICOLON, self.EQUALS,
            self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(9)
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITORS", "END"]

        # populates name table with keywords and assigns keywork IDs
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITORS_ID,
            self.END_ID] = self.names.lookup(self.keywords_list)

        # hold the last character read from the definition file
        self.current_character = ""

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace

        if self.current_character.isalpha():  # name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string]) # lookup a symbol id

        elif self.current_character.isdigit():  # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER

        elif self.current_character == "=":  # punctuation
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ",":
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == "{":
            symbol.type = self.BRACE_OPEN
            self.advance()

        elif self.current_character == "}":
            symbol.type = self.BRACE_CLOSE
            self.advance()

        elif self.current_character == "\n": # new line symbol, update line number and position
            symbol.line_number += 1
            symbol.position = 0
            # skip all spaces after new line
            # will catch any subsequent new lines
            self.skip_spaces() 

        elif self.current_character == "":  # end of file
            symbol.type = self.EOF

        else:  # not a valid character
            self.advance()

        return symbol

    def open_file(self, path):
        """Open and return the file specified by path."""
        try:
            # Try to open the file for reading
            file = open(path, "r")
        except:
            # Exit the program with error message
            sys.exit("Error: can\'t find specified file - check file name is correct")
        else:
            return file
    
    '''def update_position(self, symbol):
        # update position in line
        symbol.start_position += 1
    '''
    def advance(self, symbol):
        """Reads the next character in file and places it in current_character.
           Increments position in line for every call.
        """
        self.current_character = self.file.read(1)
        # update position in line
        symbol.start_position += 1

    def skip_spaces(self):
        """Calls advance() method until current character is not space or is '\n'."""
        while self.current_character.isspace():
            if self.current_character == '\n':
                break
            else:
                self.advance()

    def get_name(self):
        """Assumes that current character is alphabetical and returns an alphanumeric name."""
        name = f"{self.current_character}" # put first character in string 
        self.advance() # get next character
        while self.current_character.isalnum(): # updating alnum chars to string
            name += self.current_character
            self.advance()
        return name

    def get_number(self):
        """Assumes that current character is a number"""
        num = f"{self.current_character}" # put first digit in string
        self.advance() # get next character
        while self.current_character.isdigit(): # updating digits to string
            num += self.current_character
            self.advance()
        return int(num)

    def display_line_and_marker(self, symbol):
        """Takes a symbol instance and prints its line in file and a caret underneath"""
        # find the whole line where that symbol appears
        for i, line in enumerate(self.file, start=1):
            if i == symbol.line_number:
                line_text = line
                break

        line_length = len(line_text)
        caret_position = symbol.position

        caret_string = " " * line_length
        caret_list = list(caret_string)
        caret_list[caret_position] = "^"

        print(line_text)
        print( "".join(caret_list))

