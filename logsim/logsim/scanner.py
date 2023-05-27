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
        self.start_position = None

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
        self.path = path

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
        self.current_character = " " # initialised with a space so that advance() is called on the first call to get_symbol

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace 

        if self.current_character.isalpha():  # name
            self.load_scanner_data(symbol) #load the scanner location attributes to symbol
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
                 
            else:
                symbol.type = self.NAME
            symbol.id = self.names.lookup([name_string])[0] # lookup a symbol id

        elif self.current_character.isdigit():  # number
            self.load_scanner_data(symbol)
            number = self.get_number()
            symbol.type = self.NUMBER
            symbol.id = self.names.lookup([number])[0]
            

        elif self.current_character == "=":  # punctuation...
            self.load_scanner_data(symbol)
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ",":
            self.load_scanner_data(symbol)
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ".":
            self.load_scanner_data(symbol)
            symbol.type = self.FULLSTOP
            self.advance()
        
        elif self.current_character == ";":
            self.load_scanner_data(symbol)            
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == "{":
            self.load_scanner_data(symbol)
            symbol.type = self.BRACE_OPEN
            self.advance()

        elif self.current_character == "}":
            self.load_scanner_data(symbol)
            symbol.type = self.BRACE_CLOSE
            self.advance()
        
        elif self.current_character == "(":
            self.load_scanner_data(symbol)
            symbol.type = self.BRACKET_OPEN
            self.advance()

        elif self.current_character == ")":
            self.load_scanner_data(symbol)
            symbol.type = self.BRACKET_CLOSE
            self.advance()
        
        elif self.current_character in ['#', '"']: # comment openers
            self.skip_comment()
            self.get_symbol()

        elif self.current_character == "":  # end of file
            self.load_scanner_data(symbol)
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
            # raise a value error
            raise ValueError("Error: can\'t find specified file - check file name is correct")
        else:
            return file

    def load_scanner_data(self, symbol):
        """Update the location attributes of symbol using Scanner's current location attributes."""
        symbol.line_number = self.line_number
        symbol.start_position = self.position

    def advance(self):
        """Reads the next character in file and places it in current_character.
           Increments position in line for every call.
        """
        self.current_character = self.file.read(1)
        self.position += 1
        

    def skip_spaces(self):
        """Calls advance() method until current character is not space. 
        If current_character is a space, returns next non-whitespace character.
        If current_character is not a space, returns current character."""
        while self.current_character.isspace():
            if self.current_character == "\n":
                self.line_number += 1
                self.position = 0
            self.advance()
    
    def skip_comment(self):
        """Assumes current character is a # or " and advances until comments are closed. 
        Then skip spaces such than current_character is non_whitespace"""
        if self.current_character == "#":
            self.advance() # get first character in comment
            while not self.current_character == "\n": # closed by new line
                self.advance() 
            self.skip_spaces() # current_character now non-whitespace, line_number and position updated
        else:
            self.advance() # get first character in comment
            while not self.current_character == '"': # closed by " (have to break PEP8 for this)
                if self.current_character == "\n":
                    self.line_number += 1
                    self.position = 0
                self.advance()
            self.advance()
            self.skip_spaces()

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
        """Uses a temp_file instance to avoid interference with scanner's pointer. 
        Takes a symbol instance and prints its line in the file. 
        If the 'name' is over length one, use tildes, otherwise use caret.
        Printed lines will have a standard indent of eight spaces."""

        temp_file = self.open_file(self.path)
        # find the whole line where that symbol appears
        for i, line in enumerate(temp_file, start=1):
            if i == symbol.line_number:
                line_text = line
                break
        temp_file.close()

        line_length = len(line_text)

        for i, char in enumerate(line_text):
            if not char.isspace():
                start_of_text_index = i
                break
            
        if symbol.type in [self.KEYWORD, self.NAME, self.NUMBER]:
            name = self.names.get_name_string(symbol.id)
            name_length = len(name)

            if name_length == 1:
                caret_position = symbol.start_position - 1
                empty_caret_string = " " * line_length
                caret_list = list(empty_caret_string)
                caret_list.pop()
                caret_list[caret_position] = "^"
                filled_marker_string = "".join(caret_list)


            else:
                start_position = symbol.start_position
                empty_tilde_string = " " * line_length
                tilde_list = list(empty_tilde_string)
                tilde_list[start_position - 1: start_position + name_length] = list("~" * name_length)
                filled_marker_string = "".join(tilde_list)
            
        else:
                caret_position = symbol.start_position - 1
                empty_caret_string = " " * line_length
                caret_list = list(empty_caret_string)
                caret_list.pop()
                caret_list[caret_position] = "^"
                filled_marker_string = "".join(caret_list)


        # standardise line indent
        line_text = " "*8 + line_text.lstrip()
        filled_marker_string = " "*8 + filled_marker_string[start_of_text_index:]

        if symbol.type == self.EOF: # handle case of error in END keyword
            print(line_text)
            print(filled_marker_string, end="\n\n")

        else:
            print(line_text, end="")
            print(filled_marker_string, end="\n\n")
        
            

